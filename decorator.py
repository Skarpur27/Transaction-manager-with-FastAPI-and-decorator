from fastapi import FastAPI
from config import SUPPORTED_HTTP_METHODS
import pandas as pd
from data_manager import *
from config import *
from main import *
app = FastAPI(debug=True)  # Création d'une instance de l'application FastAPI avec le mode débogage activé

def decorator(path: str, methods: list):
    """
    Un décorateur pour créer dynamiquement des routes dans une application FastAPI.
    Il permet de définir une route avec des méthodes HTTP spécifiées dans la liste 'methods'.

    Args:
        path (str): Le chemin d'accès (endpoint) de la route.
        methods (list): Une liste des méthodes HTTP à supporter pour cette route (par exemple, GET, POST).

    Returns:
        Function: La fonction décorée, maintenant liée aux routes et méthodes HTTP spécifiées.
    """
    def decorator(func):
        # Itération sur chaque méthode HTTP fournie dans la liste
        for method in methods:
            # Association de la fonction avec la route et la méthode HTTP correspondante
            if method.lower() == 'get':
                app.get(path)(func)
            elif method.lower() == 'post':
                app.post(path)(func)
            elif method.lower() == 'put':
                app.put(path)(func)
            elif method.lower() == 'delete':
                app.delete(path)(func)

        return func  # Retourne la fonction décorée
    return decorator
