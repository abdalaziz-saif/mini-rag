from .Enums.DataBaseEnum import DataBaseEnum 
from .BaseModel import BaseDataModel 
from .db_schemes.project import Project

class ProjectModel(BaseDataModel):

    def __init__(self , db_client):
        super().__init__(db_client=db_client)

        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

# buz of the problem that index function is async and init is not iwill make create_instance func

    @classmethod 
    async def create_instance(cls ,db_client):
         instance = cls(db_client)
         await instance.init_collection()

         return instance 





    # chek if the collection exist or not if not create it
    # create the index for the collection

    async def init_collection(self):

        collection_ls =  await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in collection_ls :
             self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

            #create the index for the collection 
             indexes = Project.get_indexes()
             for index in indexes:
                  await self.collection.create_index(
                       index["key"] , 
                       name = index["name"],
                       unique = index["unique"]
                  )
         



# create a  project inside the collection 
    async def create_project(self, project : Project):
            result = await self.collection.insert_one(project.dict())
            project.id = result.inserted_id 
            
            return project 

    async def get_project_or_create(self, project_id):

            record = await self.collection.find_one({
                "project_id" : project_id
            })  

            if record == None :
                project = Project(project_id = project_id)
                result = await self.create_project(project)

                return result
             
            return Project(**record)                      # return it on form Project 
        
    async def get_all_projects(self, page: int=1, page_size: int=10):

            # count total number of documents
            total_documents = await self.collection.count_documents({})

            # calculate total number of pages
            total_pages = total_documents // page_size
            if total_documents % page_size > 0:
                total_pages += 1

            cursor = self.collection.find().skip( (page-1) * page_size ).limit(page_size)
            projects = []
            async for document in cursor:
                projects.append(
                    Project(**document)
                )

            return projects, total_pages