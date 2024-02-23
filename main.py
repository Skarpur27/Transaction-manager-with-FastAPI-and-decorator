from application import *
import uvicorn
from config import *


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)