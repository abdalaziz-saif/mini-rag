from fastapi import FastAPI , APIRouter , Depends 
from helpers.Config import get_settings , Settings 


base_route = APIRouter(
    prefix = '/route1'
)


@base_route.get('/')
async def root(app_settings :Settings = Depends(get_settings)):
    # uses the settings from the Config.py file
    app_name = app_settings.APP_NAME

    return {
        "app" : app_name ,
        'helth' : 'ok'
    } 