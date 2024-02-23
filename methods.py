from fastapi import APIRouter, HTTPException
from data_manager import *
from config import FILE_PATH
from models import *
from typing import Dict
import re
import yfinance as yf

yf.pdr_override()
from datetime import datetime, timedelta


def get_item_dict():
    """
    Crée et retourne un dictionnaire d'entrées boursières à partir d'un fichier CSV.
    Chaque ligne du CSV est convertie en une entrée de stock (StockEntry), avec des vérifications
    sur la validité du type d'opération et du symbole ISIN.

    Raises:
        HTTPException: Levée si le type d'opération ou le symbole ISIN est invalide.

    Returns:
        Dict[int, StockEntry]: Dictionnaire où chaque clé est un index de ligne et chaque valeur est un StockEntry.
    """
    df = read_csv(FILE_PATH)
    item_dict: Dict[int, StockEntry] = {}
    for index, row in df.iterrows():
        # Vérifier et traiter le type d'opération
        operation_type = test_operation_type(str(row['operation_type']))
        if not operation_type:
            raise HTTPException(status_code=400,
                                detail=f"operation_type invalide dans la base de données ligne {index + 1}")

        # Vérifier la validité du symbole ISIN
        isin = str(row['isin'])
        if not is_valid_yfinance_ticker(isin):
            raise HTTPException(status_code=400, detail=f"ISIN invalide dans la base de données ligne {index + 1}")
        else:
            # Créer l'entrée de stock et l'ajouter au dictionnaire
            item = StockEntry(index=index,
                              date=row['date'],
                              isin=isin,
                              company_name=row['company_name'],
                              quantity=row['quantity'],
                              unit_price=row['unit_price'],
                              operation_type=str(row['operation_type']).lower())
            item_dict[index] = item
    return item_dict


def get_unit_price(date, isin):
    """
    Récupère le dernier prix de clôture d'un titre boursier pour une date donnée.
    Si la date spécifiée n'est pas un jour ouvré, un historique de 5 jours est utilisé pour trouver le dernier prix disponible.

    Args:
        date (str): Date pour laquelle récupérer le prix.
        isin (str): Symbole ISIN du titre boursier.

    Returns:
        Dict[str, float]: Un dictionnaire contenant la date du dernier prix de clôture et le prix lui-même.
    """
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    jcinq = date_obj - timedelta(days=5)
    historical_data = yf.download(isin, start=jcinq, end=date_obj)

    last_close_price = historical_data['Close'].iloc[-1]
    last_close_date = historical_data.index[-1].strftime('%Y-%m-%d')
    return {"date": last_close_date, "price": last_close_price}


def test_operation_type(input_string):
    """
    Teste si une chaîne de caractères donnée correspond à un type d'opération valide.

    Args:
        input_string (str): La chaîne de caractères à tester.

    Returns:
        str or bool: Retourne la chaîne en minuscule si valide, sinon False.
    """
    input_string = input_string.lower()  # Conversion en minuscule
    for operation_type in OperationType:
        if input_string == operation_type.value:
            return input_string
    return False


def is_valid_yfinance_ticker(string_variable):
    """
    Vérifie si une chaîne de caractères est un symbole boursier valide pour Yahoo Finance.

    Args:
        string_variable (str): Le symbole boursier à vérifier.

    Returns:
        bool: True si le symbole est valide, sinon False.
    """
    pattern = r'^[A-Z0-9\-.]+$'  # Pattern de regex pour symbole boursier
    return bool(re.match(pattern, string_variable))


def calculate_portfolio_gains(items_net_positions):
    """
    Calcule les gains réalisés et latents pour un portefeuille d'actions.

    Args:
        items_net_positions (Dict[str, NetPosition]): Un dictionnaire de positions nettes dans le portefeuille.

    Returns:
        Tuple[Dict[str, float], Dict[str, float]]: Deux dictionnaires contenant les gains réalisés et latents.
        Le premier dictionnaire mappe l'ISIN à ses gains réalisés, tandis que le second mappe l'ISIN à ses gains latents.
    """
    df = pd.read_csv(FILE_PATH)

    # Conversion de la date au format standard et filtrage des lignes invalides
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date', 'isin', 'operation_type'])

    # Calcul du total_price si manquant
    df['total_price'] = df['total_price'].fillna(df['quantity'] * df['unit_price'])

    # Identification des différentes opérations (achats et ventes)
    buy_ops = ['buy', 'buy to Cover']
    sell_ops = ['sell', 'short sell']

    # Séparation des achats et des ventes
    buys = df[df['operation_type'].isin(buy_ops)]
    sells = df[df['operation_type'].isin(sell_ops)]

    # Remplacement des NaN par zéro pour les calculs
    buy_costs = buys.groupby('isin')['total_price'].sum().fillna(0)
    sell_revenues = sells.groupby('isin')['total_price'].sum().fillna(0)

    # Calcul des gains réalisés
    raw_gains = sell_revenues - buy_costs
    gains = {isin: round(value, 2) for isin, value in raw_gains.items() if pd.notna(value) and value != 0}

    # Calcul des gains latents
    latent_gains = {}
    for id, net_position in items_net_positions.items():
        isin = net_position.isin
        quantity_in_portfolio = net_position.quantity_in_portfolio
        current_price = net_position.current_price

        # Calcul du prix moyen d'achat
        average_buy_price = 0
        if isin in buys['isin'].values:
            average_buy_price = buys[buys['isin'] == isin]['total_price'].sum() / buys[buys['isin'] == isin][
                'quantity'].sum()

        # Calcul de la plus ou moins-value latente
        latent_gain = quantity_in_portfolio * (current_price - average_buy_price)
        latent_gains[isin] = round(latent_gain, 2)  # Arrondi à deux décimales

    return gains, latent_gains
