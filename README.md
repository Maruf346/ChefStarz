# ChefStarz


**Created by:** [Maruf346](https://github.com/Maruf346/ChefStarz)


---

> 🚀 **Getting Started:** For detailed step-by-step setup, database migrations, and deployment commands, please follow the **[DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md)**.

---

## 1. Project Title
- **Project Name:** ChefStarz
- **Description:** [Chef Starz is a fun and safe place where kids can discover the joy of cooking. Explore recipes, try new challenges, and share your delicious creations.]

## 2. Overview
- **Problem Statement:** [Briefly explain what problem this backend solves]
- **Target Consumers:** [e.g., Frontend React App, Mobile Application, Third-party Integrations]
- **Architecture Type:** REST API (Django REST Framework)

## 3. Tech Stack
- **Framework:** Django REST Framework
- **Language:** Python 3.12+
- **Dependency Manager:** [uv](https://docs.astral.sh/uv/)
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose
- **Infrastructure:** Terraform & Ansible (optional)
- **Monitoring:** Prometheus & Grafana (optional)

## 4. Architecture
- **Request Flow:** [Describe high-level request flow from Client -> Nginx -> Gunicorn -> Django]
- **Dependencies:** PostgreSQL, Redis, AWS S3
- **Diagrams:** [Reference architecture diagrams here if available]

## 5. Features
- [ ] JWT Authentication
- [ ] Automated Documentation (Swagger/ReDoc)
- [ ] Scalable App-based Architecture
- [ ] [Add your custom features here]

## 6. Project Structure

The project is divided into several main components, following a modern full-stack backend architecture focused on scalability and infrastructure-as-code.

```text
/
├── backend/                  # REST API Server (Django + DRF)
│   ├── core/                 # Main project configuration (settings, database, middleware)
│   ├── apps/                 # Modular business logic (Authentication, Users, Notifications, etc.)
│   ├── templates/            # Email and administration templates
│   ├── static/               # Source static assets
│   ├── Dockerfile            # Packaging the server environment
│   └── manage.py             # CLI for local server management
├── nginx/                    # Reverse Proxy and Load Balancer
│   └── backend.conf          # Nginx configuration (SSL, Proxy, Static serving)
├── infra/                    # Infrastructure as Code (IaC)
│   ├── terraform/            # Provisions AWS cloud resources (EC2, S3, RDS)
│   └── ansible/              # Automates server configuration and deployments
├── monitoring/               # Metrics collection & Dashboards (optional)
├── .github/                  # CI/CD pipelines (GitHub Actions)
└── README.md                 # Project Overview
```

### Server Folder (`backend/`)
The `backend` directory contains the core application logic. It is built with **Django REST Framework** and is fully containerized. 
- **Core Configuration:** Settings are managed through environment variables (`.env`).
- **Scalability:** Each feature (Users, Recipes, Posts) resides in its own Django App under `apps/` to maintain a clean codebase.
- **Production Grade:** Uses Gunicorn as the WSGI server and Nginx as the reverse proxy for high performance and security.

### Infrastructure (`infra/`)
This project utilizes automated provisioning and configuration:
- **Terraform:** Used for one-click provisioning of the entire AWS environment.
- **Ansible:** Responsible for installing Docker, configuring Nginx, and deploying the latest code automatically on newly created servers.


## 7. Environment Variables
Managed via `.env` file located in the `backend/` directory.
- Refer to `backend/.env` for the list of required variables.
- Required variables include: `SECRET_KEY`, `DATABASE_URL`, `DEBUG`.

## 8. Local Development Setup
Detailed instructions are provided in the **[DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md)**.
Basic requirements:
- Python 3.12+
- `uv` installed
- Docker (optional but recommended)

## 9. Database & Migrations
- **Initialization:** `python manage.py makemigrations`
- **Apply Migrations:** `python manage.py migrate`
- **Admin User:** [Refer to the CLI output or DEVELOPMENT_GUIDE for default credentials]

## 10. API Documentation
Available endpoints (once running):
- **Swagger:** `http://localhost:8000/api/swagger.json/`
- **ReDoc:** `http://localhost:8000/api/docs/`

## 11. Authentication
- **Method:** JWT (JSON Web Token)
- **Format:** `Authorization: Bearer <token>`
- **Endpoints:** `/api/token/` (Obtain) and `/api/token/refresh/` (Refresh)

## 12. Deployment
- **Environments:** Staging, Production (AWS ready)
- **CI/CD:** GitHub Actions configured for automated builds and deployment.

## 13. Monitoring & Logging
- **Health Check:** `/api/health-check/` (placeholder)
- **Logging:** Configured via Django LOGGING settings.
- **Monitoring:** Prometheus metrics available at `/metrics/` (if enabled).

## 14. Security Considerations
- Secrets are never committed to version control (.env excluded).
- Passwords hashed via Argon2/PBKDF2.
- CORS headers correctly configured.

## 15. Maintenance & Handover Notes
- **New Apps:** Use `ocd` or standard Django commands inside `backend/apps/`.
- **Backups:** Database backups should be managed at the RDS/Server level.

## 16. Support & Contact
- **Developer:** Maruf Hossain
- **Repository:** https://github.com/Maruf346/ChefStarz