from fastapi import *
from utils import *
from starlette.requests import Request
from methods import *
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from home_page import *
from fastapi.responses import JSONResponse
from fastapi import Form


app = FastAPI(debug=True)


# Gestionnaires d'exceptions
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# décorateur
def register_route(path: str, method: Method):
    """
     #   création d'un décorateur fastAPI de gestion des Tests
     #   :param path: lien vers la route
     #   :param method: get / post / put / delete
     #   :return: l'output de la fonction décorateur est la fonction associée à la route définie

     """
    def decorator(func):
        match method.lower():
            case 'get':
                app.get(path)(func)
            case 'post':
                app.post(path)(func)
            case 'put':
                app.put(path)(func)
            case 'delete':
                app.delete(path)(func)
            case 'patch':
                app.patch(path)(func)
            case _:
                raise HTTPException(status_code=404, detail="méthode non gérée")
        return func
    return decorator



# Create a Jinja2Templates instance and specify the "templates" directory
templates = Jinja2Templates(directory="templates")

# récupération en objet StockEntry des éléments du fichier csv
items = get_item_dict()

# définition d'une route en utilisant le décorateur
@register_route("/", method="get")
async def get_home_page(request: Request):
    """
    Calculer et mettre-à-jour les positions nettes
    et les plus ou moins values latentes et réalisées
    en fonction de l'inventaire des transactions
    :param request:
    :return:
    """
    # récupération des lignes du csv en dict StockEntry
    items = get_item_dict()

    # calcul des positions netttes à partir de l'inventaire des transactions items
    items_net_positions = get_net_position(items)

    # calcul des plus-values latentes
    gains, latent_gains = calculate_portfolio_gains(items_net_positions)

    #affichage du résultat dans le template
    return templates.TemplateResponse("home.html", {
        "request": request,
        "items": items_net_positions,
        "gains": gains,
        "latent_gains": latent_gains
    })


# définition d'une route en utilisant le décorateur
@register_route("/add-item", method="post")
async def add_item(date: str = Form(...), isin: str = Form(...), company_name: str = Form(...), quantity: float = Form(...), operation_type: str = Form(...)):
    """
    Ajouter un élément à notre inventaire et l'ajouter à notre objet items: BaseModel ainsi qu'à un fichier .csv (qui fait figure de database lorsqu'on ferme l'API)
    :param date:
    :param isin:
    :param company_name:
    :param quantity:
    :param operation_type:
    :return: une fois l'élément ajouté, s'il n'y a pas d'erreurs on est regirrigé vers l'inventaire /read_stock_data
    """

    # affectation d'un id au nouvel élément
    new_item_id = max(items.keys()) + 1 if items else 0

    # vérification que l'input entré par l'utilisateur pour operation_type est valide
    op_type = test_operation_type(operation_type)

    # gestion d'rrreur : operation_type n'est pas valide
    if not op_type:
        raise HTTPException(status_code=500,
                            detail=f"Invalid operation type. Expected {[operation_type.value for operation_type in OperationType]} but got {operation_type}")

    # vérification que le ticker entré est valide
    if not is_valid_yfinance_ticker(isin):
        raise HTTPException(status_code=400, detail="ticker invalide")

    try:
        # Test de conversion de date en un objet datetime
        dateobj = datetime.strptime(date, "%Y-%m-%d")

    except ValueError:
        raise HTTPException(status_code=400, detail="format de date invalide. Veuillez entrer une date en format yyyy-mm-dd")

    # récupération du prix à partir de la date et l'isin
    result = get_unit_price(date, isin)
    date = result['date']
    unit_price = result['price']

    #création d'un nouvel élément new_item: StockEntry
    new_item = StockEntry(index=new_item_id, date=date, isin=isin, company_name=company_name, quantity=quantity, unit_price=unit_price, total_price=unit_price*quantity, operation_type=op_type)

    # ajout de l'élément au dictionnaire
    items[new_item_id] = new_item

    # mise-à-jour des données dans le csv
    update_dict = new_item.dict()

    # conversion de operation_type en string
    update_dict['operation_type'] = op_type

    # calcul de total_price
    update_dict['total_price'] = quantity*unit_price

    # conversion en df de la ligne créée
    new_item_df = pd.DataFrame([update_dict])

    # ajout du nouvel élément au df contenant les données du csv
    df = pd.concat([read_csv(FILE_PATH), new_item_df])

    # conversion en csv du nouveau df
    df.to_csv(FILE_PATH, index=False)

    # JavaScript response pour redirriger vers la page d'accueil
    response_html = f"""
    <script>
        window.location.href = "/";
    </script>
    """

    # Après l'ajout, rediriger vers la page d'accueil
    return RedirectResponse(url="/", status_code=303)



# définition d'une route en utilisant le décorateur
@register_route("/read_stock_data", method="get")
async def read_stock_data_api() -> dict[str, dict[int, StockEntry]]:
    """
    récupération et affichage des données sur l'api
    :return:
    """
    return {"items": items}

