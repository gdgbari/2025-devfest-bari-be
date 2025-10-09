# DevFest Bari 2025 - Backend API

User management API built with FastAPI, Firebase Auth, and Firestore, following Domain-Driven Design (DDD) principles and Clean Architecture patterns.

## Architecture Overview

This project follows **Domain-Driven Design (DDD)** with Clean Architecture principles, ensuring separation of concerns, maintainability, and testability.

### Layer Structure

```
/app
├── api/                          # Presentation Layer
│   ├── routers/                  # HTTP endpoints (FastAPI routers)
│   │   ├── health/              # Health check endpoints
│   │   └── users/               # User management endpoints
│   ├── schemas/                  # Request/Response models (Pydantic)
│   │   └── users/               # User-related schemas
│   ├── adapters/                 # Data transformation adapters
│   │   └── users/               # User data adapters
│   ├── dependencies.py           # FastAPI dependency injection
│   └── include_routers.py        # Router registration
│
├── domain/                       # Domain Layer (Business Logic)
│   ├── entities/                 # Domain entities
│   │   └── user.py              # User domain entity
│   └── services/                 # Domain services (business logic)
│       └── user_service.py      # User business operations
│
├── infrastructure/               # Infrastructure Layer (External Systems)
│   ├── clients/                  # External service clients
│   │   ├── firebase_auth_client.py  # Firebase Auth SDK wrapper
│   │   └── firestore_client.py      # Firestore SDK wrapper
│   ├── repositories/             # Data access repositories
│   │   ├── auth_repository.py   # Firebase Auth operations
│   │   └── user_repository.py   # Firestore user operations
│   └── errors/                   # Infrastructure error handling
│       ├── auth_errors.py       # Authentication errors
│       ├── firestore_errors.py  # Firestore errors
│       └── user_errors.py       # User-related errors
│
├── core/                         # Core Layer (Shared Kernel)
│   ├── settings.py              # Application settings
│   ├── logging.py               # Logging configuration
│   ├── middleware.py            # FastAPI middleware
│   └── security.py              # Security utilities
│
├── secrets/                      # Sensitive configuration files
│   └── service_account_key.json # Firebase service account key
│
├── main.py                       # Application entry point
├── requirements.txt              # Python dependencies
└── env-template                  # Environment variables template
```

## Clean Architecture Principles

### 1. **Dependency Rule**
Dependencies flow inward: `API → Domain ← Infrastructure`

- **Domain Layer** has no dependencies (pure business logic)
- **Infrastructure Layer** depends on Domain
- **API Layer** depends on Domain and uses Infrastructure through dependency injection

### 2. **Separation of Concerns**

- **Routers**: Handle HTTP requests/responses
- **Schemas**: Validate and serialize API data (DTOs)
- **Adapters**: Transform between schemas and domain entities
- **Entities**: Pure domain models with business logic
- **Services**: Orchestrate domain operations
- **Repositories**: Abstract data persistence
- **Clients**: Wrap external service SDKs

### 3. **Dependency Injection**

All dependencies are injected via FastAPI's dependency injection system using `@lru_cache()` for singletons:

```python
# Clients (Singleton)
@lru_cache()
def get_auth_client() -> FirebaseAuthClient

# Repositories
def get_auth_repository(auth_client: FirebaseAuthClient) -> AuthRepository

# Services
def get_user_service(repositories...) -> UserService
```

## Technology Stack

- **FastAPI**: Modern Python web framework
- **Firebase Authentication**: User authentication and identity management
- **Firestore**: NoSQL document database
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server

## Getting Started

### Prerequisites

- Python 3.9+
- Firebase project with Authentication and Firestore enabled
- Firebase service account key

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd 2025-devfest-bari-be
```

2. **Install dependencies**

```bash
pip install -r app/requirements.txt
```

3. **Configure Firebase**

   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Enable **Authentication** (Email/Password provider)
   - Enable **Firestore Database**
   - Generate a service account key:
     - Go to Project Settings → Service Accounts
     - Click "Generate New Private Key"
     - Save as `/app/secrets/service_account_key.json`

4. **Set environment variables** (optional)

Create a `.env` file in the project root:

```env
FIREBASE_SERVICE_ACCOUNT_PATH=/app/secrets/service_account_key.json
API_ROOT_PATH=/api
VERSION=1.0.0
DEBUG=False
```

### Running the Application

**Development mode:**

```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Production mode:**

