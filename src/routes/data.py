from fastapi import FastAPI , APIRouter , UploadFile , File , Depends , status 
from  fastapi.responses import JSONResponse 
from helpers.Config import get_settings , Settings 
from controller import DataController ,ProjectController , ProcessController
from models import ResponseSignal
import aiofiles
import logging
from .schemes.data import ProcessRequest

logger = logging.getLogger(__name__)
import aiofiles
import logging 

logger = logging.getLogger('uvicorn.error')

data_route = APIRouter(
    prefix = "/data1"
)

@data_route.post('/upload_files/{project_id}') 
async def uploade(project_id: str, file: UploadFile = File(...), app_settings: Settings = Depends(get_settings)):

        # we will split the logic of processing the file  { we will do it on Controller /  layer}  
        is_valid , status_code =  DataController().validate_uploaded_file(file = file) 
        
        if not is_valid : 
            return JSONResponse(
                 status_code=status.HTTP_400_BAD_REQUEST,
                 content ={
                    'signal' : status_code 
             }
         )

        #1  get the project path from project id 
        #2 generate unique file path name for the file to upload
            
        project_dir_path = ProjectController().get_project_path(project_id=project_id)
        file_path, file_id = DataController.generate_unique_filepath(
            orig_file_name=file.filename,
            project_id=project_id
        )
        # write the uploaded file as binary in  the  unique file Path that we made  
        try:
            async with aiofiles.open(file_path, "wb") as f:
                while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                    await f.write(chunk)
        except Exception as e:

            logger.error(f"Error while uploading file: {e}")

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
                }
            )

        return JSONResponse(
                content={
                    "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                    "file_id": file_id
                }
            )



@data_route.post('/process/{project_id}')        
async def process(project_id: str , ProcessRequest: ProcessRequest):
     
     process_controller = ProcessController(project_id=project_id)

    # get From the json request 
     file_id = ProcessRequest.file_id
     chunk_size = ProcessRequest.chunk_size 
     overlap_size = ProcessRequest.overlap_size 


     file_content = process_controller.get_file_content(file_id)

          
     file_chunks = process_controller.process_file_content(
               file_content=file_content ,
                chunk_size=chunk_size, 
                overlap_size=overlap_size )
          
     if file_chunks == None or len(file_chunks) == 0 : 
          
         return JSONResponse(
              status_code=status.HTTP_400_BAD_REQUEST,
              content = {
                   "signal" : ResponseSignal.PIROCESSINGFAILD.value
              }
         ) 