FastAPI Blog Platform

A modern full-stack blog platform built using FastAPI, featuring JWT authentication, async database operations, user management, and blog post interactions.

This project demonstrates backend engineering concepts including:

* REST API development
* Authentication & authorization
* Async database handling
* ORM relationships
* Pydantic validation
* Secure password hashing
* Environment-based configuration

⸻

Features

Authentication

* User registration
* User login
* JWT token authentication
* Password hashing
* Protected routes

Blog Functionality

* Create posts
* Update posts
* Delete posts
* View all posts
* View single post
* User-specific posts

User Features

* User profile handling
* Relationship mapping
* Saved posts functionality

Backend Features

* Async SQLAlchemy integration
* Environment variable configuration
* Pydantic request validation
* Modular project architecture
* Clean API routing structure

⸻

Tech Stack

Backend

* Python
* FastAPI
* SQLAlchemy (Async)
* Pydantic
* JWT Authentication
* Passlib

Database

* PostgreSQL / SQLite

Tools

* Uvicorn
* Alembic
* dotenv

⸻

Project Structure
```bash
.
├── routers/
│   ├── auth.py
│   ├── users.py
│   ├── posts.py
│   └── save_posts.py
├── models.py
├── schemas.py
├── database.py
├── auth.py
├── config.py
├── main.py
├── requirements.txt
└── .env
```
⸻

Installation

##1. Clone the Repository
```bash
git clone https://github.com/yourusername/project-name.git
cd project-name
```
⸻

2. Create Virtual Environment

Linux / macOS
``` bash
python3 -m venv venv
source venv/bin/activate
```
Windows
``` bash
python -m venv venv
venv\Scripts\activate
```
⸻

3. Install Dependencies
```bash
pip install -r requirements.txt
```
⸻

4. Configure Environment Variables

Create a .env file in the root directory.

Example:

DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

⸻

5. Run the Application
```bash
uvicorn main:app --reload
```
Server will start at:

http://127.0.0.1:8000

⸻

API Documentation

FastAPI automatically generates interactive API docs.

Swagger UI

http://127.0.0.1:8000/docs

ReDoc

http://127.0.0.1:8000/redoc

⸻

Authentication Flow

1. Register a new user
2. Login using credentials
3. Receive JWT access token
4. Use token in protected routes

Example Authorization Header:

Authorization: Bearer <your_token>

⸻

Example API Endpoints

## Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Register a user |
| POST | `/login` | Login user |

## Posts

| Method | Endpoint | Description |
|---|---|---|
| GET | `/posts` | Get all posts |
| POST | `/posts` | Create post |
| PUT | `/posts/{id}` | Update post |
| DELETE | `/posts/{id}` | Delete post |

## Users

| Method | Endpoint | Description |
|---|---|---|
| GET | `/users/{id}` | Get user profile |

⸻

Security Features

* Password hashing using Passlib
* JWT token-based authentication
* Environment variable protection
* Input validation with Pydantic
* Protected API routes

⸻

Learning Outcomes

This project helped in understanding:

* Backend architecture
* RESTful API design
* Async programming in Python
* Database relationship management
* Authentication systems
* FastAPI dependency injection
* Clean project structuring

⸻

Future Improvements

* Docker support
* Unit & integration testing
* Role-based access control
* Email verification
* Pagination
* Rate limiting
* CI/CD pipeline
* Caching support
* WebSocket notifications

⸻

Deployment

You can deploy this project on:

* Render
* Railway
* AWS
* DigitalOcean

⸻

Recommended .gitignore

venv/
__pycache__/
.env
*.pyc
.DS_Store

⸻

Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

⸻

Author

Developed as a backend learning project using FastAPI and modern Python backend practices.

⸻

License

This project is licensed under the MIT License.