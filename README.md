# Admin Dashboard - Django Web Application

Aplikasi web admin yang dibangun dengan Django untuk manajemen user, audit log, dan pengaturan sistem.

## 📋 Fitur Utama

- ✅ **User Authentication** - Sistem login yang aman
- ✅ **User Management** - Kelola user dengan berbagai role (Admin, Manager, Staff, Viewer)
- ✅ **Audit Logging** - Catat semua aktivitas user
- ✅ **Dashboard** - Statistik dan overview sistem
- ✅ **System Settings** - Kelola pengaturan sistem
- ✅ **Responsive Design** - Interface yang mobile-friendly dengan Bootstrap 5
- ✅ **Built-in Admin Panel** - Django admin untuk manajemen data yang lebih mendalam

## 🛠️ Requirements

- Python 3.10+
- Django 4.2.8
- Pillow 10.1.0 (untuk image handling)
- python-decouple 3.8

## 📁 Struktur Proyek

```
admin_project/
├── admin_project/          # Django project configuration
│   ├── __init__.py
│   ├── settings.py         # Settings konfigurasi
│   ├── urls.py            # URL routing utama
│   └── wsgi.py            # WSGI configuration
├── admin_app/              # Django application
│   ├── migrations/
│   ├── templates/          # HTML templates
│   │   └── admin_app/
│   │       ├── base.html
│   │       ├── login.html
│   │       ├── dashboard.html
│   │       ├── user_list.html
│   │       ├── user_detail.html
│   │       ├── user_edit.html
│   │       ├── audit_logs.html
│   │       └── settings.html
│   ├── static/            # Static files (CSS, JS, images)
│   │   ├── css/
│   │   └── js/
│   ├── admin.py           # Django admin configuration
│   ├── apps.py            # App configuration
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # App URL routing
│   └── __init__.py
├── manage.py              # Django management script
├── db.sqlite3             # Database (akan dibuat setelah migration)
└── requirements.txt       # Python dependencies
```

## 🚀 Instalasi dan Setup

### 1. Clone dan Setup Virtual Environment

```bash
cd /home/topgun/pp/algotrade/admin_project
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Ikuti instruksi di terminal untuk membuat admin account.

### 5. Run Development Server

```bash
python manage.py runserver
```

Server akan berjalan di: `http://localhost:8000`

## 🔗 URL Routes

| Path | Deskripsi |
|------|-----------|
| `/login/` | Halaman login |
| `/logout/` | Logout user |
| `/` | Dashboard utama |
| `/users/` | Daftar semua user |
| `/users/<id>/` | Detail user |
| `/users/<id>/edit/` | Edit user |
| `/audit-logs/` | Lihat audit logs |
| `/settings/` | Pengaturan sistem |
| `/admin/` | Django Admin Panel |

## 📊 Models

### User_Profile
- Field: user, role, phone, address, city, country, profile_picture, created_at, updated_at
- Role: admin, manager, staff, viewer

### AuditLog
- Field: user, action, model_name, object_id, description, ip_address, user_agent, timestamp
- Action: create, update, delete, login, logout, view

### SystemSettings
- Field: key, value, description, updated_at

## 👤 User Roles

- **Admin**: Akses penuh ke semua fitur
- **Manager**: Kelola user dan melihat logs
- **Staff**: Kelola data dasar
- **Viewer**: Hanya dapat melihat data

## 🔐 Security Features

- Login/Logout dengan session management
- CSRF Protection
- Password hashing dengan Django built-in
- Audit logging untuk semua aktivitas
- Role-based access control
- IP address logging

## 🎨 Styling

Menggunakan Bootstrap 5 dengan custom CSS untuk:
- Responsive layout
- Modern UI components
- Custom color scheme
- Mobile-friendly design

## 📝 Menggunakan Admin Panel

Akses Django Admin di `/admin/` dengan credentials superuser:
- Kelola User_Profile
- Kelola Audit Logs (read-only)
- Kelola System Settings

## 🔄 Workflow Aktivitas

Setiap aktivitas penting dicatat di AuditLog:
- Login/Logout
- Create/Update/Delete data
- View important pages
- Sistem mengcatat: user, waktu, IP address, user agent

## 📱 Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🐛 Troubleshooting

### Database Error
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Migration Issues
```bash
# Clear migrations dan recreate
python manage.py makemigrations --empty admin_app --name reset
python manage.py migrate
```

### Port Already in Use
```bash
python manage.py runserver 8001
```

## 📚 Development Tips

1. **Buat app baru:**
```bash
python manage.py startapp new_app
```

2. **Buat migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Shell Django untuk testing:**
```bash
python manage.py shell
```

4. **Collect static files:**
```bash
python manage.py collectstatic
```

## 🚀 Production Deployment

Sebelum deploy ke production:

1. Set `DEBUG = False` di settings.py
2. Set `SECRET_KEY` yang aman
3. Gunakan database yang lebih robust (PostgreSQL, MySQL)
4. Setup HTTPS
5. Configure ALLOWED_HOSTS
6. Setup static files serving
7. Gunakan web server (Gunicorn, uWSGI)
8. Setup email configuration

## 📧 Support

Untuk pertanyaan atau masalah, hubungi tim development.

## 📄 License

MIT License - Bebas digunakan untuk project apapun.

---

**Created:** 2026
**Last Updated:** January 14, 2026
