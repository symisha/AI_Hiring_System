from app.database.db_connection import supabase
from uuid import UUID

#delete button leads to this function

#def delete_job(#make sure its the right user, #job_id
#        ):
    #supabase.delete the JOb_id 
    #error upon unable to delete 


#edit button leads to this 
#
#it is a form resubmsion, so the real question is that should i just do this in the frontend 
#or so i so it in backend 

#moreover how is the job description is gonna be processed. Editing it will depend on that 


def delete_job_db(job_id: UUID):
    supabase.table("jobs").delete().eq("id", job_id).execute()
    if supabase.error:
        return {"error": supabase.error.message}    #should be replaced with ambigous message 
        