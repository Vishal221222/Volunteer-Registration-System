# Volunteer Registration System using Flask and MySQL

## Features

- Volunteer registration form
- MySQL database connection
- Admin login authentication
- Admin dashboard
- View, search and filter volunteers
- Approve, reject or keep volunteers pending
- Delete volunteer records
- Generate CSV report

## Folder Structure

```text
volunteer_registration_system/
│
├── app.py
├── create_admin.py
├── database.sql
├── requirements.txt
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   └── volunteers.html
│
└── static/
    └── style.css
```

## Setup Steps

### 1. Create virtual environment

```bash
python -m venv env
```

### 2. Activate virtual environment

For Windows:

```bash
env\Scripts\activate
```

For Mac/Linux:

```bash
source env/bin/activate
```

### 3. Install packages

```bash
pip install -r requirements.txt
```

### 4. Create MySQL database

Open MySQL command line or MySQL Workbench and run:

```sql
SOURCE database.sql;
```

Or manually copy and execute the SQL code from `database.sql`.

### 5. Add your MySQL password

Open `app.py` and `create_admin.py`, then replace:

```python
"password": "your_mysql_password"
```

with your actual MySQL password.

### 6. Create admin account

```bash
python create_admin.py
```

Default admin login:

```text
Username: admin
Password: admin123
```

### 7. Run project

```bash
python app.py
```

Open in browser:

```text
http://127.0.0.1:5000
```

## Admin Routes

```text
/admin/login
/admin/dashboard
/admin/volunteers
/admin/report
```
