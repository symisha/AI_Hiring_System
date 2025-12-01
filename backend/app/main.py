
import uvicorn                                          # ASGI server used to run FastAPI apps (like "npm start" for Node)
from fastapi import FastAPI, Depends                             # Main FastAPI class used to create the web application instance
from fastapi.middleware.cors import CORSMiddleware      # Middleware to handle CORS (Cross-Origin Resource Sharing) — allows frontend (React, etc.) to communicate with backend
from pydantic import BaseModel                          # Used to define and validate data models (for requests/responses) with type checking
from app.config.config import Settings                    # Import the Settings class from the config module to access environment variables
from app.routes.dashboard_essentials import dashboard_info
from app.routes.dashboard_essentials.profile_preview_router import router 

from app.database.db_connection import supabase         # Import the Supabase client instance to interact with the database
#from app.database.db_queries import dashboard_info
from app.auth_middleware import auth_middleware         # Import the authentication middleware to protect routes


app = FastAPI()  # Create FastAPI app instance, This line creates the main application object that will handle all incoming HTTP requests

orgins =[
    #"http://localhost:8000" , # Frontend URL, This is the URL of the frontend application (React, etc.) that will communicate with this backend
]


# Include your endpoints
#app.include_router(rating_resume.router, prefix="/routes", tags=["rating"])
app.include_router(dashboard_info.router, prefix="/routes/dashboard_essentials", tags=["database"])
app.include_router(router, prefix="/routes/dashboard_essentials", tags=["database"])


app.add_middleware(
    CORSMiddleware,            # Add CORS middleware to the FastAPI app, This middleware allows the backend to accept requests from the specified origins
    allow_origins=Settings.FRONTEND_URL,  # List of allowed origins (frontend URLs)
    allow_credentials=True,   # Allow cookies and authentication headers        
    allow_methods=["*"],      # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],      # Allow all headers
)

@app.get("/")  # Define a GET endpoint at the root URL ("/")
async def read_root():  # Async function to handle requests to the root URL
    return {"Hello": "World"}  # Return a simple JSON response

@app.post("/")
async def create_item(item: dict):  # Async function to handle POST requests to the root URL, expects a JSON body parsed into a dictionary
    return {"item_received": item}  # Return the received item in the response

# TEST endpoint to verify environment variable loading

@app.get("/whoami")
async def who_am_i(user=Depends(auth_middleware)):
    return user

if __name__ == "__main__": # If this script is run directly (not imported as a module)
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Start the Uvicorn server to run the FastAPI app on all interfaces at port 8000(default FastAPI port)
