# EduCore School ERP

**Full-stack School Management System**
Django 5 · PostgreSQL · REST API · Render.com

---

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Backend     | Python 3.12 + Django 5.0            |
| API         | Django REST Framework + JWT Auth    |
| Database    | PostgreSQL (Render managed DB)      |
| Static      | WhiteNoise (served from Django)     |
| Deployment  | Render.com (render.yaml)            |

---

## Project Structure

```
educore/
├── config/
│   ├── settings.py        # All settings (env-driven)
│   ├── urls.py            # Root URL dispatcher
│   └── wsgi.py
├── apps/
│   ├── core/              # User, School, Grade, Section + dashboard API
│   ├── students/          # Student CRUD + stats
│   ├── teachers/          # Teacher, Department, Subject, Leave
│   ├── attendance/        # Daily attendance + bulk mark + reports
│   ├── fees/              # Fee structure, invoices, payments, scholarships
│   ├── exams/             # Exams, schedules, results, timetable
│   ├── library/           # Books, categories, issues/returns
│   ├── transport/         # Vehicles, routes, stops, student assignments
│   └── announcements/     # Announcements, notice board, events
├── templates/
│   └── index.html         # SPA entry point (served by Django)
├── static/                # CSS/JS assets
├── requirements.txt
├── render.yaml            # Render.com IaC deploy config
├── .env.example           # Environment variable template
└── manage.py
```

---

## Local Development Setup

### 1. Clone & create virtual environment

```bash
git clone https://github.com/yourorg/educore.git
cd educore
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — set SECRET_KEY, DATABASE_URL (local postgres), DEBUG=True
```

Example local `.env`:
```
SECRET_KEY=dev-secret-key-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://postgres:password@localhost:5432/educore_dev
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Create local PostgreSQL database

```bash
psql -U postgres -c "CREATE DATABASE educore_dev;"
```

### 4. Run migrations & seed data

```bash
python manage.py migrate
python manage.py seed_data       # creates admin user + demo data
python manage.py createsuperuser # optional additional superuser
```

### 5. Start development server

```bash
python manage.py runserver
```

API available at: `http://localhost:8000/api/`
Admin panel:       `http://localhost:8000/admin/`

**Default credentials (from seed_data):**
- Username: `admin`
- Password: `Admin@1234`

---

## API Reference

### Authentication

All API endpoints require a JWT Bearer token (except login).

```bash
# Login
POST /api/auth/login/
{
  "username": "admin",
  "password": "Admin@1234"
}
# Response: { "access": "...", "refresh": "...", "user": {...} }

# Use token in all subsequent requests
Authorization: Bearer <access_token>

# Refresh token
POST /api/auth/refresh/
{ "refresh": "..." }

# Logout (blacklist refresh token)
POST /api/auth/logout/
{ "refresh": "..." }
```

### Core Endpoints

| Method | Endpoint                        | Description                    |
|--------|---------------------------------|--------------------------------|
| GET    | `/api/core/dashboard/`          | KPI stats for dashboard        |
| GET    | `/api/core/me/`                 | Current user profile           |
| GET    | `/api/core/grades/`             | All grades                     |
| GET    | `/api/core/sections/`           | All sections (filterable)      |
| GET/PUT| `/api/core/school/`             | School profile                 |

### Students

| Method | Endpoint                         | Description                    |
|--------|----------------------------------|--------------------------------|
| GET    | `/api/students/`                 | List (paginated, searchable)   |
| POST   | `/api/students/`                 | Admit new student              |
| GET    | `/api/students/{id}/`            | Student detail                 |
| PATCH  | `/api/students/{id}/`            | Update student                 |
| POST   | `/api/students/{id}/deactivate/` | Deactivate student             |

**Query params:** `?section=1`, `?section__grade=2`, `?search=Aarav`, `?is_active=true`

### Teachers

| Method | Endpoint                               | Description           |
|--------|----------------------------------------|-----------------------|
| GET    | `/api/teachers/`                       | All teachers          |
| POST   | `/api/teachers/`                       | Add teacher           |
| GET    | `/api/teachers/{id}/schedule/`         | Teacher's timetable   |
| GET    | `/api/teachers/departments/`           | All departments       |
| GET    | `/api/teachers/subjects/`              | All subjects          |
| GET    | `/api/teachers/leaves/`                | Leave applications    |
| POST   | `/api/teachers/leaves/{id}/approve/`   | Approve leave         |

### Attendance

| Method | Endpoint                                | Description                  |
|--------|-----------------------------------------|------------------------------|
| GET    | `/api/attendance/`                      | All records (filtered)       |
| POST   | `/api/attendance/bulk_mark/`            | Mark entire section at once  |
| GET    | `/api/attendance/today_summary/`        | Today's attendance KPIs      |
| GET    | `/api/attendance/section_report/`       | Section report (date range)  |
| GET    | `/api/attendance/holidays/`             | Holiday calendar             |

**Bulk mark payload:**
```json
{
  "section_id": 1,
  "date": "2026-03-17",
  "records": [
    {"student_id": 1, "status": "present"},
    {"student_id": 2, "status": "absent", "remarks": "Sick"}
  ]
}
```

### Fees

