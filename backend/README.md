ai_hiring_system/
│
├── app/                              # 🔹 Main application package
│   ├── __init__.py                   # Initializes the app
│   ├── main.py                       # Entry point (starts the backend server)
│   │
│   ├── api/                          # 🔸 API routes / endpoints
│   │   ├── __init__.py
│   │   ├── employer_routes.py        # Employer registration + questionnaire
│   │   ├── candidate_routes.py       # Resume uploads, etc.
│   │   ├── interview_routes.py       # AI interview endpoints
│   │   └── report_routes.py          # Report download / status
│   │
│   ├── core/                         # 🔸 Core system logic
│   │   ├── __init__.py
│   │   ├── config.py                 # App-level configurations
│   │   └── utils.py                  # Common helper functions
│   │
│   ├── models/                       # 🔸 Data models (DB or schema)
│   │   ├── __init__.py
│   │   ├── employer_model.py
│   │   ├── candidate_model.py
│   │   ├── questionnaire_model.py
│   │   └── interview_model.py
│   │
│   ├── services/                     # 🔸 Business logic modules
│   │   ├── __init__.py
│   │   ├── resume_screening.py       # NLP & scoring for resumes
│   │   ├── ai_interview.py           # AI interview question/answer system
│   │   ├── report_generator.py       # PDF creation
│   │   └── matching_engine.py        # Core AI matching algorithm
│   │
│   ├── database/                     # 🔸 Database layer
│   │   ├── __init__.py
│   │   ├── db_connection.py          # Handles DB setup (e.g. PostgreSQL)
│   │   └── db_queries.py             # CRUD functions
│   │
│   └── static/                       # For frontend assets or uploaded resumes
│       ├── uploads/                  # Uploaded resumes / audio files
│       └── reports/                  # Generated reports (PDFs)
│
├── tests/                            # ✅ Automated tests
│   ├── test_resume_screening.py
│   ├── test_interview_module.py
│   └── test_api_routes.py
│
├── scripts/                          # 🧩 Utility scripts (optional)
│   ├── init_db.py                    # Initialize database tables
│   ├── generate_mock_data.py         # Create fake resumes for testing
│   └── benchmark_ai.py               # Test AI performance
│
├── .env                              # 🔐 Environment variables (API keys, DB creds)
├── requirements.txt                  # 📦 Python dependencies
├── README.md                         # 📘 Project documentation
├── run.py                            # ▶️ Start the system (shortcut to app/main.py)
└── pyproject.toml / setup.py         # 📦 Packaging configuration



| Folder               | Purpose                                                     |
| -------------------- | ----------------------------------------------------------- |
| **app/api/**         | REST endpoints for your frontend or portal                  |
| **app/core/**        | App-wide configs and helper tools                           |
| **app/models/**      | Defines data structure (e.g. candidates, employers)         |
| **app/services/**    | AI logic, NLP models, scoring algorithms                    |
| **app/database/**    | Database connection and queries                             |
| **app/static/**      | Stores user uploads and generated files                     |
| **tests/**           | Unit & integration tests                                    |
| **scripts/**         | Reusable scripts for setup/testing                          |
| **requirements.txt** | All library dependencies (FastAPI, OpenAI, reportlab, etc.) |
| **run.py**           | Quick launcher                                              |
| **.env**             | Keeps sensitive info safe and separate from code            |
| **README.md**        | Explains how to run and what it does                        |


--Backend and frontend seperate and will be deployed separately 
