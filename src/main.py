from fastapi import FastAPI , APIRouter 
from routes import data
from routes import base
from motor.motor_asyncio import AsyncIOMotorClient  
from helpers import get_settings 
from stores.llm import LLMFactory

app = FastAPI()

# make motor connect directly when startup the app 
@app.on_event('startup') 
async def on_start_up():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.client_db = app.mongo_conn[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMFactory(settings)

    #generation model 
    app.generation_model = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_model.set_generation_model(settings.GENERATION_MODEL_ID)

    #Embedding Model 
    app.embedding_model = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_model.set_embedding_model(settings.EMBEDDING_MODEL_ID , settings.EMBEDDING_MODEL_SIZE)

    

# turn it off when shutdown app 
@app.on_event('shutdown')
async def on_shutdown():
    app.mongo_conn.close()
  
# include the base_route in the main app
app.include_router(base.base_route)
app.include_router(data.data_route)