| Method | Endpoint                           | Description                    |
|--------|------------------------------------|--------------------------------|
| GET    | `/api/fees/invoices/`              | All invoices                   |
| POST   | `/api/fees/invoices/`              | Create invoice                 |
| GET    | `/api/fees/invoices/summary/`      | Collection summary KPIs        |
| POST   | `/api/fees/invoices/mark_overdue/` | Bulk-mark overdue invoices     |
| POST   | `/api/fees/payments/`              | Record payment + issue receipt |
| GET    | `/api/fees/structures/`            | Fee structure (per grade/term) |

### Exams & Results

| Method | Endpoint                             | Description                |
|--------|--------------------------------------|----------------------------|
| GET    | `/api/exams/`                        | All exams                  |
| POST   | `/api/exams/`                        | Create exam                |
| GET    | `/api/exams/schedules/`              | Exam schedules             |
| POST   | `/api/exams/results/bulk_enter/`     | Bulk enter marks           |
| GET    | `/api/exams/results/section_report/` | Results analytics          |
| GET    | `/api/exams/timetable/`              | Weekly timetable slots     |

### Library

| Method | Endpoint                            | Description             |
|--------|-------------------------------------|-------------------------|
| GET    | `/api/library/`                     | Book catalog            |
| POST   | `/api/library/`                     | Add book                |
| GET    | `/api/library/stats/`               | Library summary KPIs    |
| POST   | `/api/library/issues/`              | Issue a book            |
| POST   | `/api/library/issues/{id}/return_book/` | Return a book       |

### Transport

| Method | Endpoint                  | Description           |
|--------|---------------------------|-----------------------|
| GET    | `/api/transport/`         | All routes            |
| GET    | `/api/transport/vehicles/`| All vehicles          |
| GET    | `/api/transport/drivers/` | All drivers           |
| POST   | `/api/transport/student-routes/` | Assign student to route |

### Announcements

| Method | Endpoint                        | Description         |
|--------|---------------------------------|---------------------|
| GET    | `/api/announcements/`           | All announcements   |
| POST   | `/api/announcements/`           | Create announcement |
| GET    | `/api/announcements/notices/`   | Notice board        |
| GET    | `/api/announcements/events/`    | School calendar     |

---

## Deploying to Render.com

### One-time setup

1. **Push to GitHub:**
```bash
git init
git add .
git commit -m "Initial EduCore commit"
git remote add origin https://github.com/yourorg/educore.git
git push -u origin main
```

2. **Create services on Render:**
   - Go to [render.com](https://render.com) → **New** → **Blueprint**
   - Connect your GitHub repo
   - Render reads `render.yaml` automatically and creates:
     - Web service: `educore-api`
     - PostgreSQL database: `educore-db`

3. **Environment variables** (set in Render dashboard under your service → Environment):
   - `SECRET_KEY` → auto-generated by `render.yaml`
   - `DATABASE_URL` → auto-linked from `educore-db`
   - `DEBUG` → `False`
   - `ALLOWED_HOSTS` → `educore-api.onrender.com`

4. **Post-deploy: seed demo data (optional):**
   In Render dashboard → your web service → **Shell**:
```bash
python manage.py seed_data
```

### Continuous Deployment

Every `git push` to `main` automatically triggers a redeploy on Render (`autoDeploy: true` in `render.yaml`).

---

## User Roles & Permissions

| Role          | Access                                           |
|---------------|--------------------------------------------------|
| `super_admin` | Full access to everything                        |
| `admin`       | Full access except system-level settings         |
| `principal`   | Read all + approve leaves, view all reports      |
| `teacher`     | Own schedule, mark attendance, enter results     |
| `accountant`  | Fee collection, invoices, financial reports only |
| `librarian`   | Library module only                              |
| `parent`      | Own child's data only (attendance, fees, results)|
| `student`     | Own academic records only                        |

---

## Key Design Decisions

- **JWT Auth** — stateless, works well with mobile apps and SPAs
- **Bulk endpoints** — `bulk_mark` for attendance saves N² API calls to 1
- **Auto-grade calculation** — `ExamResult.save()` computes A+/A/B/C/D/F automatically
- **Invoice lifecycle** — `FeePayment.save()` updates parent invoice status automatically
- **WhiteNoise** — serves static files directly from Django, no separate nginx needed on Render
- **`render.yaml`** — full infra-as-code: one file defines web service + managed DB

---

## Running Tests

```bash
pip install pytest pytest-django factory-boy
pytest
```

---

## Adding a Frontend (React / Vue / Next.js)

Option A — **Same Render service (SPA served by Django):**
1. Build your frontend: `npm run build` → outputs to `dist/` or `build/`
2. Copy `dist/index.html` to `templates/index.html`
3. Copy `dist/assets/` to `static/`
4. Run `python manage.py collectstatic`
5. The Django `frontend_urls.py` catch-all serves the SPA for all non-`/api/` routes

Option B — **Separate Render Static Site:**
1. Create a second Render service of type **Static Site**
2. Set `CORS_ALLOWED_ORIGINS` env var on the Django service to your static site URL
3. Frontend calls `https://educore-api.onrender.com/api/...`

---

## License

MIT — free to use and modify for your school.
