# Salon Appointment Booking Platform

A full-stack booking app with role-based access. Customers view open slots, book and cancel.
Staff publish their own slots and see appointments. Admins manage services and all bookings.

**Stack:** Django, Django REST Framework, JWT (SimpleJWT), PostgreSQL/SQLite, React (Vite)

## Features
- JWT authentication with three roles: customer, staff, admin
- Customers: browse open slots by date and service, book a slot, cancel a booking, view history
- Staff: create and remove their own slots (overlaps blocked), view their appointments
- Admin: manage services, view and cancel any booking
- **Double-booking prevention** at two levels: row lock inside a transaction, plus a partial
  unique database constraint (one active booking per slot)
- **Cancellation cutoff:** customers can cancel up to 2 hours before the appointment (`CANCEL_CUTOFF_HOURS`)
- Automated tests for booking, double booking, cancellation and permissions

## Run locally
```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo        # demo users, services, slots
python manage.py runserver        # http://localhost:8000

# Frontend (new terminal)
cd frontend
cp .env.example .env
npm install
npm run dev                       # http://localhost:5173
```
Demo logins: `admin / Admin@12345`, `priya / Staff@12345` (staff), `demo / Demo@12345` (customer).
Run tests: `python manage.py test`

First time only: run `python manage.py makemigrations accounts bookings` before `migrate`,
and commit the generated `migrations/` folders.

## API
| Method | Endpoint | Who |
|---|---|---|
| POST | `/api/auth/register/` | public (creates a customer) |
| POST | `/api/auth/login/`, `/api/auth/refresh/` | public |
| GET | `/api/auth/me/` | any user |
| GET | `/api/services/` | any user (admin: full CRUD) |
| GET | `/api/slots/?date=YYYY-MM-DD&service=ID` | any user (customers see open slots only) |
| POST, DELETE | `/api/slots/` | staff, admin |
| GET, POST | `/api/bookings/` | GET: any user (scoped by role), POST: customer |
| POST | `/api/bookings/{id}/cancel/` | customer (own), admin |

## Deploy (free tiers)
- **Database:** create a Postgres database on Neon or Supabase and copy its URL.
- **Backend (Render):** root `backend`, build `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`,
  start `gunicorn config.wsgi`. Set `SECRET_KEY`, `DEBUG=0`, `ALLOWED_HOSTS`, `DATABASE_URL`, `FRONTEND_URL` (your Vercel URL).
- **Frontend (Vercel):** root `frontend`, set `VITE_API_URL=https://<your-render-app>.onrender.com/api`.
- Create the admin on the server with `python manage.py createsuperuser` (or run `seed_demo` for a demo).
