# Library Management System

A backend library management system built with **Flask** and **PostgreSQL**, using **raw SQL** for database operations.

The project provides APIs for managing library resources such as members, books, branches, loans, loan statuses, notifications, and related workflows.

---

## Tech Stack

* Python 3.11
* Flask
* PostgreSQL 16
* psycopg
* Raw SQL
* pytest
* Git

> This project does not use an ORM. Database access is implemented with SQL queries directly.

---

## Prerequisites

Install the following software before starting:

| Requirement | Version      |
| ----------- | ------------ |
| Python      | 3.11.x       |
| PostgreSQL  | 16.x         |
| Git         | 2.x or newer |

Verify the installed versions:

```bash
python --version
psql --version
git --version
```

The commands should report Python 3.11, PostgreSQL 16, and Git 2.x or newer.

---

# Installation

Follow these steps on a clean machine.

## 1. Clone the repository

```bash
git clone <REPOSITORY_URL>
cd library_project
```

For example:

```bash
git clone https://github.com/<username>/library_project.git
cd library_project
```

---

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, activate using:

```powershell
.venv\Scripts\activate.bat
```

### Linux / macOS

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

After activation, verify:

```bash
python --version
```

It should show Python 3.11.x.

---

## 3. Install dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

---

# Database Setup

The application uses PostgreSQL.

## 4. Create the database

Open PostgreSQL:

```bash
psql -U postgres
```

Create the database:

```sql
CREATE DATABASE library_db;
```

Exit PostgreSQL:

```sql
\q
```

You can verify that the database exists with:

```bash
psql -U postgres -l
```

---

## 5. Configure environment variables

Create a `.env` file in the project root:

```text
library_project/
├── app/
├── migrations/
├── tests/
├── .env
├── requirements.txt
└── run.py
```

Add the following configuration:

```env
FLASK_ENV=development

DB_HOST=localhost
DB_PORT=5432
DB_NAME=library_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password

DB_POOL_MIN=1
DB_POOL_MAX=10

JWT_SECRET_KEY=change-this-secret-key
```

Replace:

```text
your_postgres_password
```

with the password of your PostgreSQL user.

Do not commit `.env` to Git.

The `.gitignore` file should contain:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

---

# Database Migrations

The database schema is maintained through SQL migration files in the `migrations/` directory.

Example:

```text
migrations/
├── 2026-08-16_init.sql
├── 2026-08-20_add_members.sql
└── 2026-08-25_add_notifications.sql
```

Run the migrations in chronological order.

For example:

```bash
psql -U postgres -d library_db -f migrations/2026-08-16_init.sql
```

Then run the remaining migration files in order:

```bash
psql -U postgres -d library_db -f migrations/2026-08-20_add_members.sql
psql -U postgres -d library_db -f migrations/2026-08-25_add_notifications.sql
```

If the project contains a migration runner, use the project's migration command instead.

### Verify the database

Connect to the database:

```bash
psql -U postgres -d library_db
```

List the tables:

```sql
\dt
```

You should see the application's database tables.

Exit:

```sql
\q
```

---

# Run the Application

Make sure the virtual environment is activated.

Start the Flask application:

```bash
python run.py
```

The development server should start on:

```text
http://127.0.0.1:5000
```

You can also access it through:

```text
http://localhost:5000
```

Keep this terminal running while testing the API.

---

# API Examples

The following examples demonstrate how to communicate with the running server.

## Example 1: Get Books

```bash
curl http://127.0.0.1:5000/books
```

Example response:

```json
{
  "items": [
    {
      "book_id": 1,
      "title": "The Hobbit",
      "author": "J. R. R. Tolkien"
    }
  ]
}
```

---

## Example 2: Search Books

The API supports query parameters.

```bash
curl "http://127.0.0.1:5000/books?search=tolkien&page=1&limit=10"
```

This requests:

* `search=tolkien`
* page `1`
* maximum `10` results

---

## Example 3: Create a Member

```bash
curl -X POST http://127.0.0.1:5000/members \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"John Doe\",\"email\":\"john@example.com\"}"
```

The server should return an appropriate HTTP status code and JSON response.

---

## Example 4: Get a Specific Book

If the API exposes a book resource by ID:

```bash
curl http://127.0.0.1:5000/books/1
```

A successful request should return the book with ID `1`.

---

# Running Tests

Install the development dependencies if they are not already installed:

```bash
pip install -r requirements.txt
```

Run the test suite:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

All tests should pass before the project is considered ready.

---

# Project Structure

```text
library_project/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── errors.py
│   ├── extensions.py
│   │
│   ├── auth/
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── repository.py
│   │
│   ├── members/
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── repository.py
│   │
│   ├── books/
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── repository.py
│   │
│   ├── loans/
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── repository.py
│   │
│   ├── quiz/
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── repository.py
│   │
│   ├── db/
│   │   └── database.py
│   │
│   └── utils/
│       └── logger.py
│
├── migrations/
│   └── *.sql
│
├── tests/
│   └── ...
│
├── logs/
│
├── .env
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

---

# Development Notes

## Database

The application uses PostgreSQL directly through `psycopg`.

Database queries are kept in the repository layer.

The general responsibility separation is:

```text
Route
  ↓
Service
  ↓
Repository
  ↓
PostgreSQL
```

### Route

Handles HTTP concerns:

* request parsing
* authentication/authorization
* status codes
* response formatting

### Service

Handles business logic:

* validation
* workflows
* state transitions
* business rules

### Repository

Handles database operations:

* SQL queries
* parameters
* transactions
* database results

This separation prevents routes from becoming enormous functions containing HTTP handling, business logic, and SQL simultaneously, which is how backend projects slowly turn into archaeological sites.

---

# Configuration

Environment-specific configuration must be provided through environment variables or `.env`.

Never hard-code:

* database passwords
* JWT secrets
* API keys
* other credentials

The `.env` file is intended for local development and must not be committed to the repository.

---

# Clean-Machine Acceptance Test

A fresh machine should be able to run the application using only this README and the repository.

The acceptance test is:

```text
1. Install Python 3.11
2. Install PostgreSQL 16
3. Install Git
4. Clone repository
5. Create virtual environment
6. Activate virtual environment
7. Install requirements.txt
8. Create PostgreSQL database
9. Create .env
10. Run all migrations
11. Start Flask server
12. Call an API endpoint
13. Receive a valid response
```

For example:

```bash
curl http://127.0.0.1:5000/books
```

If this request successfully reaches the running Flask server and returns the expected response, the clean-machine setup is working.

If another developer cannot get the server running by following this README alone, the project setup is not considered complete.

---

# Troubleshooting

## `ModuleNotFoundError: No module named 'flask'`

Make sure the virtual environment is activated:

### Windows

```powershell
.venv\Scripts\Activate.ps1
```

Then reinstall dependencies:

```bash
pip install -r requirements.txt
```

---

## `psql is not recognized`

PostgreSQL may not be added to the system `PATH`.

Verify PostgreSQL is installed and add its `bin` directory to `PATH`.

Then reopen the terminal and run:

```bash
psql --version
```

---

## `connection refused`

Check that PostgreSQL is running and that the `.env` configuration matches the database:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=library_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

---

## `database "library_db" does not exist`

Create it:

```bash
psql -U postgres
```

Then:

```sql
CREATE DATABASE library_db;
```

---

## Migration file not found

Make sure you are running the command from the repository root:

```bash
cd library_project
```

Then verify:

```bash
dir migrations
```

on Windows, or:

```bash
ls migrations
```

on Linux/macOS.

---

# License

This project is for educational and development purposes.
