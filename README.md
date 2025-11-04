![baner](https://github.com/Ghosts6/Local-website/blob/main/img/Baner.png)

# 📝 Blogging System
Welcome to the Blogging System! This project allows users to create, manage, and interact with articles. It features user authentication, article management, and a powerful API built with Django and FastAPI.

## 🚀 Features
- **User Authentication**: Sign up, log in, and manage user profiles securely.
- **Article Management**: Create, read, update, and delete articles with tags and publication dates.
- **Advanced Article Features**: Articles can be saved as drafts, published, and have cover images.
- **User Profiles**: Users have profiles with a bio, website, and profile picture.
- **API Improvements**: The API now supports pagination, filtering (by author, category, and tags), and searching (in title and content).
- **FastAPI Integration**: FastAPI provides a lightweight and high-performance API for article interactions.
- **Password Management**: Forgot password functionality with secure reset tokens.
- **Health Check and Diagnostics**: Endpoints to monitor the service's health and view application diagnostics.

## 🛠️ Technologies Used
- **Django**: Web framework for building the application and handling backend logic.
- **FastAPI**: For building a fast and efficient RESTful API.
- **Docker**: For containerizing the application and its services.
- **Django REST Framework**: To extend Django’s capabilities for building APIs.
- **Redis**: Used for caching and session management, improving performance.
- **PostgreSQL**: The database used for storing user and article data.
- **Celery**: Distributed task queue used for handling asynchronous tasks such as background jobs and scheduled tasks, integrated with Redis as a message broker.

## ⚙️ Configuration
### Logging
- Configured to log messages to both the console and a file (`debug.log`) for easy debugging and monitoring.

### Caching
- Redis is configured as the cache backend to store frequently accessed data, speeding up response times and reducing database load.

### User Model
- A custom user model (`CustomUser`) extends the default Django user model, and a `Profile` model is linked to it.

## 🗺️ API Endpoints
Here are the main API endpoints:

### User Authentication
- `POST /signup/`: Register a new user.
- `POST /login/`: Authenticate a user and get an access token.
- `POST /password-reset-request/`: Request a password reset token.
- `POST /password-reset-confirm/`: Confirm password reset with a token and new password.

### Articles
- `GET /articles/`: Retrieve a list of articles with optional pagination, filtering, and searching.
- `POST /articles/`: Create a new article (requires authentication).
- `GET /articles/{article_id}/`: Retrieve a specific article.
- `PUT /articles/{article_id}/`: Update an existing article (requires authentication and ownership).
- `DELETE /articles/{article_id}/`: Delete an article (requires authentication and ownership).

### Comments
- `POST /articles/{article_id}/comments/`: Add a comment to an article (requires authentication).
- `GET /articles/{article_id}/comments/`: Retrieve comments for a specific article.

### Categories
- `POST /categories/`: Create a new category.
- `GET /categories/`: Retrieve a list of categories.

### FAQs
- `POST /faqs/`: Create a new FAQ (requires authentication).
- `GET /faqs/`: Retrieve a list of FAQs.
- `GET /faqs/{faq_id}/`: Retrieve a specific FAQ.
- `PUT /faqs/{faq_id}/`: Update an existing FAQ (requires authentication and ownership).
- `DELETE /faqs/{faq_id}/`: Delete an FAQ (requires authentication and ownership).

### System
- `GET /health/`: Check the health of the service.
- `GET /diagnostics/`: Get diagnostic information about the application.

## 📦 Getting Started
1. Clone the repository:
   ```bash
   git clone https://github.com/Ghosts6/Blogging-System
   cd Blogging-System
   ```
2. Create a `.env` file based on the `docker-compose.yml` file and fill in the required environment variables.
3. Build and run the Docker containers:
   ```bash
   docker-compose up --build -d
   ```
4. Access the FastAPI documentation at http://127.0.0.1:8001/docs or http://127.0.0.1:8001/redoc to interact with the API.

## 💬 Contributing
Contributions are welcome! Feel free to submit a pull request or create an issue to discuss improvements.