```bash
cd app
python main.py
```

The API will be available at: `http://localhost:8000/api`

### Docker Support

```bash
docker-compose up --build
```

## API Documentation

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

### Endpoints

Base URL: `http://localhost:8000/api`

#### 1. Health Check

**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

#### 2. Create User

**POST** `/users`

Creates a new user in Firebase Auth and Firestore.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John",
  "surname": "Doe",
  "nickname": "johndoe"
}
```

**Response:** `201 Created`
```json
{
  "uid": "firebase-generated-uid",
  "email": "user@example.com",
  "name": "John",
  "surname": "Doe",
  "nickname": "johndoe"
}
```

#### 3. Get All Users

**GET** `/users`

Retrieves all users from Firestore.

**Response:** `200 OK`
```json
{
  "users": [
    {
      "uid": "firebase-uid-1",
      "email": "user1@example.com",
      "name": "John",
      "surname": "Doe",
      "nickname": "johndoe"
    }
  ],
  "total": 1
}
```

#### 4. Get User by UID

**GET** `/users/{uid}`

Retrieves a specific user by their UID.

**Response:** `200 OK`
```json
{
  "uid": "firebase-uid",
  "email": "user@example.com",
  "name": "John",
  "surname": "Doe",
  "nickname": "johndoe"
}
```

#### 5. Update User

**PUT** `/users/{uid}`

Updates user information in Firebase Auth and/or Firestore.

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "name": "Jane",
  "surname": "Smith",
  "nickname": "janesmith"
}
```

**Response:** `200 OK`
```json
{
  "uid": "firebase-uid",
  "email": "newemail@example.com",
  "name": "Jane",
  "surname": "Smith",
  "nickname": "janesmith"
}
```

#### 6. Delete User

**DELETE** `/users/{uid}`

Deletes a user from both Firebase Auth and Firestore.

**Response:** `204 No Content`

#### 7. Delete All Users

**DELETE** `/users`

⚠️ **Warning**: Deletes all users from Firebase Auth and Firestore. Use with caution!

**Response:** `204 No Content`

## Data Flow

### Example: Create User Flow

```
1. HTTP Request
   ↓
2. Router (create_user.py)
   ↓
3. Schema Validation (CreateUserRequest)
   ↓
4. Adapter (transform to domain entity)
   ↓
5. UserService (business logic orchestration)
   ↓
6. AuthRepository (create in Firebase Auth)
   ↓
7. UserRepository (create in Firestore)
   ↓
8. Adapter (transform to response schema)
   ↓
9. HTTP Response (CreateUserResponse)
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST request
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `500 Internal Server Error`: Server error

Custom error classes:
- `AuthenticationError`: Firebase Auth errors
- `UserNotFoundError`: User doesn't exist
- `UserAlreadyExistsError`: User already exists
- `DocumentNotFoundError`: Firestore document not found

## Testing

The architecture supports easy testing through dependency injection:

```python
# Example: Mock repository in tests
app.dependency_overrides[get_user_repository] = lambda: MockUserRepository()
```

## Security Considerations

- ✅ Passwords are hashed and managed by Firebase Auth
- ✅ Service account key must be kept secure
- ✅ Firestore security rules should be configured
- ✅ Use HTTPS in production
- ✅ Environment variables for sensitive configuration
- ✅ Input validation via Pydantic schemas

## Project Configuration

### Settings (core/settings.py)

- `FIREBASE_SERVICE_ACCOUNT_PATH`: Path to Firebase service account key
- `API_ROOT_PATH`: API base path (default: `/api`)
- `VERSION`: API version
- `DEBUG`: Debug mode flag

## Firebase Setup

### Authentication Rules

Enable Email/Password authentication in Firebase Console.

### Firestore Structure

**Collection: `users`**

```
users/
  └── {uid}/
      ├── email: string
      ├── name: string
      ├── surname: string
      └── nickname: string
```

### Firestore Security Rules (Example)

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## Development Guidelines

### Adding a New Entity

1. Create domain entity in `domain/entities/`
2. Create repository interface in `domain/repositories/` (if using interfaces)
3. Implement repository in `infrastructure/repositories/`
4. Create service in `domain/services/`
5. Add schemas in `api/schemas/`
6. Create adapters in `api/adapters/`
7. Implement router in `api/routers/`
8. Register dependencies in `api/dependencies.py`
9. Include router in `api/include_routers.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Contact

GDG Bari - DevFest 2025
