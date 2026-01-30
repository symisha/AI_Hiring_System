from app.database.db_queries.specific_job_db import delete_job_db
from fastapi import APIRouter, Depends
from app.auth_middleware import auth_middleware
from uuid import UUID

delRouter = APIRouter()

@delRouter.delete("/delete-job/{job_id}")

def delete_job_route(job_id: UUID, user=Depends(auth_middleware)): 
    # Call the delete_job_db function directly since service layer is not needed
    result = delete_job_db(job_id)
    return result