# Authentication Microservice (FastAPI)

This project is a **JWT-based Authentication and User Management Microservice** built with **FastAPI, SQLAlchemy, and OAuth2**.
It is designed as part of a **Final Year Project (FYP)** to provide secure authentication for other services in a microservice architecture.

The service handles:

* User registration
* User login
* JWT token generation
* Token verification
* User management (CRUD)
* Role-based user data

---

# Features

* Secure password hashing using **bcrypt**
* JWT authentication using **OAuth2**
* Token verification endpoint
* User CRUD operations
* SQLite database using **SQLAlchemy ORM**
* Environment variable configuration using **python-dotenv**

---

# Tech Stack

* **Backend:** FastAPI
* **Database:** SQLite
* **ORM:** SQLAlchemy
* **Authentication:** OAuth2 + JWT
* **Password Hashing:** Passlib (bcrypt)
* **Environment Management:** python-dotenv

---

# Project Structure

```
Authentication/
│
├── main.py          # FastAPI application and API routes
├── Model.py         # SQLAlchemy models and Pydantic schemas
├── util.py          # Authentication utilities (JWT, hashing, token verification)
├── .env             # Environment variables (NOT included in repo)
├── requirements.txt
└── README.md
```

---

# Installation

### 1 Clone the repository

```
git clone https://github.com/Kashif-alamshah/AuthenticationFYP.git
cd AuthenticationFYP
```

### 2 Create a virtual environment

```
python -m venv auth
```

Activate the environment:

Windows

```
auth\Scripts\activate
```

Linux / Mac

```
source auth/bin/activate
```

---

### 3 Install dependencies

```
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the root directory:

```
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DB_URL=sqlite:///./auth.db
```

⚠️ **Important:** Never commit `.env` to GitHub.

---

# Running the Application

Start the FastAPI server:

```
uvicorn main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

Interactive documentation:

```
http://127.0.0.1:8000/docs
```

---

# API Endpoints

## Authentication

### Register User

```
POST /register
```

### Login (Generate JWT Token)

```
POST /token
```

### Verify Token

```
GET /verify-token
```

---

## User Management

### Get Current User Profile

```
GET /profile
```

### Get All Users

```
GET /users/
```

### Get User by ID

```
GET /users/{user_id}
```

### Update User

```
PUT /users/{user_id}
```

### Delete User

```
DELETE /users/{user_id}
```

---

# Example Authentication Flow

1. Register a user

```
POST /register
```

2. Login to receive JWT token

```
POST /token
```

3. Use token in requests

```
Authorization: Bearer <your_token>
```

---

# Security Features

* Passwords are hashed using **bcrypt**
* Authentication is handled using **OAuth2 password flow**
* JWT tokens include expiration timestamps
* Protected endpoints require a valid bearer token

---

# Future Improvements

* Role-Based Access Control (RBAC)
* PostgreSQL integration
* Refresh tokens
* Rate limiting
* Docker containerization
* Microservice deployment

---

# Author

**Kashif Alam**
Software Engineering Student
Bahria University Karachi

Interested in **Artificial Intelligence, Machine Learning, and AI Engineering**.

---

# License

This project is for **educational and research purposes**.
