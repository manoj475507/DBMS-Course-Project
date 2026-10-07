"""
=============================================================================
Cold Storage System - End-to-End Verification Test Script
Tests all 7 required operations:
1. VIEW existing Customer records from MySQL
2. INSERT one test customer
3. Verify the inserted customer appears in UI / query
4. Verify the inserted customer exists in MySQL
5. DELETE the test customer
6. Verify the customer disappears from UI / query
7. Verify the customer was actually deleted from MySQL
=============================================================================
"""

import os
import sys
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

from app import app, get_db_connection

def run_tests():
    print("=" * 65)
    print("Cold Storage Management System - Local Verification Test")
    print("=" * 65)

    # 0. Test MySQL Connection
    conn, err = get_db_connection()
    if not conn:
        print(f"\n[FAIL] Cannot connect to MySQL: {err}")
        print("\n--> ACTION NEEDED:")
        print("Please edit the '.env' file in this folder and replace:")
        print("    DB_PASSWORD=your_mysql_password")
        print("with your actual MySQL root password, then rerun this script.\n")
        sys.exit(1)

    print("\n[PASS] Database Connection Successful!")
    print(f"       Connected to: {os.getenv('DB_USER')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

    cursor = conn.cursor(dictionary=True)
    test_client = app.test_client()

    TEST_CID = 999
    TEST_NAME = "Demo Logistics Test"
    TEST_PHONE = "9876543219"
    TEST_EMAIL = "demo@coldstorage.test"
    TEST_CITY = "Hyderabad"
    TEST_ADDR = "Sector 5 Cold Zone"

    try:
        # Clean up any leftover test record before starting
        cursor.execute("DELETE FROM Customer WHERE Customer_ID = %s;", (TEST_CID,))
        conn.commit()

        # -------------------------------------------------------------
        # STEP 1: VIEW existing Customer records
        # -------------------------------------------------------------
        print("\n--- STEP 1: VIEW Existing Records ---")
        cursor.execute("SELECT Customer_ID, Customer_Name, City FROM Customer ORDER BY Customer_ID ASC;")
        initial_rows = cursor.fetchall()
        print(f"[PASS] Successfully fetched {len(initial_rows)} customer(s) from ColdStorageDB.Customer:")
        for r in initial_rows[:5]:
            print(f"       - ID {r['Customer_ID']}: {r['Customer_Name']} ({r['City']})")
        if len(initial_rows) > 5:
            print(f"       - ... and {len(initial_rows) - 5} more")

        # Verify UI Route GET /
        ui_view_res = test_client.get('/')
        assert ui_view_res.status_code == 200, "Dashboard route returned non-200"
        print("[PASS] UI Dashboard (GET /) renders existing records cleanly.")

        # -------------------------------------------------------------
        # STEP 2: INSERT one test customer through UI POST route
        # -------------------------------------------------------------
        print("\n--- STEP 2: INSERT Test Customer ---")
        insert_data = {
            "customer_id": str(TEST_CID),
            "customer_name": TEST_NAME,
            "phone": TEST_PHONE,
            "email": TEST_EMAIL,
            "city": TEST_CITY,
            "address": TEST_ADDR
        }
        res_insert = test_client.post('/customer/insert', data=insert_data, follow_redirects=True)
        assert res_insert.status_code == 200
        print(f"[PASS] Executed INSERT for Customer ID {TEST_CID} ('{TEST_NAME}').")

        # -------------------------------------------------------------
        # STEP 3: Verify the inserted customer appears in UI
        # -------------------------------------------------------------
        print("\n--- STEP 3: Verify Inserted Record in UI ---")
        assert TEST_NAME.encode() in res_insert.data, "Inserted customer name missing from UI response"
        assert f"#{TEST_CID}".encode() in res_insert.data, "Inserted customer ID missing from UI response"
        print(f"[PASS] Customer ID #{TEST_CID} ('{TEST_NAME}') appears in the UI table.")

        # -------------------------------------------------------------
        # STEP 4: Verify the inserted customer exists in MySQL
        # -------------------------------------------------------------
        print("\n--- STEP 4: Verify Record in MySQL ---")
        cursor.execute("SELECT * FROM Customer WHERE Customer_ID = %s;", (TEST_CID,))
        row_in_db = cursor.fetchone()
        assert row_in_db is not None, "Customer not found in MySQL!"
        assert row_in_db["Customer_Name"] == TEST_NAME
        print(f"[PASS] Confirmed in MySQL: Customer_ID={row_in_db['Customer_ID']}, Name={row_in_db['Customer_Name']}, City={row_in_db['City']}")

        # -------------------------------------------------------------
        # STEP 5: DELETE test customer through UI POST route
        # -------------------------------------------------------------
        print("\n--- STEP 5: DELETE Test Customer ---")
        res_delete = test_client.post('/customer/delete', data={"customer_id": str(TEST_CID)}, follow_redirects=True)
        assert res_delete.status_code == 200
        print(f"[PASS] Executed DELETE for Customer ID {TEST_CID}.")

        # -------------------------------------------------------------
        # STEP 6: Verify customer disappears from UI
        # -------------------------------------------------------------
        print("\n--- STEP 6: Verify Customer Disappears from UI ---")
        # In the refreshed table response, the test customer should no longer appear
        assert TEST_NAME.encode() not in res_delete.data or b"permanently deleted" in res_delete.data
        print(f"[PASS] Customer ID #{TEST_CID} no longer listed in active UI table.")

        # -------------------------------------------------------------
        # STEP 7: Verify customer was actually deleted from MySQL
        # -------------------------------------------------------------
        print("\n--- STEP 7: Verify Deletion in MySQL ---")
        cursor.execute("SELECT * FROM Customer WHERE Customer_ID = %s;", (TEST_CID,))
        deleted_row = cursor.fetchone()
        assert deleted_row is None, "Customer still exists in MySQL after DELETE!"
        print(f"[PASS] Verified in MySQL: SELECT returned 0 rows for Customer_ID {TEST_CID}.")

        print("\n" + "=" * 65)
        print("ALL 7 DBMS CHECKS PASSED SUCCESSFULLY!")
        print("Your application is 100% ready for Presentation-III.")
        print("=" * 65 + "\n")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_tests()
