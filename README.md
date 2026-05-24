# Instagram Final Project API

A production-inspired Instagram-like social media backend built with Django, Django REST Framework, PostgreSQL, Redis, Celery, and Docker.

This project simulates core backend functionality of a modern social media platform including authentication, profiles, posts, stories, interactions, direct messaging, search, and asynchronous task processing.

---

## Features

### Authentication
- OTP-based authentication (email / phone)
- JWT authentication
- Secure OTP generation
- OTP expiration and cooldown handling
- Phone number validation
- Email validation
- Asynchronous OTP delivery via Celery

### User Profiles
- Automatic profile creation using Django signals
- Profile retrieval and update
- Avatar / bio / display name support
- Follow / unfollow functionality
- Followers / following relationships

### Posts
- Create / retrieve / update / delete posts
- Soft delete support
- Public / followers-only visibility
- Hashtag extraction and synchronization
- Saved posts
- Like / unlike functionality
- Comment system with nested replies
- Comment count tracking

### Stories
- Story creation
- Story feed based on following relationships
- Story expiration handling
- Visibility rules
- Media support

### Social Interactions
- Likes
- Saves
- Comments
- Nested replies
- Access control based on visibility and relationships

### Search
- User search
- Hashtag search
- Optimized queryset usage

### Direct Messaging
- One-to-one conversations
- Conversation creation
- Inbox listing
- Message history retrieval
- Canonical conversation pairing

### Background Processing
Powered by Celery + Redis:

- Asynchronous OTP delivery
- Task queue processing

### API Documentation
Interactive API documentation powered by DRF Spectacular / Swagger OpenAPI.

---

## Tech Stack

### Backend
- Python
- Django
- Django REST Framework

### Database
- PostgreSQL

### Task Queue / Broker
- Celery
- Redis

### DevOps
- Docker
- Docker Compose

### Authentication
- JWT
- OTP Authentication

---

## Project Architecture
```text
           Client
              |
              v
      Django REST API
              |
      +-------+--------+
      |       |        |
      v       v        v
 PostgreSQL  Redis    Celery
   (data)   (broker) (background tasks)

```

## Project Structure
```text
instagram/
├── accounts/
├── posts/
├── interactions/
├── stories/
├── direct/
├── config/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py

```

## Local Development Setup

### Prerequisites

Make sure the following are installed:

- Docker
- Docker Compose

---

### Clone Repository
```bash
git clone <your-repository-url>
cd instagram
```
---

### Environment Variables

Create:
```bash
cp .env.example .env
```

Example:
```env
SECRET_KEY=
DEBUG=True

DB_NAME=instagram_db
DB_USER=instagram_user
DB_PASSWORD=
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/1

KAVENEGAR_API_KEY=
KAVENEGAR_SENDER=
```

---

### Build Containers
```bash
docker compose build
```

### Start Services
```bash
docker compose up
```

Detached mode:
```bash
docker compose up -d
```

### Run Migrations
```bash
docker compose exec web python manage.py migrate
```

### Create Superuser
```bash
docker compose exec web python manage.py createsuperuser
```

---

## Development Commands

### Make Migrations
```bash
docker compose exec web python manage.py makemigrations
```

### Django Shell
```bash
docker compose exec web python manage.py shell
```

### Run Tests
```bash
docker compose exec web python manage.py test
```

### View Logs

All services:
```bash
docker compose logs -f
```

Specific services:
```bash
docker compose logs -f web
docker compose logs -f celery
docker compose logs -f db
```

### Stop Services
```bash
docker compose down
```

### Rebuild Containers
```bash
docker compose up --build
```

---

## API Access

Application:
```text
http://localhost:8000
```

Swagger UI:
```text
http://localhost:8000/api/schema/swagger-ui/
```

---

## Core API Domains

### Authentication
- OTP request
- OTP verification
- JWT token generation

### Profiles
- Profile retrieval
- Profile update
- Followers / following

### Posts
- CRUD operations
- Like / unlike
- Save / unsave

### Comments
- Nested replies
- Hashtag support

### Stories
- Create stories
- Story feed

### Direct Messaging
- Conversation list
- Conversation detail
- Send messages

---

## Security Notes

Current implementation includes:

- environment-based configuration
- JWT authentication
- OTP expiration handling
- Dockerized isolated development environment
- asynchronous task separation

Potential production improvements:

- Gunicorn
- Nginx
- HTTPS / TLS
- Docker healthchecks
- CI/CD pipeline
- object storage for media
- rate limiting
- centralized logging

---

## Learning Outcomes

This project demonstrates practical experience with:

- REST API design
- Django REST Framework architecture
- serializer design
- queryset optimization
- authentication flows
- asynchronous task processing
- Redis integration
- PostgreSQL integration
- Dockerized development workflows
- API documentation

---

## Author

Matin Fekri  
Backend Developer — Django / DRF
