from email.policy import default
import json
from controller import BaseController
from models.db_schemes.data_chunk import DataChunk
from models.db_schemes.project import Project
from stores.vectorDB import VectorDBFactory
from models.ChunkModel import ChunkModel
from stores.llm.LLMEnums import DocumentTypeEnum

class NLPController(BaseController):


    def __init__(self, vectordb_client, generation_client, 
                 embedding_client):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client


    def create_collection_name (self, project_id):
        return f"collection_{project_id}".strip()

    def reset_vectordb_collection(self, project:Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name)

    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.load(
            json.dumb(collection_info, default=lambda x: x.__dict__)
        )

    def index_into_vectordb(self,project: Project,chunks: list[DataChunk], chunks_ids: list[int], do_reset: bool=False) :

         
       # crate collection name 
        collection_name = self.create_collection_name(project_id=project.project_id)

        # embedding text  
        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]

        vectors = [

               self.embedding_client.embed_text(text ,DocumentTypeEnum.DOCUMENT.value )
            for text in texts 
        ]

        # crate collection if not exist 
        _=self.vectordb_client.create_collection( collection_name = collection_name, 
                                                 embedding_size=self.embedding_client.embedding_size , 
                                                 do_reset = do_reset)


        # insert vectores into collection
        _= self.vectordb_client.insert_many(collection_name=collection_name, 
                                            texts=texts, 
                                            vectors=vectors, 
                                            metadata =metadata, 
                                            record_ids=chunks_ids)

    def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):

        # get collection_name 
        collection_name = self.create_collection_name(project_id=project.project_id)

        # convert the text into vecotr  
        vector = self.embedding_client.embed_text(text ,DocumentTypeEnum.QUERY.value)

        # seart on vectore database 
        results = self.vectordb_client.search_by_vector(collection_name=collection_name, vector=text, limit=limit)


        if not results:
            return False

        return results
    