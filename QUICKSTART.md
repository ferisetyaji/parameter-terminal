# Admin Dashboard - Quick Start Guide

## ⚡ Quick Setup (5 menit)

```bash
# 1. Navigate to project
cd admin_project

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Create admin user
python manage.py createsuperuser

# 6. Run server
python manage.py runserver
```

Visit: http://localhost:8000

---

## Default Credentials

Gunakan credentials yang Anda buat saat `createsuperuser`

## Features

- Dashboard dengan statistics
- User management (create, read, update)
- Audit logging system
- Role-based access control
- System settings management
- Beautiful responsive UI

## Admin Panel

Visit: http://localhost:8000/admin/

---

Selamat! Admin Dashboard Anda siap digunakan! 🎉
