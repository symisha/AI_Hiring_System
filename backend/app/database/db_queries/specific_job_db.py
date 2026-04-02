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


def update_job_db(job_id: UUID, title: str, short_description: str, metadata: dict):
    try:
        result = supabase.table("jobs").update({
            "title": title,
            "short_description": short_description,
            "job_metadata": metadata
        }).eq("id", job_id).execute()
        if result.data:
            return {"success": True, "data": result.data[0]}
        return {"error": "Job not found"}
    except Exception as e:
        return {"error": "Failed to update job"}


def set_job_status_db(job_id: UUID, status: str):
    """Update only the status column (apply_token column may not exist in all deployments)."""
    try:
        result = supabase.table("jobs").update({"status": status}).eq("id", str(job_id)).execute()
        if result.data:
            return {"success": True, "data": result.data[0]}
        # Supabase update returns empty data when RLS is off but row-level returns are disabled;
        # treat no-exception as success.
        return {"success": True}
    except Exception as e:
        return {"error": f"Failed to update job status: {e}"}


def try_persist_apply_token(job_id: UUID, apply_token: str) -> bool:
    """Best-effort: persist apply_token to DB. Returns True on success, False if column missing."""
    try:
        supabase.table("jobs").update({"apply_token": apply_token}).eq("id", str(job_id)).execute()
        return True
    except Exception:
        return False


def close_job_db(job_id: UUID):
    return set_job_status_db(job_id, "inactive")


def activate_job_db(job_id: UUID):
    return set_job_status_db(job_id, "open")


def delete_job_db(job_id: UUID):
    try:
        supabase.table("jobs").delete().eq("id", job_id).execute()
        return {"success": True}
    except Exception as e:
        return {"error": "Failed to delete job"}  # ambiguous message for security 
        