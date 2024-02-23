from datetime import datetime, timedelta
import pandas as pd
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

def is_rate_limited(file_path, client_ip, time_window=10):
    """
    Vérifie si un client IP est limité en taux dans une fenêtre de temps donnée.

    Args:
        file_path (str): Chemin du fichier CSV contenant les enregistrements des requêtes.
        client_ip (str): Adresse IP du client à vérifier.
        time_window (int): Fenêtre de temps (en secondes) pour vérifier la limitation de taux.

    Returns:
        bool: True si le client est limité en taux, False sinon.

    Raises:
        Exception: Si une erreur survient lors de la lecture du fichier ou du traitement des données.
    """
    try:
        # Lecture du fichier CSV
        df = pd.read_csv(file_path)

        # Filtrage des requêtes pour l'IP spécifiée et tri par date et heure
        df_ip = df[df['client_ip'] == client_ip].sort_values(by='timestamp', ascending=False)

        # Vérifier si la dernière requête est dans la fenêtre de temps
        if not df_ip.empty:
            latest_request_time = pd.to_datetime(df_ip.iloc[0]['timestamp'])
            if datetime.now() - latest_request_time < timedelta(seconds=time_window):
                return True
        return False
    except Exception as e:
        # Gestion des exceptions potentielles lors de l'accès au fichier ou de la manipulation des données
        raise Exception("Une erreur est survenue lors de la vérification de la limitation de taux.")


class SimpleCache:
    """
    Classe SimpleCache pour implémenter un mécanisme de cache basique.

    Cette classe utilise un dictionnaire pour stocker des données en cache.
    Elle offre des méthodes pour définir, obtenir, et effacer des données en cache.
    """

    def __init__(self):
        """Initialise le cache comme un dictionnaire vide."""
        self.cache = {}

    def set_cache(self, key, value):
        """
        Stocke une valeur dans le cache.

        Args:
            key: La clé sous laquelle stocker la valeur.
            value: La valeur à stocker dans le cache.
        """
        self.cache[key] = value

    def get_cache(self, key):
        """
        Récupère une valeur du cache.

        Args:
            key: La clé de la valeur à récupérer.

        Returns:
            La valeur stockée dans le cache pour la clé donnée, ou None si la clé n'existe pas.
        """
        return self.cache.get(key)

    def clear_cache(self, key):
        """
        Efface une valeur spécifique du cache.

        Args:
            key: La clé de la valeur à effacer du cache.

        Cette méthode ne fait rien si la clé n'existe pas dans le cache.
        """
        if key in self.cache:
            del self.cache[key]


# Instance globale de SimpleCache
cache = SimpleCache()


async def http_exception_handler(request, exc):
    """
    Gestionnaire d'exception pour les erreurs HTTP.

    Args:
        request: La requête FastAPI.
        exc (StarletteHTTPException): L'exception HTTP levée.

    Returns:
        JSONResponse: Une réponse JSON avec le code de statut et le détail de l'erreur.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

async def general_exception_handler(request, exc):
    """
    Gestionnaire d'exception pour les erreurs non gérées.

    Args:
        request: La requête FastAPI.
        exc: L'exception levée.

    Returns:
        JSONResponse: Une réponse JSON avec un code de statut 500 et un message d'erreur générique.
    """
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne non gérée est survenue."}
    )
