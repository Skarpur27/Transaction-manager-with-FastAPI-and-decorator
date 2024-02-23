# Python OOP Project - FastApiDecoratorBuilder

The goal of this project is to design a Python decorator that transforms a Python function into a FastAPI-based API according to the function and defined configurations.

## Features

Automatic transformation of Python functions into FastAPI APIs.  
Flexible configuration of API properties, including routes and standard HTTP methods (GET, POST, PUT, DELETE).  

## Usage 

1. **Import the Decorator :**

	`from decorator import decorator`

2. **Apply the Decorator to a Function :**

	`@register_as_endpoint(path="/votre_route", methods=["GET", "POST"])  
	'def  votre_fonction(): # Logique de la fonction'`

3. **Start Your FastAPI Server :**

    `uvicorn.run(app, host="127.0.0.1", port=8000)`

##  Project Application

The rest of the project is a real application of the decorator and Fast API to a transaction manager:

Launching the Main.py file directs you to a local HTML page that displays net portfolio positions. Depending on the specified dates, prices are retrieved using a dataclass from Yahoo Finance.  
On this page, you can also add new transactions and access the transaction history of the portfolio.  

##  Fonctionnalités additionnelles :

The project also integrates several additional features in the utils.py file

A request_lov.csv file for collecting code execution logs.  
A rate limiter to prevent server overload.  
An exception handler to correct potential bugs.  

