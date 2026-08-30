from .Enums.DataBaseEnum import DataBaseEnum 
from .BaseModel import BaseDataModel 
from .db_schemes.data_chunk import DataChunk
from bson.objectid import ObjectId  
from pymongo import InsertOne
from datetime import datetime, date

BSON_INT_MAX = 9223372036854775807
BSON_INT_MIN = -9223372036854775808


def _sanitize_for_mongo(value):
    if isinstance(value, dict):
        return {str(k): _sanitize_for_mongo(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize_for_mongo(v) for v in value]
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value > BSON_INT_MAX or value < BSON_INT_MIN:
            return str(value)
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, str):
        return value
    if value is None:
        return value
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, (datetime, date)):
        return value
    if hasattr(value, "item") and callable(value.item):
        return _sanitize_for_mongo(value.item())
    return str(value)


def _chunk_to_document(chunk: DataChunk) -> dict:
    doc = chunk.model_dump(by_alias=True, exclude_unset=True)
    if "chunk_metadata" in doc:
        doc["chunk_metadata"] = _sanitize_for_mongo(doc["chunk_metadata"])
    return doc

class ChunkModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]




    @classmethod 
    async def create_instance(cls, db_client):
         instance = cls(db_client)
         await instance.init_collection()

         return instance 


    # chek if the collection exist or not if not create it
    # create the index for the collection

    async def init_collection(self):

        collection_ls =  await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in collection_ls :
             self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

            #create the index for the collection 
             indexes = DataChunk.get_indexes()
             for index in indexes:
                  await self.collection.create_index(
                       index["key"] , 
                       name = index["name"],
                       unique = index["unique"]
                  )










# iwill recieve a chunks in form DAtaChunk then i will store inside mongo 

    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(_chunk_to_document(chunk))
        chunk.id = result.inserted_id
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
                InsertOne(_chunk_to_document(chunk))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)
        
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })

        return result.deleted_count
    