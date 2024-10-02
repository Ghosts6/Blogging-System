![baner](https://github.com/Ghosts6/Local-website/blob/main/img/Baner.png)

# 📝 Blogging System
Welcome to the Blogging System! This project allows users to create, manage, and interact with articles. It features user authentication, article management, and a powerful API built with Django and FastAPI.

## 🚀 Features
- **User Authentication**: Sign up, log in, and manage user profiles securely.
- **Article Management**: Create, read, update, and delete articles with tags and publication dates.
- **Filter Articles**: Filter articles by publishing date and tags for better discoverability.
- **FastAPI Integration**: FastAPI provides a lightweight and high-performance API for article interactions.
- **Password Management**: Forgot password functionality with secure reset tokens.
- **Admin Panel**: A Django admin interface for managing users and articles efficiently.

## 🛠️ Technologies Used
- **Django**: Web framework for building the application and handling backend logic.
- **FastAPI**: For building a fast and efficient RESTful API.
- **Django REST Framework**: To extend Django’s capabilities for building APIs.
- **Redis**: Used for caching and session management, improving performance.
- **PostgreSQL**: The database used for storing user and article data.
- **Python venv**: For managing project dependencies in an isolated environment.
- **Celery**: Distributed task queue used for handling asynchronous tasks such as background jobs and scheduled tasks, integrated with Redis as a message broker.

## ⚙️ Configuration
### Logging
- Configured to log messages to both the console and a file (`debug.log`) for easy debugging and monitoring.

### Caching
- Redis is configured as the cache backend to store frequently accessed data, speeding up response times and reducing database load.

### User Model
- A custom user model (`CustomUser`) extends the default Django user model, enabling additional features while avoiding conflicts.

## 📦 Getting Started
1. Clone the repository:
   ```bash
   git clone https://github.com/Ghosts6/Blogging-System
   cd blogging_system
   ```
2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate 
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run Redis server separately (ensure Redis is installed):
   ```bash
   redis-server
   ```
5. Apply migrations:
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```
6. Collect static files:
   ```
   python3 manage.py collectstatic
   ```
7. Run the Django development server:
   ```bash
   python3 manage.py runserver # on port 8000 & redis on port 6379
   python3 manage.py runfastapi # on port 8001
   ```
8. Access the FastAPI documentation at http://127.0.0.1:8001/docs or http://127.0.0.1:8001/redoc to interact with the API.

## 💬 Contributing
Contributions are welcome! Feel free to submit a pull request or create an issue to discuss improvements.
