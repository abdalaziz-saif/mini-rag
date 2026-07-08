from fastapi import FastAPI , APIRouter 
from routes import data

from routes import base 

app = FastAPI()

# include the base_route in the main app
app.include_router(base.base_route)
app.include_router(data.data_route)