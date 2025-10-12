import uvicorn                                          # ASGI server used to run FastAPI apps (like "npm start" for Node)
from fastapi import FastAPI                             # Main FastAPI class used to create the web application instance
from fastapi.middleware.cors import CORSMiddleware      # Middleware to handle CORS (Cross-Origin Resource Sharing) — allows frontend (React, etc.) to communicate with backend
from pydantic import BaseModel                          # Used to define and validate data models (for requests/responses) with type checking
from typing import List                                 # Used to define lists and type hints, e.g., List[str], List[int], etc.
from app.core.config import Settings  # Import the Settings class from the config module to access environment variables
from app.api import rating_resume


app = FastAPI()  # Create FastAPI app instance, This line creates the main application object that will handle all incoming HTTP requests

orgins =[

    "http://localhost:8000"  # Frontend URL, This is the URL of the frontend application (React, etc.) that will communicate with this backend
]


# Include your endpoints
app.include_router(rating_resume.router, prefix="/api", tags=["rating"])

app.add_middleware(
    CORSMiddleware,            # Add CORS middleware to the FastAPI app, This middleware allows the backend to accept requests from the specified origins
    allow_origins=orgins,     # List of allowed origins (frontend URLs)
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

if __name__ == "__main__": # If this script is run directly (not imported as a module)
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Start the Uvicorn server to run the FastAPI app on all interfaces at port 8000(default FastAPI port)