# OFT Transacts

A modern financial transaction management system built with FastAPI and Vue.js. OFT Transacts provides a secure, user-friendly interface for managing accounts, tracking transactions, and monitoring balances with real-time calculations.

## 🚀 Features

- **Account Management**: Create and manage multiple financial accounts with different currencies
- **Transaction Tracking**: Record credits and debits with detailed notes and timestamps
- **Real-time Balance Calculations**: Automatic balance computation using checkpoint-based architecture
- **Multi-currency Support**: Handle accounts in different currencies (USD, EUR, GBP, etc.)
- **Secure Authentication**: OpenID Connect (OIDC) integration with PKCE flow
- **Modern UI**: Responsive Vue 3 frontend with Tailwind CSS
- **RESTful API**: FastAPI backend with automatic OpenAPI documentation

## 🏗️ Architecture

This is a monorepo containing isolated frontend and backend projects with separate build steps, enabling coordinated releases and easy separation if needed.

```
oft_transacts/
├── backend/          # FastAPI application
│   ├── migrations/   # Database schema and seeds
│   └── src/          # Python source code
└── frontend/         # Vue 3 application
    └── src/          # TypeScript/Vue source code
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** 0.118.0 - Modern Python web framework
- **SQLAlchemy** 2.0.41 - Database ORM
- **Pydantic** 1.10.24 - Data validation
- **python-jose** - JWT/OIDC token verification
- **uvicorn** - ASGI server
- **SQLite** - Database (easily swappable for PostgreSQL)

### Frontend
- **Vue 3** - Progressive JavaScript framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **TanStack Query** - Data fetching and caching
- **Tailwind CSS** - Utility-first CSS framework
- **oidc-client-ts** - OIDC authentication

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python** 3.12 or higher
- **Node.js** 18.0 or higher
- **npm** or **pnpm**
- **Git**
- An **OIDC provider** account (Okta, Auth0, Keycloak, etc.)

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-ORG/oft_transacts.git
cd oft_transacts
```

### 2. Backend Setup

#### Create Virtual Environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cp .env.example .env
```

Edit `backend/.env` with your configuration (see [Configuration](#-configuration) section).

#### Initialize Database

```bash
# Create the database directory
mkdir -p var

# Run migrations
sqlite3 var/oft.sqlite3 < migrations/oft_schema.sql

# (Optional) Load seed data
sqlite3 var/oft.sqlite3 < migrations/seed.sql
```

#### Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment Variables

Create a `.env` file in the `frontend/` directory:

```bash
cp .env.example .env
```

Edit `frontend/.env` with your configuration (see [Configuration](#-configuration) section).

#### Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## ⚙️ Configuration

### Backend Configuration (`backend/.env`)

```bash
# Database URL
DATABASE_URL=sqlite:///backend/var/oft.sqlite3
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/oft_transacts

# OIDC Configuration (Required)
OIDC_ISSUER=https://your-tenant.okta.com/oauth2/default
OIDC_AUDIENCE=                  # Optional: API identifier if required

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:4173

# Pagination
TRANSACTS_PAGE_SIZE=10
```

### Frontend Configuration (`frontend/.env`)

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# OIDC Configuration (Required)
VITE_OIDC_ISSUER=https://your-tenant.okta.com/oauth2/default
VITE_OIDC_CLIENT_ID=your_spa_client_id
```

## 🔐 OIDC Setup

This application uses OpenID Connect (OIDC) with the PKCE flow for secure authentication. You'll need to configure an OIDC provider:

### Supported Providers
- Okta
- Auth0
- Keycloak
- Azure AD
- Google Identity Platform
- Any OIDC-compliant provider

### Configuration Steps

1. **Create an Application** in your OIDC provider
   - Application Type: **Single Page Application (SPA)**
   - Grant Type: **Authorization Code with PKCE**

2. **Configure Redirect URIs**
   - Login Redirect: `http://localhost:5173/signin-callback`
   - Logout Redirect: `http://localhost:5173/`
   - For production, add your production URLs

3. **Note Your Configuration**
   - Issuer URL (e.g., `https://your-tenant.okta.com/oauth2/default`)
   - Client ID

4. **Set Scopes**
   - Minimum required: `openid profile email`

5. **Update Environment Variables**
   - Backend: Set `OIDC_ISSUER` and optionally `OIDC_AUDIENCE`
   - Frontend: Set `VITE_OIDC_ISSUER` and `VITE_OIDC_CLIENT_ID`

### Example: Okta Setup

1. Go to **Applications** → **Create App Integration**
2. Select **OIDC** and **Single-Page Application**
3. Set Sign-in redirect URIs to `http://localhost:5173/signin-callback`
4. Set Sign-out redirect URIs to `http://localhost:5173/`
5. Copy the **Client ID** and **Issuer URL**
6. Update your `.env` files

### Example: Auth0 Setup

1. Go to **Applications** → **Create Application**
2. Select **Single Page Web Applications**
3. Set Allowed Callback URLs to `http://localhost:5173/signin-callback`
4. Set Allowed Logout URLs to `http://localhost:5173/`
5. Set Allowed Web Origins to `http://localhost:5173`
6. Copy the **Domain** (use as `https://{domain}` for issuer) and **Client ID**
7. Update your `.env` files

## 📊 Database Schema

The application uses a checkpoint-based balance calculation system:

### Tables

- **users**: User accounts with email and username
- **accounts**: Financial accounts with checkpoint balances
- **transacts**: Individual transactions (credits/debits)

### Key Concepts

- **Checkpoint Balance**: A known balance at a specific timestamp
- **Computed Balance**: Checkpoint + sum of transactions after checkpoint
- **Transaction Status**: `posted` or `deleted` (soft delete)

## 🧪 Development

### Backend Development

```bash
# Run with auto-reload
cd backend
uvicorn app.main:app --reload

# Type checking
mypy app/

# Code formatting
black app/
ruff check app/
```

### Frontend Development

```bash
# Development server
npm run dev

# Type checking
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🏗️ Building for Production

### Backend

```bash
cd backend
pip install -r requirements.txt

# Set production environment variables
export DATABASE_URL="postgresql://..."
export OIDC_ISSUER="https://..."
export ALLOWED_ORIGINS="https://your-domain.com"

# Run with gunicorn or uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend

```bash
cd frontend
npm run build

# Serve the dist/ directory with your web server
# Example with nginx, apache, or cloud hosting
```

## 📚 API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `GET /accounts` - List user's accounts
- `POST /accounts` - Create new account
- `GET /accounts/{id}/transacts` - Get transactions for account
- `POST /transacts` - Create transaction
- `PATCH /transacts/{id}` - Update transaction
- `DELETE /transacts/{id}` - Soft delete transaction

## 🔒 Security

- All API endpoints require valid OIDC JWT authentication
- CORS is configured to allow only specified origins
- CSP headers are enforced
- SQLite foreign keys are enabled
- Input validation via Pydantic schemas
- Secure defaults for all configurations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Vue.js team for the reactive framework
- All contributors who help improve this project

## 📞 Support

If you have any questions or need help, please:
- Open an issue on GitHub
- Check existing documentation
- Review the API documentation at `/docs`