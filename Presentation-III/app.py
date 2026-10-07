"""
=============================================================================
Cold Storage Commodity & Chamber Management System
DBMS Course Project - Phase 3 (Presentation-III)
Tech Stack: Python, Flask, MySQL, mysql-connector-python, HTML/CSS/JavaScript
=============================================================================

This Flask application demonstrates core DBMS functionality:
1. SELECT Query  -> VIEW all existing customer records from MySQL
2. INSERT Query  -> Add new customer into ColdStorageDB.Customer with COMMIT
3. DELETE Query  -> Delete customer by Customer_ID from MySQL with COMMIT
4. Error Handling-> Handles duplicates (PK violation), FK constraints, & ROLLBACK
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Secret key required for session security and flash messages
app.secret_key = os.getenv("SECRET_KEY", "coldstorage_presentation3_secret_key_2026")

# Database configuration from environment variables (defaults to ColdStorageDB)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ColdStorageDB")


def get_db_connection():
    """
    Helper function to establish and return a connection to MySQL database.
    Returns:
        (connection, None) if successful
        (None, error_message) if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection, None
    except mysql.connector.Error as err:
        # Never expose password or internal credentials in error messages
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            msg = "Access Denied: Invalid MySQL username or password in .env"
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            msg = f"Database '{DB_NAME}' does not exist on MySQL server."
        else:
            msg = f"MySQL Connection Error: {err.msg}"
        return None, msg


@app.route("/")
def index():
    """
    Dashboard Home Route (VIEW Operation):
    - Connects to MySQL
    - Fetches all records from ColdStorageDB.Customer
    - Fetches system summary stats (e.g., total chambers, commodities)
    - Renders the dashboard template
    """
    db_conn, conn_err = get_db_connection()
    customers = []
    stats = {
        "total_customers": 0,
        "total_chambers": 0,
        "total_commodities": 0,
        "total_lots": 0
    }

    if not db_conn:
        # Database connection failed; render page with warning banner
        return render_template(
            "index.html",
            customers=[],
            stats=stats,
            db_connected=False,
            db_error=conn_err,
            db_name=DB_NAME,
            db_user=DB_USER,
            db_host=DB_HOST
        )

    try:
        cursor = db_conn.cursor(dictionary=True)

        # 1. SELECT query to view all customer records ordered by Customer_ID
        cursor.execute("""
            SELECT Customer_ID, Customer_Name, Phone, Email, Address, City
            FROM Customer
            ORDER BY Customer_ID ASC;
        """)
        customers = cursor.fetchall()
        stats["total_customers"] = len(customers)

        # 2. Fetch ancillary counts for dashboard stat cards (safe fallback if tables empty)
        try:
            cursor.execute("SELECT COUNT(*) AS cnt FROM Chamber;")
            row = cursor.fetchone()
            if row:
                stats["total_chambers"] = row["cnt"]
        except Exception:
            pass

        try:
            cursor.execute("SELECT COUNT(*) AS cnt FROM Commodity;")
            row = cursor.fetchone()
            if row:
                stats["total_commodities"] = row["cnt"]
        except Exception:
            pass

        try:
            cursor.execute("SELECT COUNT(*) AS cnt FROM Lot;")
            row = cursor.fetchone()
            if row:
                stats["total_lots"] = row["cnt"]
        except Exception:
            pass

        cursor.close()
        db_conn.close()

        return render_template(
            "index.html",
            customers=customers,
            stats=stats,
            db_connected=True,
            db_error=None,
            db_name=DB_NAME,
            db_user=DB_USER,
            db_host=DB_HOST
        )

    except mysql.connector.Error as err:
        if db_conn:
            db_conn.close()
        flash(f"Error fetching data: {err.msg}", "danger")
        return render_template(
            "index.html",
            customers=[],
            stats=stats,
            db_connected=False,
            db_error=err.msg,
            db_name=DB_NAME,
            db_user=DB_USER,
            db_host=DB_HOST
        )


