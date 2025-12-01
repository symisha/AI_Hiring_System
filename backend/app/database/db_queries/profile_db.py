from app.database.db_connection import supabase



#profile preview
def get_company_by_user_id(user_id: str):
    res = supabase.table("companies").select("*").eq("id", user_id).execute()
    return res.data[0] if res.data else None

#profile update

def update_email(user_id: str, new_email: str):
    supabase.auth.api.update_user_by_id(user_id, {"email": new_email})
    #add verification

def update_password(user_id: str, new_password: str):
    supabase.auth.api.update_user_by_id(user_id, {"password": new_password})
    
def update_username(user_id: str, new_username: str):
    supabase.table("companies").update({"name": new_username}).eq("id", user_id).execute()



#more profile stuff