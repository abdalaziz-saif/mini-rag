from .BaseController import BaseController
from fastapi import UploadFile  
from models import ResponseSignal 


class DataController(BaseController) : 

    def __init__(self):
        super().__init__()

        def validate_uploaded_file (self , file:UploadFile):

            if file.content.size > self.app_settings.FILE_MAX_SIZE * 1024 * 1024 : 
                return False , ResponseSignal.FILE_SIZE_EXCEEDED.value

            if file.content.type not in self.app_settings.FILE_ALLOWED_TYPES : 
                return False , ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
            
            return ResponseSignal.FILE_VALIDATED_SUCCESS.value 