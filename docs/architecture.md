ramy_chatbot/
├── .env                              # Environment variables for local/production
├── config.yaml                       # Global configuration settings (YAML)
├── docker-compose.yml                # Compose file for MongoDB, Redis, FastAPI, etc.
├── Dockerfile                        # Docker build instructions for the FastAPI app
├── requirements.txt                  # Python dependencies
├── README.md                         # Project overview, setup, and usage instructions
├── start.sh                          # Startup script for local or production
├── .github/                        
│   └── workflows/                    # GitHub Actions workflows for CI/CD
│       └── ci-cd.yml                 # CI/CD pipeline configuration
│
├── docker/                           # Docker-specific resources
│   ├── Dockerfile                    # Alternate/service-specific Dockerfile(s)
│   ├── docker-compose.yml            # Multi-container deployment config (for production)
│   └── scripts/                      # Docker entrypoint and setup scripts
│       ├── start.sh                  # Container startup script for production
│       └── setup.sh                  # Initial setup and migration tasks
│
├── src/                              # Application source code
│   ├── __init__.py
│   ├── main.py                       # FastAPI application entry point
│   │
│   ├── api/                        # API endpoints, versioning, and middleware
│   │   ├── __init__.py
│   │   ├── dependencies.py         # Dependency injection (DB, cache, etc.)
│   │   ├── middlewares.py          # Security, rate limiting, CORS, etc.
│   │   └── v1/                     # Versioned API endpoints
│   │       ├── __init__.py
│   │       ├── chat.py             # Chatbot endpoint integrating LLM, RAG, caching, and Pydantic validation for results
│   │       ├── health.py           # Health check endpoint
│   │       └── user.py             # User management endpoints
│   │
│   ├── core/                       # Core business logic and orchestration
│   │   ├── __init__.py
│   │   ├── config.py               # Loads settings from YAML and .env
│   │   ├── decision_manager.py     # Chatbot decision logic (with Pydantic validation) and caching integration
│   │   ├── llm.py                  # LLM and RAG pipelines with prompt management
│   │   ├── cache.py                # Caching abstraction (supports Redis or in-memory)
│   │   └── enums.py                # Enums for log levels, error codes, statuses, etc.
│   │
│   ├── db/                         # Database operations (MongoDB)
│   │   ├── __init__.py
│   │   ├── connection.py           # MongoDB connection logic (Docker-ready)
│   │   ├── models.py               # MongoDB/Pydantic models and schemas
│   │   ├── crud.py                 # CRUD operations for data management (e.g., saving chatbot results)
│   │   └── migrations/             # Database migration scripts (if needed)
│   │
│   ├── logging/                    # Logging, monitoring, and alerting systems
│   │   ├── __init__.py
│   │   ├── logger.py               # Logger configuration (file & DB logging)
│   │   ├── monitor.py              # Application performance and health monitoring
│   │   └── alerts.py               # Alerting mechanisms for errors and warnings
│   │
│   ├── schemas/                    # Pydantic models for request/response validation
│   │   ├── __init__.py
│   │   ├── chatbot_schema.py       # Schemas for validating chatbot messages and responses
│   │   ├── logs_schema.py          # Schemas for logging events
│   │   └── user_schema.py          # Schemas for user data and authentication
│   │
│   ├── services/                   # External integrations and notifications
│   │   ├── __init__.py
│   │   ├── whatsapp.py             # WhatsApp Business API integration
│   │   └── email_notifications.py  # Email notifications integration (optional)
│   │
│   ├── utils/                      # Utility functions and shared constants
│   │   ├── __init__.py
│   │   ├── helpers.py              # General helper functions
│   │   └── constants.py            # Global constants and configuration defaults
│   │
│   └── caches/                     # Dedicated caching implementation
│       ├── __init__.py
│       ├── cache_manager.py        # Central cache management (e.g., Redis abstraction)
│       └── redis_client.py         # Redis client and connection helper methods
│
├── logs/                           # Persistent log storage (rotated/log files)
│   └── app.log                     # Application log file
│
├── scripts/                        # Deployment and automation scripts
│   ├── start.sh                    # Production startup script
│   └── setup.sh                    # Initial setup script for first-time deployments
│
├── docs/                           # Documentation and technical guides
│   ├── architecture.md             # System architecture and design details
│   └── api_endpoints.md            # Detailed API endpoint documentation
│
└── tests/                          # Unit, integration, and end-to-end tests
    ├── __init__.py
    ├── test_api.py                 # API endpoint tests (chat, health, user, etc.)
    ├── test_db.py                  # Tests for database CRUD operations and models
    ├── test_decision_manager.py    # Business logic, caching, and Pydantic validation tests
    └── test_llm.py                 # Tests for LLM and RAG pipeline integrations
