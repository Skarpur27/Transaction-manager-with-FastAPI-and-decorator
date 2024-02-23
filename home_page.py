import main
from models import *
#from main import *
from data_manager import *
from datetime import datetime, timedelta
import pandas as pd

def get_net_position(item_dict):
    """
    Calcule la position nette pour chaque ISIN en tenant compte des achats et des ventes.

    Args:
        item_dict (dict): Un dictionnaire contenant des objets représentant des opérations boursières.
                          Chaque clé est un identifiant unique et chaque valeur est un objet avec des attributs tels que
                          ISIN, quantité et type d'opération.

    Returns:
        dict: Un dictionnaire de positions nettes, où chaque clé est un identifiant unique et chaque valeur
              est un objet NetPosition représentant la position nette pour un ISIN donné.
    """
    totals = {}
    # Parcours des éléments dans item_dict
    for key, data in item_dict.items():
        isin = data.isin
        quantity = data.quantity  # Accès à l'attribut 'quantity'
        operation_type = data.operation_type

        # Calcul de la quantité nette par ISIN
        if isin in totals:
            # Soustraction de la quantité pour les opérations de vente
            if operation_type.value in ['sell', 'short sell']:
                totals[isin] -= quantity
            else:
                # Ajout de la quantité pour les opérations d'achat
                totals[isin] += quantity
        else:
            # Initialisation de la quantité pour un nouvel ISIN
            if operation_type.value in ['sell', 'short sell']:
                totals[isin] = -quantity
            else:
                totals[isin] = quantity

    # Conversion du dictionnaire totals en DataFrame pour un traitement plus aisé
    grouped = pd.DataFrame(list(totals.items()), columns=['isin', 'total_quantity'])

    net_positions_dict = {}
    # Parcours du DataFrame pour créer des objets NetPosition
    for index, row in grouped.iterrows():
        # Obtention des données historiques pour l'ISIN
        data = YahooFinanceDataLoader.get_historic_returns(row['isin'])
        # Création de l'objet NetPosition avec les informations calculées et obtenues
        net_positions = NetPosition(id=index,
                                    isin=row['isin'],
                                    quantity_in_portfolio=row['total_quantity'],
                                    current_price=data.current_price,
                                    net_position=row['total_quantity'] * data.current_price,
                                    price_history=data.returns_history.to_dict())
        # Ajout de l'objet NetPosition au dictionnaire
        net_positions_dict[index] = net_positions

    return net_positions_dict
