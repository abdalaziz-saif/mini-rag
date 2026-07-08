from fastapi import FastAPI , APIRouter , UploadFile ,Depends , status 
from  fastapi.responses import JSONResponse 
from helpers.Config import get_settings , Settings 
from controller import DataController 



data_route = APIRouter(
    prefix = "/data1"
)

@data_route.post('/upload_files/{project_id}') 
async def uploade(project_id : str , file : UploadFile 
                    ,app_settings : Settings = Depends(get_settings) ):

        # we will split the logic of processing the file  { we will do it on Controller /  layer}  
        is_valid =  DataController().validate_uploaded_file(file) 
        return JSONRespone(
            status_code=status.HTTP_400_BAD_REQUEST,
            content ={
                'signal' : is_valid 
            }
        )