@app.route("/customer/insert", methods=["POST"])
def insert_customer():
    """
    INSERT Operation:
    - Extracts form fields
    - Validates mandatory attributes
    - Executes parameterized INSERT query
    - Calls conn.commit() to persist changes
    - Calls conn.rollback() on failure
    """
    # 1. Retrieve data from HTML form
    customer_id = request.form.get("customer_id", "").strip()
    customer_name = request.form.get("customer_name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip() or None
    address = request.form.get("address", "").strip() or None
    city = request.form.get("city", "").strip()

    # 2. Basic input validations
    if not customer_id or not customer_name or not phone or not city:
        flash("Validation Error: Customer ID, Name, Phone, and City are required fields.", "warning")
        return redirect(url_for("index"))

    try:
        customer_id_int = int(customer_id)
        if customer_id_int <= 0:
            flash("Validation Error: Customer ID must be a positive integer.", "warning")
            return redirect(url_for("index"))
    except ValueError:
        flash("Validation Error: Customer ID must be a numeric integer value.", "warning")
        return redirect(url_for("index"))

    # 3. Connect to MySQL
    db_conn, conn_err = get_db_connection()
    if not db_conn:
        flash(f"Database error: {conn_err}", "danger")
        return redirect(url_for("index"))

    try:
        cursor = db_conn.cursor()

        # Parameterized query protects against SQL injection
        sql = """
            INSERT INTO Customer (Customer_ID, Customer_Name, Phone, Email, Address, City)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        values = (customer_id_int, customer_name, phone, email, address, city)

        cursor.execute(sql, values)

        # COMMIT the transaction to make the INSERT permanent in MySQL
        db_conn.commit()

        flash(f"Success! Customer '{customer_name}' (ID: {customer_id_int}) inserted successfully into MySQL.", "success")
        cursor.close()
        db_conn.close()

    except mysql.connector.Error as err:
        # ROLLBACK the transaction on error
        db_conn.rollback()
        db_conn.close()

        # Handle Primary Key duplication specifically
        if err.errno == errorcode.ER_DUP_ENTRY or err.errno == 1062:
            flash(f"Primary Key Conflict: A customer with ID '{customer_id}' already exists in ColdStorageDB.Customer.", "danger")
        else:
            flash(f"MySQL Error during INSERT: {err.msg}", "danger")

    return redirect(url_for("index"))


@app.route("/customer/delete", methods=["POST"])
def delete_customer():
    """
    DELETE Operation:
    - Extracts Customer_ID to delete
    - Executes parameterized DELETE query
    - Calls conn.commit() if rows affected
    - Handles Foreign Key constraints (e.g. customer has lots/invoices)
    - Calls conn.rollback() on failure
    """
    customer_id = request.form.get("customer_id", "").strip()

    if not customer_id:
        flash("Validation Error: Customer ID is required to perform deletion.", "warning")
        return redirect(url_for("index"))

    try:
        customer_id_int = int(customer_id)
    except ValueError:
        flash("Validation Error: Customer ID must be a numeric integer value.", "warning")
        return redirect(url_for("index"))

    db_conn, conn_err = get_db_connection()
    if not db_conn:
        flash(f"Database error: {conn_err}", "danger")
        return redirect(url_for("index"))

    try:
        cursor = db_conn.cursor()

        # Parameterized DELETE query
        sql = "DELETE FROM Customer WHERE Customer_ID = %s;"
        cursor.execute(sql, (customer_id_int,))

        # Check if record actually existed
        if cursor.rowcount == 0:
            db_conn.rollback()
            flash(f"Not Found: No customer found with ID {customer_id_int}. Nothing was deleted.", "warning")
        else:
            # COMMIT deletion transaction
            db_conn.commit()
            flash(f"Success! Customer with ID {customer_id_int} was permanently deleted from MySQL.", "success")

        cursor.close()
        db_conn.close()

    except mysql.connector.Error as err:
        # ROLLBACK transaction
        db_conn.rollback()
        db_conn.close()

        # Foreign key constraint failure (e.g. error 1451)
        if err.errno == 1451 or "foreign key constraint" in err.msg.lower():
            flash(
                f"Referential Integrity Error: Cannot delete Customer ID {customer_id_int} because related records (Lots or Invoices) reference this customer in the database.",
                "danger"
            )
        else:
            flash(f"MySQL Error during DELETE: {err.msg}", "danger")

    return redirect(url_for("index"))


@app.route("/api/customers", methods=["GET"])
def api_get_customers():
    """API endpoint returning customer records in JSON format (useful for tests & verification)"""
    db_conn, conn_err = get_db_connection()
    if not db_conn:
        return jsonify({"success": False, "error": conn_err}), 500

    try:
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Customer ORDER BY Customer_ID ASC;")
        rows = cursor.fetchall()
        cursor.close()
        db_conn.close()
        return jsonify({"success": True, "count": len(rows), "data": rows}), 200
    except mysql.connector.Error as err:
        db_conn.close()
        return jsonify({"success": False, "error": err.msg}), 500


@app.route("/api/db-status", methods=["GET"])
def api_db_status():
    """Health check endpoint to test MySQL connectivity"""
    db_conn, conn_err = get_db_connection()
    if not db_conn:
        return jsonify({"connected": False, "error": conn_err}), 200

    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()[0]
        cursor.close()
        db_conn.close()
        return jsonify({
            "connected": True,
            "database": DB_NAME,
            "version": version,
            "host": DB_HOST,
            "port": DB_PORT
        }), 200
    except Exception as e:
        db_conn.close()
        return jsonify({"connected": False, "error": str(e)}), 200


if __name__ == "__main__":
    # Run the Flask development server on port 5000 with debug disabled for production stability
    print("==================================================================")
    print("Cold Storage Commodity & Chamber Management System (Phase 3 UI)")
    print(f"Connecting to MySQL: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    print("Running on http://127.0.0.1:5000")
    print("==================================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)
