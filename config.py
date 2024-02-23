import os

# Obtient le répertoire courant dans lequel se trouve ce script
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Construit le chemin complet vers le fichier CSV contenant les transactions de stock
# Ce fichier est nommé "updated_stock_transactions.csv" et se situe dans le même répertoire que ce script.
FILE_PATH = os.path.join(CURRENT_DIRECTORY, "updated_stock_transactions.csv")

#Configuration du host et du port
HOST = "127.0.0.1"
PORT = 8012
