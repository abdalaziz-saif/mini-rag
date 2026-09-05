from fastapi import FastAPI , APIRouter , Depends  , Request
from models import ChunkModel
from models.db_schemes.project import Project


nlp_route = APIRouter(
    prefix = "/nlp"
)

