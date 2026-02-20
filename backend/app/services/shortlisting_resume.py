#extract all the rating from database
#check the deviation of the ratings
#that decides the threshold for shortlisting
# if the rating is above the threshold, then the resume is shortlisted
from app.database.db_connection import supabase        



def shortlist_resumes(job_id: str):
    #get all the ratings for the job_id
    ratings = supabase.table("job_applications").select("resume_score").eq("job_id", job_id).execute().data
    scores = [r["resume_score"] for r in ratings if r["resume_score"] is not None]
    
    if not scores:
        return []
    
    #calculate the mean and standard deviation
    mean_score = sum(scores) / len(scores)
    std_dev = (sum((x - mean_score) ** 2 for x in scores) / len(scores)) ** 0.5
    
    #set the threshold as mean + 1 standard deviation
    threshold = mean_score + std_dev
    
    #get all the resumes that have a score above the threshold
    shortlisted_resumes = supabase.table("job_applications").select("*").eq("job_id", job_id).gt("resume_score", threshold).execute().data
    
    return shortlisted_resumes      


def send_emails(shortlisted_resumes):
    for resume in shortlisted_resumes:
        email = resume["email"]
        #send email to the candidate
        print(f"Email sent to {email} for shortlisting")