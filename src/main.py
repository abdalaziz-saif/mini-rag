from fastapi import FastAPI , APIRouter 
from routes import data
from routes import base
from motor.motor_asyncio import AsyncIOMotorClient  
from helpers import get_settings 

app = FastAPI()

# make motor connect directly when startup the app 
@app.on_evnet('startup') 
async def on_start_up():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.client_db = app.mongo_conn[settings.MONGODB_DATABASE]

# turn it off when shutdown app 
@app.on_event('shutdown')
async def on_shutdown():
    app.mongo_conn.close()
  
# include the base_route in the main app
app.include_router(base.base_route)
app.include_router(data.data_route)