# définition d'une route en utilisant le décorateur
@register_route("/read_stock_data/items/{item_id}", method="get")
def query_item_by_id(item_id: int) -> StockEntry:
    """
    Récupération sur l'API d'un élément en particulier en spécifiant son id
    cf: Tests/retrieve_stock_by_id.py
    :param item_id: int
    :return: {response : {item:StockEntry}}
    """
    # gestion d'erreurs si l'id entré par l'utilisateur n'est pas valide
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"item with {item_id} does not exist")
    # récupération de l'élément correspondant sous fore d'un message json
    return JSONResponse(content=f"item {items[item_id]}")

Selection = dict[str, str | int | float | OperationType | None]

#http://127.0.0.1:8012/read_stock_data/items/?isin=AAPL
# définition d'une route en utilisant le décorateur
@register_route("/read_stock_data/items/", method="get")
def query_item_by_parameters(
    isin: str | None = None,
    unit_price: float | None = None,
    quantity: float | None = None,
    operation_type: OperationType | None = None):
    """
    Récupération sur l'API d'un ou plusieurs éléments à partir de l'isin / le type d'opération / le unit_price
    cf: Tests/retrieve_stock_by_id.py
    :param isin:
    :param unit_price:
    :param quantity:
    :param operation_type:
    :return: {JSONResponse : {item:StockEntry}}
    """
    # Initialisatoin d'une liste vide pour stocker les éléments sélectionnés en fonction des paramètres
    selected_items = []

    # itérations sur tous les éléments de items
    for item in items.values():

        # Vérifie si l'ISIN correspond au paramètre ou si le paramètre n'est pas spécifié
        if isin is None or item.isin == isin:

            # Convertit l'élément en dictionnaire
            item_dict = item.dict()

            # Convertit le type d'opération en chaîne de caractères
            if item.operation_type is not None:
                item_dict["operation_type"] = item.operation_type.value

            # Ajoute l'élément sélectionné à la liste
            selected_items.append(item_dict)

    # Création d'un dictionnaire de réponse avec les résultats de la requête
    response_data = {
        "query": {
            "isin": isin,
            "unit_price": unit_price,
            "quantity": quantity,
            "operation_type": operation_type.value if operation_type else None,
        },
        "selection": selected_items,  # Ajoute les éléments sélectionnés dans la réponse
    }

    return JSONResponse(content=response_data)

# Modifier la fonction update pour accepter le corps de la requête au format JSON
# Définition de la route en utilisant le décorateur
@register_route("/read_stock_data/update_stock_data/{item_id}", method="put")
async def update_item(item_id: int, request: Request):
    """
    modifier un élément de l'inventaire dans l'API et enregistrer cette modification dans le fichier csv
    cf: Tests/test_query.py
    :param item_id:
    :param data: Les données JSON dans le corps de la requête
    :return: un message de succès après avoir modifié l'élément selon les informations renseignés
    """
    data = await request.json()

    # Récupère l'élément spécifié par son ID
    item = items[item_id]

    # Vérifie si 'quantity' est présent dans les données JSON
    if 'quantity' in data:
        quantity = data['quantity']
        item.quantity = quantity  # Met à jour la quantité

        # Met à jour le prix unitaire en fonction de la date et de l'ISIN
        result = get_unit_price(item.date, item.isin)
        item.unit_price = result["price"]
        item.date = result["date"]

        # Met à jour l'élément dans le dictionnaire 'items'
        items[item_id] = item
        index = item_id

        # Conversion de operation_type en str
        for item_id, item in items.items():
            item.operation_type = item.operation_type.value

        # Crée un DataFrame pandas à partir des éléments du stock
        df = pd.DataFrame([item.dict() for item in items.values()])

        # Retranscription dans le CSV de l'API après avoir modifié les données
        df['total_price'] = df['quantity'] * df['unit_price']
        column_order = ['date', 'isin', 'company_name', 'quantity', 'unit_price', 'total_price', 'operation_type']
        df = df[column_order]

        df.to_csv(FILE_PATH, index=False)  # Enregistre le DataFrame dans un fichier CSV

        # Message de réponse
        response_data = {"message": f"Item {items[index]} updated successfully"}
    else:
        # Si 'quantity' n'est pas présent dans les données JSON, retournez une erreur
        raise HTTPException(status_code=400, detail="The 'quantity' field is required in the JSON data.")

    return response_data

# définition d'une route en utilisant le décorateur
@register_route("/read_stock_data/delete_stock_data/{item_id}", method="delete")
def delete_item(item_id: int) -> ResponseModel:
    """
    supprimer un item après avoir spécifié l'id
    cf: Tests/delete_line.py
    :param item_id:
    :return:
    """
    if item_id not in items:
        raise HTTPException(
            status_code=404, detail=f"Item with {item_id=} does not exist."
        )

    #suppression de l'item dans l'API
    item = items.pop(item_id)

    for item_id, item in items.items():
        # Conversion de operation_type en string
        item.operation_type = item.operation_type.value

    # Mise-à-jour du csv avec les changements
    df = pd.DataFrame([item.dict() for item in items.values()])

    df['total_price'] = df['quantity'] * df['unit_price']

    column_order = ['date', 'isin', 'company_name', 'quantity', 'unit_price', 'total_price', 'operation_type']
    df = df[column_order]

    df.to_csv(FILE_PATH, index=False)

    # message de réponse
    response_data =  {"message": f"Item {item} deleted successfully"}

    return JSONResponse(content=response_data)




