from pydantic import BaseModel
from enum import Enum

class OperationType(Enum):
    """
    Énumération des différents types d'opérations sur les actions.
    """
    SELL = "sell"
    BUY = "buy"
    BUYTOCOVER = "buy to cover"
    SHORTSELL = "short sell"


class StockEntry(BaseModel):
    """
    Modèle représentant une entrée de stock, avec des détails tels que la date, l'ISIN, etc.

    Attributs:
        date (str): Date de l'opération.
        isin (str): Code ISIN de l'action.
        company_name (str): Nom de l'entreprise.
        quantity (float): Quantité d'actions.
        unit_price (float): Prix unitaire de l'action.
        operation_type (OperationType): Type d'opération (achat, vente, etc.).
    """
    date: str
    isin: str
    company_name: str
    quantity: float
    unit_price: float
    operation_type: OperationType


class UpdateStockEntry(BaseModel):
    """
    Modèle pour la mise à jour d'une entrée de stock existante.

    Attributs:
        index (int): Identifiant de l'entrée à mettre à jour.
        date (str): Nouvelle date de l'opération.
        isin (str): Nouveau code ISIN de l'action.
        company_name (str): Nouveau nom de l'entreprise.
        quantity (int): Nouvelle quantité d'actions.
        unit_price (float): Nouveau prix unitaire de l'action.
        operation_type (str): Nouveau type d'opération.
    """
    index: int
    date: str
    isin: str
    company_name: str
    quantity: int
    unit_price: float
    operation_type: str


class DeleteStockEntry(BaseModel):
    """
    Modèle pour la suppression d'une entrée de stock.

    Attributs:
        index (int): Identifiant de l'entrée à supprimer.
    """
    index: int


class NetPosition(BaseModel):
    """
    Modèle représentant la position nette d'une action dans le portefeuille.

    Attributs:
        isin (str): Code ISIN de l'action.
        quantity_in_portfolio (float): Quantité totale de l'action dans le portefeuille.
        current_price (float): Prix actuel de l'action.
        net_position (float): Position nette de l'action (quantité * prix actuel).
        price_history (dict): Historique des prix de l'action.
    """
    isin: str
    quantity_in_portfolio: float
    current_price: float
    net_position: float
    price_history: dict

class ResponseModel(BaseModel):
    message: str

class Method(Enum):
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'
