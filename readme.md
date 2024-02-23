# Projet Python OOP - FastApiDecoratorBuilder

L'objectif de se projet est de concevoir un décorateur Python qui transforme une fonction Python en une API FastAPI basée sur la fonction et des configurations définies.

# Table des Matières

1. [Fonctionnalités](#fonctionnalit\u00E9s)
2. [Utilisation](#utilisation)
   - [Importez le Décorateur](#1-importez-le-d\u00E9corateur-)
   - [Appliquez le Décorateur à une Fonction](#2-appliquez-le-d\u00E9corateur-\u00E0-une-fonction-)
   - [Démarrez votre serveur FastAPI](#3-d\u00E9marrez-votre-serveur-fastapi-)
3. [Application du projet](#application-du-projet)
4. [Fonctionnalités additionnelles](#fonctionnalit\u00E9s-additionnelles)



# Fonctionnalités

-   Transformation automatique des fonctions Python en API FastAPI.
-   Configuration flexible des propriétés de l'API, y compris des routes et des méthodes HTTP classique (GET, POST, PUT, DELETE).

# Utilisation 

1. **Importez le Décorateur** :

	`from decorator import decorator`

2. **Appliquez le Décorateur à une Fonction** :

	`@register_as_endpoint(path="/votre_route", methods=["GET", "POST"])  
	'def  votre_fonction(): # Logique de la fonction'`

3. **Démarrez votre serveur FastAPI** :

    `uvicorn.run(app, host="127.0.0.1", port=8000)`

#  Application du projet  

Le reste du projet est une application réelle du décorateur et de Fast API à un gestionnaire de transaction : 

- Le lancement du fichier Main.py vous renvoie vers une page html en local permettant d'afficher des positions nettes de portefeuilles. En fonction des dates spécifiées les prix sont récupéré à l'aide d'une dataclass sur Yahoo Finance.
- Sur cette page vous pouvez également ajouter de nouvelles transactions et accéder à l'historique des transactions du portefeuille.

#  Fonctionnalités additionnelles :

Le projet intègre également plusieurs fonctionnalités additionnelles dans le fichier utils.py

- Un fichier request_lov.csv permettant de récolter les logs d'exécution du code.
- Un rate limiter permettant de prévenir la surcharge du serveur.
- Un gestionnaire d'exception permettant de corriger d'éventuels bugs.

# Auteurs

- Joudy Benkaddour
- Nassim Chamakh
- Naïm Lehbiben

