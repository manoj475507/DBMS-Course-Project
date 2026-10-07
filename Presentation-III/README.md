# Cold Storage Commodity and Chamber Management System
**DBMS Course Project — Phase 3 (Presentation-III: Web UI & Database Integration)**

A full-stack database-backed web dashboard built with **Python, Flask, and MySQL** for managing cold storage commodities, temperature-controlled chambers, and customer accounts.

---

## 📌 Project Overview

This project satisfies the Phase 3 (Presentation-III) demonstration requirements:
1. **VIEW Records**: Fetches and renders live data directly from `ColdStorageDB.Customer` in MySQL.
2. **INSERT Records**: Inserts new customer records with client/server validation and transaction `COMMIT`.
3. **DELETE Records**: Removes customer records by `Customer_ID` with confirmation modals and transaction `COMMIT`.
4. **Transaction Integrity**: Enforces `ROLLBACK` on failed transactions (e.g. duplicate primary keys, foreign key violations).
5. **No Schema Alteration**: Connects seamlessly to the pre-existing database schema without modifying, dropping, or re-creating tables.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.x, Flask
- **Database**: MySQL Server 9.x (`ColdStorageDB`)
- **Database Driver**: `mysql-connector-python`
- **Frontend**: HTML5, CSS3 (Custom Responsive Dashboard), Vanilla JavaScript
- **Environment Management**: `python-dotenv`

---

## 🗄️ Database Table: Customer

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `Customer_ID` | `INT` | `PRIMARY KEY` | Unique identifier for customer |
| `Customer_Name` | `VARCHAR(100)` | `NOT NULL` | Full name of customer/enterprise |
| `Phone` | `VARCHAR(15)` | `NOT NULL` | Contact number |
| `Email` | `VARCHAR(100)` | `NULL` | Optional email address |
| `Address` | `VARCHAR(200)` | `NULL` | Optional physical address |
| `City` | `VARCHAR(50)` | `NOT NULL` | City of operation |

---

## 📁 Project Structure

```text
ColdStorage-UI/
├── app.py              # Main Flask application with routes and MySQL integration
├── requirements.txt    # Python package dependencies
├── .env.example        # Template for database credentials
├── .gitignore          # Ignores .env and virtual environment files
├── README.md           # Documentation and presentation guide
├── templates/
│   └── index.html      # Dashboard template (Jinja2)
└── static/
    └── style.css       # Clean dashboard styling and responsive layout
```

---

## 🚀 Setup & Execution Guide

### 1. Install Dependencies
Open PowerShell or Command Prompt in the project folder and run:
```powershell
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to create your `.env` file:
```powershell
Copy-Item .env.example .env
```
Open `.env` in any text editor and fill in your MySQL credentials:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_password
DB_NAME=ColdStorageDB
```

> 🔒 **Security Notice:** The `.env` file is included in `.gitignore` so your password is never committed to version control.

### 3. Run the Application
Start the Flask development server:
```powershell
python app.py
```

### 4. Access the Dashboard
Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🎯 How to Demonstrate to Your Lecturer (Presentation-III)

### Step 1: VIEW Existing Data
- Open `http://127.0.0.1:5000`.
- Point out the **MySQL Connected (ColdStorageDB)** indicator in the header.
- Show the table populated with records loaded directly from MySQL using `SELECT * FROM Customer ORDER BY Customer_ID ASC`.

### Step 2: INSERT a New Customer
- In the **Add New Customer** form, enter:
  - **Customer ID**: `99` (or any unused integer)
  - **Customer Name**: `Vikas Cold Traders`
  - **Phone**: `9876501234`
  - **Email**: `vikas@coldtraders.com`
  - **City**: `Surat`
  - **Address**: `Warehouse 4B, Ring Road`
- Click **Insert Customer into MySQL**.
- **Result**: A green success message appears, and customer `#99` immediately shows up in the table.
- *(Optional verification)*: Run `SELECT * FROM Customer WHERE Customer_ID = 99;` in MySQL Workbench to show that the record is in MySQL.

### Step 3: Test Error Handling (Primary Key Duplication)
- Try entering the exact same Customer ID `99` again.
- Click **Insert Customer**.
- **Result**: The application catches MySQL Error 1062, executes `db.rollback()`, and shows:
  *"Primary Key Conflict: A customer with ID '99' already exists in ColdStorageDB.Customer."*

### Step 4: DELETE the Customer
- Click the **🗑 Delete** button next to customer `#99` in the table (or use the Delete form on the right).
- A confirmation dialog appears asking: *"Are you sure you want to permanently delete customer: ID: #99 - Vikas Cold Traders?"*.
- Click **Yes, Delete Record**.
- **Result**: Customer `#99` is removed from the table with a success message.
- *(Optional verification)*: Run `SELECT * FROM Customer WHERE Customer_ID = 99;` in MySQL Workbench to show the row has been deleted.

---

## 💡 Code & Viva Reference for Presentation

### 1. How Flask connects to MySQL:
```python
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("DB_PASSWORD"),
    database="ColdStorageDB"
)
```

### 2. Why `commit()` and `rollback()` are required:
- By default, relational databases follow **ACID** properties (Atomicity, Consistency, Isolation, Durability).
- In Python's DB-API 2.0, transactions start automatically.
- Any Data Modification Language (DML) operation (`INSERT`, `UPDATE`, `DELETE`) is temporary in the session until `conn.commit()` is executed.
- If an error occurs (such as duplicate keys or network drops), `conn.rollback()` safely aborts the transaction, leaving the database in a consistent state.

### 3. Parameterized Queries (`%s`):
Instead of string concatenation (`f"INSERT INTO ... '{name}'"`), we pass query parameters separately:
```python
cursor.execute("INSERT INTO Customer (Customer_ID, Customer_Name) VALUES (%s, %s);", (cid, name))
```
This guarantees **SQL Injection protection** because the database treats inputs strictly as literal values rather than executable SQL syntax.
