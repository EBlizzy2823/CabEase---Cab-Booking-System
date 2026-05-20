# 🚖 CabEase — Cab Booking System

A Python + Tkinter + MySQL desktop application built as a Final Year Project.

---

## 🗂️ Project Structure

```
cab_booking_system/
├── assets/                  # Images & icons
├── database/
│   ├── db_connection.py     # MySQL connection helpers
│   └── setup.sql            # Run this ONCE to create the DB
├── modules/
│   ├── auth.py              # Login / register logic
│   ├── booking.py           # Booking logic
│   ├── admin.py             # Admin operations
│   └── utils.py             # Helpers (hashing, validation, fare)
├── views/
│   ├── login_view.py        # Login UI
│   ├── register_view.py     # Register UI
│   ├── dashboard_view.py    # User dashboard
│   ├── booking_view.py      # Book a cab
│   └── admin_view.py        # Admin panel
├── config.py                # DB credentials + theme colours
└── main.py                  # ← Run this to start the app
```

---

## ⚙️ Setup Instructions

### 1. Install Python
- Download from https://www.python.org/downloads/
- ✅ Check "Add Python to PATH" during install

### 2. Install required libraries
```bash
pip install mysql-connector-python pillow tkcalendar
```

### 3. Install MySQL
- Download from https://dev.mysql.com/downloads/installer/
- Choose "Developer Default"
- Set a root password and remember it

### 4. Create the database
Open MySQL Workbench (or the MySQL CLI) and run:
```sql
source database/setup.sql
```
Or paste the contents of `database/setup.sql` directly.

### 5. Update credentials
Open `config.py` and set:
```python
DB_PASSWORD = "your_mysql_password"
```

### 6. Run the app
```bash
python main.py
```

---

## 🔑 Default Login Credentials

| Role  | Email                | Password  |
|-------|----------------------|-----------|
| Admin | admin@cabease.com    | Admin@123 |
| User  | ram@example.com      | password123 |
| User  | sita@example.com     | password123 |

---

## ✨ Features

### User Side
- Register & Login with password hashing
- Book a cab (Mini / Sedan / SUV / Luxury)
- View booking history with colour-coded status
- Cancel pending bookings

### Admin Side
- Dashboard with key stats (bookings, revenue, users)
- View and update all bookings
- Manage users (view, delete)
- Revenue breakdown by cab type

---

## 🛠️ Tech Stack

| Layer      | Technology               |
|------------|--------------------------|
| Language   | Python 3.12+             |
| GUI        | Tkinter + tkcalendar     |
| Database   | MySQL 8.x                |
| Connector  | mysql-connector-python   |
| Security   | SHA-256 password hashing |

---

## 📚 For Your Report

**Problem Statement:** Manual cab booking is inefficient and error-prone. This system automates the entire process digitally.

**Objectives:**
1. Provide a user-friendly cab booking interface
2. Maintain a secure database of users and bookings
3. Enable admin monitoring and management

**Modules:**
- Authentication Module
- Booking Management Module
- Admin Control Module
- Database Layer

---

*Built with ❤️ as a Final Year Project*
