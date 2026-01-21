# ABG Digital Asset Management System

![ABG Logo](https://img.shields.io/badge/Autonomous%20Region%20of-Bougainville%20Government-blue?style=for-the-badge&logo=gov&logoColor=white)

A comprehensive Digital Asset Management (DAM) system designed specifically for the **Autonomous Region of Bougainville Government** to securely manage, store, and distribute digital assets including documents, archives, and media files.

## 🎯 **About ABG**

The Autonomous Region of Bougainville (ABG) is a government entity in Papua New Guinea responsible for managing regional affairs. This DAM system provides a secure, professional platform for government officials to manage digital archives and assets with appropriate classification levels and access controls.

## ✨ **Key Features**

### 🔐 **Security & Access Control**
- **Role-Based Access Control**: Admin, Archivist, Regular, and Viewer roles
- **Asset Classification**: Public, Regular, and Confidential security levels
- **Secure Authentication**: JWT-based authentication with session management
- **Audit Logging**: Complete tracking of all user actions and asset access

### 📁 **Asset Management**
- **Multi-format Support**: Documents, images, videos, audio, and archives
- **Metadata Management**: Rich metadata with tags, descriptions, and custom fields
- **Search & Filtering**: Full-text search with advanced filtering options
- **Bulk Operations**: Upload multiple files with batch processing

### 🎨 **Professional Interface**
- **ABG Government Branding**: Official colors, logo, and professional styling
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Modern UI/UX**: Clean, intuitive interface designed for government use
- **Accessibility**: WCAG-compliant design for inclusive access

### 🔧 **Technical Features**
- **RESTful API**: Complete API with automatic OpenAPI documentation
- **Database Migrations**: Alembic-powered schema management
- **File Storage**: Secure local filesystem storage with thumbnail generation
- **Background Processing**: Asynchronous task processing for uploads

## 🛠️ **Technology Stack**

- **Backend**: FastAPI (Python 3.8+)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy with Alembic migrations
- **Authentication**: JWT tokens with scrypt password hashing
- **Frontend**: Jinja2 templates with responsive CSS
- **API Documentation**: Automatic OpenAPI/Swagger docs
- **Deployment**: Uvicorn ASGI server

## 🚀 **Quick Start**

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ABG.git
   cd ABG
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=sqlite:///./dam.db
   SECRET_KEY=your-super-secret-key-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Initialize the database**
   ```bash
   # Run migrations
   alembic upgrade head

   # Seed with sample data (optional)
   python seed.py
   ```

6. **Start the server**
   ```bash
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

7. **Access the application**
   - **Web Interface**: http://127.0.0.1:8000
   - **API Documentation**: http://127.0.0.1:8000/docs
   - **Admin Login**: username: `admin`, password: `admin123`

## 📊 **Default Users**

After running `seed.py`, the following users are available:

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `admin` | `admin123` | Admin | Full system access |
| `archivist` | `archive123` | Archivist | Can upload and manage assets |
| `user` | `user123` | Regular | Standard user access |
| `viewer` | `view123` | Viewer | Read-only access |

## 🏗️ **Project Structure**

```
ABG/
├── app/                    # Main application package
│   ├── main.py            # FastAPI application and routes
│   ├── database.py        # Database configuration
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── crud.py            # Database operations
│   └── routers/           # API route modules
│       └── api.py         # REST API endpoints
├── templates/             # Jinja2 HTML templates
│   ├── index.html         # Home page
│   ├── login.html         # Authentication page
│   ├── assets.html        # Asset library
│   ├── upload.html        # File upload interface
│   ├── reports.html       # Analytics dashboard
│   └── settings.html      # User settings
├── static/                # Static assets (CSS, JS, images)
├── uploads/               # File storage directory
├── alembic/               # Database migrations
├── requirements.txt       # Python dependencies
├── seed.py               # Database seeding script
├── .env                  # Environment variables (create this)
└── README.md             # This file
```

## 🔒 **Security Features**

- **Password Hashing**: scrypt algorithm for secure password storage
- **JWT Authentication**: Stateless token-based authentication
- **Session Management**: Secure server-side session handling
- **Access Control**: Granular permissions based on user roles
- **File Validation**: Secure file upload with type and size validation
- **Audit Trail**: Complete logging of all system activities

## 📈 **API Endpoints**

### Authentication
- `POST /api/token` - Obtain access token
- `POST /login` - Web login
- `POST /logout` - Web logout

### Assets
- `GET /api/assets/` - List assets
- `POST /api/upload/` - Upload new asset
- `GET /api/assets/{id}` - Get asset details
- `GET /api/download/{id}` - Download asset

### Users
- `POST /api/users/` - Create user
- `GET /api/users/me/` - Get current user

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is proprietary software developed for the Autonomous Region of Bougainville Government.

## 📞 **Support**

For technical support or questions about this system, please contact the ABG IT Department.

---

**Built with ❤️ for the Autonomous Region of Bougainville Government**

5. Seed the database (optional):
   ```
   python -m app.seed
   ```

6. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

7. Open http://localhost:8000 in your browser.

## Usage

- Register/Login as user
- Upload assets with metadata
- Search and filter assets
- Manage users and permissions (Admin only)

## Security Notes

- All file access is through the API, no direct paths
- Permissions checked server-side
- Audit logs for all actions
- Use HTTPS in production
- Store SECRET_KEY securely

## Future Improvements

- S3/NAS storage abstraction
- Video thumbnail generation
- Advanced search with Elasticsearch
- Mobile app integration
- Bulk operations