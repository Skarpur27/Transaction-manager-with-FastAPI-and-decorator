from dataclasses import dataclass
import pandas as pd
import yfinance as yf
from utils import cache
from fastapi import HTTPException
import pandas as pd
from fastapi import HTTPException


yf.pdr_override()


@dataclass
class YahooFinanceData:
    """
    Classe représentant les données financières récupérées pour un actif spécifique.

    Attributes:
        ticker (str): Le symbole boursier de l'actif.
        returns_history (pd.DataFrame): Historique des retours de l'actif.
        asset_name (str): Nom de l'actif.
        current_price (float): Prix actuel de l'actif.
    """
    ticker: str
    returns_history: pd.DataFrame
    asset_name: str
    current_price: float

    @staticmethod
    def from_data_loader(ticker: str, history: pd.DataFrame, name_asset: str, curr_price: float):
        """
        Crée une instance de YahooFinanceData à partir des données chargées.

        Args:
            ticker (str): Symbole boursier de l'actif.
            history (pd.DataFrame): Historique des retours de l'actif.
            name_asset (str): Nom de l'actif.
            curr_price (float): Prix actuel de l'actif.

        Returns:
            YahooFinanceData: Une instance de YahooFinanceData.
        """
        return YahooFinanceData(
            ticker=ticker,
            returns_history=history,
            asset_name=name_asset,
            current_price=curr_price
        )


class YahooFinanceDataLoader:
    """
    Classe pour charger les données financières à partir de Yahoo Finance.
    """

    @staticmethod
    def get_historic_returns(ticker_symbol, start_date=None, end_date=None):
        """
        Récupère l'historique des retours d'un actif financier entre deux dates.

        Args:
            ticker_symbol (str): Symbole boursier de l'actif.
            start_date (datetime, optional): Date de début de l'historique. Defaults à None.
            end_date (datetime, optional): Date de fin de l'historique. Defaults à None.

        Returns:
            YahooFinanceData: Les données financières historiques de l'actif.

        """

        # Télécharger les données si elles ne sont pas dans le cache
        returns_history = YahooFinanceDataLoader.compute_total_return(ticker_symbol, start_date, end_date)
        asset = yf.Ticker(ticker_symbol)
        name_asset = asset.info['shortName']
        curr_price = asset.history(period="1d")["Close"].iloc[0]

        return YahooFinanceData.from_data_loader(ticker_symbol, returns_history, name_asset, curr_price)

    @staticmethod
    def compute_total_return(ticker, start_date=None, end_date=None):
        """
        Calcule le retour total pour un actif financier sur une période donnée.

        Args:
            ticker (str): Symbole boursier de l'actif.
            start_date (datetime): Date de début de la période.
            end_date (datetime): Date de fin de la période.

        Returns:
            pd.DataFrame: DataFrame contenant le retour total de l'actif sur la période.
        """
        df = yf.download(ticker, start=start_date, end=end_date)
        return df['Adj Close']




def read_csv(file_path):
    """
    Lit un fichier CSV à partir du chemin spécifié.

    Args:
        file_path (str): Chemin vers le fichier CSV à lire.

    Returns:
        DataFrame: Un DataFrame contenant les données du fichier CSV.

    Raises:
        HTTPException: Si le fichier CSV n'est pas trouvé ou si une autre erreur se produit.
    """
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier CSV non trouvé.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Une erreur interne est survenue lors de la lecture du fichier CSV.")


def write_csv(df, file_path):
    """
    Écrit un DataFrame dans un fichier CSV.

    Args:
        df (DataFrame): Le DataFrame à écrire dans le fichier CSV.
        file_path (str): Chemin où le fichier CSV sera enregistré.

    Raises:
        HTTPException: Si une erreur se produit lors de l'écriture dans le fichier CSV.
    """
    try:
        df.to_csv(file_path, index=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Une erreur interne est survenue lors de l'écriture dans le fichier CSV.")
