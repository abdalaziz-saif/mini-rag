from .Enums.DataBaseEnum import DataBaseEnum 
from .BaseModel import BaseDataModel 
from .db_schemes.project import Project
from .db_schemes.data_chunk import DataChunk
from bson.objectid import ObjectId  
from pymongo import InsertOne

class ChunkModel(BaseDataModel):

    def __init__(self):
        super.__init__(self.db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]




    @classmethod 
    async def create_instance(cls ,db_client):
         instance = cls(db_client)
         await instance.init_collection()

         return instance 


    # chek if the collection exist or not if not create it
    # create the index for the collection

    async def init_collection(self):

        collection_ls =  await self.collection.list_collections_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in collection_ls :
             self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

            #create the index for the collection 
             indexes = Project.get_indexes()
             for index in indexes:
                  await self.collection.create_index(
                       index["key"] , 
                       name = index["name"],
                       unique = index["unique"]
                  )










# iwill recieve a chunks in form DAtaChunk then i will store inside mongo 

    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk._id = result.inserted_id
        return chunk

    async def get_chunk(self, chunk_id: str):
        result = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })

        if result is None:
            return None
        
        return DataChunk(**result)

    # iwill inset many chunks toghether   

    async def insert_many_chunks(self, chunks: list, batch_size: int=100):

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]

            operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)
        
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })

        return result.deleted_count
    