
import os 
from fastapi import FastAPI , APIRouter , UploadFile , File , Depends , status , Request 
from  fastapi.responses import JSONResponse 
from helpers.Config import get_settings , Settings 
from controller import DataController ,ProjectController , ProcessController
from models import ResponseSignal
import aiofiles
import logging

from models.db_schemes.data_chunk import DataChunk
from models.db_schemes.asset import Asset
from .schemes.data import ProcessRequest
from models import ProjectModel , BaseDataModel , ChunkModel , AssetModel
from models.Enums.AssetTypeEnum import AssetTypeEnum

logger = logging.getLogger(__name__)
import aiofiles
import logging 

logger = logging.getLogger('uvicorn.error')

data_route = APIRouter(
    prefix = "/data"
)

@data_route.post('/upload_files/{project_id}') 
async def uploade(request : Request ,project_id: str, file: UploadFile = File(...), app_settings: Settings = Depends(get_settings)):

       #ihave to get the db client from the app to pass it to Project class  so iwill use Request  
       
        # project_model = ProjectModel(
        #    Request.app.db_client
        # )


        project_model = await ProjectModel.create_instance(
             db_client=request.app.client_db)

        project = await project_model.get_project_or_create(project_id = project_id)


       
       
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
        file_path, file_id = DataController().generate_unique_filepath(
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

    # STORE THE ASSET[FILE] INTO DATABASE   

        asset_model = await AssetModel.create_instance(
             db_client=request.app.client_db
        )

        asset_resource = Asset(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value,
            asset_name=file_id,
            asset_size=os.path.getsize(file_path)
        )

        asset_record =await asset_model.create_asset(asset_resource) 




        return JSONResponse(
                content={
                    "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                    "file_id": str(asset_record.id),
            
                }
            )



@data_route.post('/process/{project_id}')        
async def process(project_id: str , ProcessRequest: ProcessRequest , request :Request):
     
     process_controller = ProcessController(project_id=project_id)

     no_records = 0 
     no_files = 0 

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

     

     project_model = await ProjectModel.create_instance(
             db_client=request.app.client_db)
       
     project = await project_model.get_project_or_create(project_id = project_id)


     chunk_model = await ChunkModel.create_instance(
          request.app.client_db 
     )


     file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1,
                chunk_project_id=project.id,
        
            )
            for i, chunk in enumerate(file_chunks)
        ]

     no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
     no_files += 1

     return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files": no_files
        }
    )