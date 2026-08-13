from .BaseController import BaseController
from .ProjectController import ProjectController
import os 
from langchain_docling.loader import DoclingLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ProcessController(BaseController):

    def __init__(self , project_id):
        super().__init__() 


        self.project_id = project_id 
        self.project_path = ProjectController().get_project_path(self.project_id) 
      
    #extract the content of the file using langchain
    def get_file_content(self , file_id) :
        self.file_path = os.path.join(
            self.project_path , 
            file_id
        )

        loader = DoclingLoader(self.file_path) 
        return  loader.load()  # the output will be in shape document(text =  , metadata = )

    # split the content to chunks  
    def process_file_content(self , file_content :list , chunk_size : int =100  , overlap_size :int =20):

            text_spliter = RecursiveCharacterTextSplitter(
                 chunk_size = chunk_size , 
                 chunk_overlap = overlap_size , 
                 length_function=len
                 )


            file_content_text = [
                    rec.page_content
                 for rec in file_content 
            ]
            
            file_content_metadata = [
                    rec.metadata
                 for rec in file_content
            ]
        
         
            chunks = text_spliter.create_documents(
                file_content_text,
                 metadatas=file_content_metadata
            )
            
            return chunks 
  
