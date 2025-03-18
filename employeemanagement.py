# Author: Hyobin Yook
# employeemanagement.py
# Note: Prepared for CSS475, Winter2025, UWB
# ---------------------------------------------

from api_endpoint import APIEndpoint
import re # Regex model for correct formatting

class ListEmployeesAPI(APIEndpoint):
    #initalize class
    def __init__(self, conn):
        self.conn = conn
        # Prepare the SQL statement for listing employees
        cur = self.conn.cursor()
        try:
            cur.execute("""
                PREPARE list_employees(boolean, text, text) AS
                SELECT *
                FROM Employee
                WHERE ($1 IS NULL OR (CASE WHEN $1 THEN deactivateddate IS NULL ELSE deactivateddate IS NOT NULL END))
                    AND ($2 IS NULL OR LOWER(firstName) = LOWER($2))
                    AND ($3 IS NULL OR LOWER(lastName) = LOWER($3));
            """)

            self.conn.commit()  # Commit the prepare command

        except Exception as e:
            self.conn.rollback()
            print("Error preparing list_employees:", e)
        finally:
            cur.close()

    #display brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. ListEmployees - Lists employee records (optional filters).") 

    def display_details(self):
        print("\n--- ListEmployees ---")
        print("Description: Retrieves a list of employee records with optional filters.")
        print("Parameters:")
        print("\t- Employee activeStatus (true/false) or leave empty for all")
        print("\t- firstName or leave empty for all")
        print("\t- lastName or leave empty for all")
        print("Example: ativeStatus = true, firstName = Meryl, lastName = Streep")
        print("-------------------------\n")

    # Function for executing API and collecting user input
    def execute(self):
        filter_active = input("Enter activeStatus filter (true/false or leave empty for all): ").strip().lower()
        filter_firstName = input("Enter firstName filter (or leave empty for all): ").strip()
        filter_lastName = input("Enter lastName filter (or leave empty for all): ").strip()

        # Convert inputs to proper types: if empty, then use None
        filter_active_lower = filter_active.strip().lower()
        if filter_active_lower == "":
            active_filter = None  # Treat empty string as None
        elif filter_active_lower not in {"true", "false"}:
            print("Error: filter_active must be either 'true', 'false', or an empty string (case insensitive).")
            active_filter = None
        else:
            active_filter = filter_active_lower == "true"
        
        firstName_filter = filter_firstName if filter_firstName else None
        lastName_filter = filter_lastName if filter_lastName else None
        
        cur = self.conn.cursor()

        try:
            cur.execute("EXECUTE list_employees(%s, %s, %s);", (active_filter, firstName_filter, lastName_filter))
            rows = cur.fetchall()

            print("\nid | employeenum | firstname | lastname |    phone     |            email           |  hiredate  | deactivateddate | hourlywage")
            print("----+-------------+-----------+----------+--------------+---------------------------+------------+-----------------+------------")

            for row in rows:
                id, employeenum, firstname, lastname, phone, email, hiredate, deactivateddate, hourlywage = row
                hiredate_str = hiredate.strftime('%Y-%m-%d') if hiredate else None
                deactivateddate_str = deactivateddate.strftime('%Y-%m-%d') if deactivateddate else None

                print(f"{id:2} | {employeenum:11} | {firstname:9} | {lastname:8} | {phone:12} | {email or '':26} | {hiredate_str or '          '} | {deactivateddate_str or '':15} | {hourlywage:9}")

            print(f"({len(rows)} rows)")

        except Exception as e:
            print("Error executing list_employees:", e)
        finally:
            cur.close()


# ---------------------------
# CreateEmployeeAPI using prepared statement and transactions inline
# ---------------------------
class CreateEmployeeAPI(APIEndpoint):
    # Initialize Class Instance
    def __init__(self, conn):
        self.conn = conn

    def execute(self):
        while True:
            firstName = input("Enter first name: ").strip()
            lastName = input("Enter last name: ").strip()
            phone = input("Enter phone (XXX-XXX-XXXX): ").strip()
            email = input("Enter email: ").strip()
            hireDate = input("Enter hire date (YYYY-MM-DD): ").strip()
            hourlyWage = input("Enter hourly wage: ").strip()

            # Input validation
            # Check if any field is "quit"
            if any(field.lower() == "quit" for field in [firstName, lastName, phone, email, hireDate, hourlyWage]):
                print("Termination Request received: exiting API...")
                return  # Exit the API if "quit" is entered

            # Check if any field is empty
            if not firstName or not lastName or not phone or not email or not hireDate or not hourlyWage:
                print("Error: All fields are required. Please re-enter the details.")
                continue  # Re-execute the loop

            if not re.match(r"^\d{3}-\d{3}-\d{4}$", phone):
                print("Error: Invalid phone number format.")
                return
            
            if "@" not in email or "." not in email.split("@")[1]:
                print("Error: Invalid email format.")
                return

            try:
                cur = self.conn.cursor()

                # Define the prepared statement inside the execution function
                cur.execute("""
                    PREPARE create_employee AS
                    INSERT INTO Employee (firstName, lastName, phone, email, hireDate, hourlyWage)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING employeeNum;
                """)

                # Execute the prepared statement
                cur.execute("EXECUTE create_employee (%s, %s, %s, %s, %s, %s);", 
                            (firstName, lastName, phone, email, hireDate, hourlyWage))
                
                employee_number = cur.fetchone()[0]
                self.conn.commit()
                print(f"Success! Employee created with EmployeeNumber: {employee_number}")
                break

            except Exception as e:
                self.conn.rollback()
                print("Error creating employee:", e)
                break
            finally:
                cur.close()
    
    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. CreateEmployee - Adds a new employee record.")

    # Display details of API and its use
    def display_details(self):
        print("\n--- CreateEmployee ---")
        print("Description: Creates a new employee record.")
        print("Parameters:")
        print("\t- firstName (text)")
        print("\t- lastName (text)")
        print("\t- phone (text, format: XXX-XXX-XXXX)")
        print("\t- email (text, unique)")
        print("\t- hireDate (date, format: YYYY-MM-DD)")
        print("\t- hourlyWage (money)")
        print("Returns: EmployeeNumber if successful, errorMessage if fails.")
        print("----------------------------------------\n")


# ---------------------------
# EditEmployeeAPI using prepared statement and transactions inline
# ---------------------------
class EditEmployeeAPI(APIEndpoint):
    def __init__(self, conn):
        self.conn = conn

    def search_employee(self, cur, first_name=None, last_name=None):
        """Search for an employee based on given parameters."""
        query = "SELECT employeenum FROM employee WHERE "
        conditions = []
        values = []

        if first_name:
            conditions.append("firstname = %s")
            values.append(first_name)
        if last_name:
            conditions.append("lastname = %s")
            values.append(last_name)

        if not conditions:
            return []  # No conditions means no search

        query += " AND ".join(conditions)
        cur.execute(query, values)
        return cur.fetchall()

    def execute(self):
        cur = self.conn.cursor()
        try:
            # Prepare the SQL query dynamically in the execute method
            cur.execute("""
                PREPARE edit_employee(text, text, text, text, text, money, date, date) AS
                UPDATE employee
                SET 
                    firstname = COALESCE($2, firstname),
                    lastname = COALESCE($3, lastname),
                    phone = COALESCE($4, phone),
                    email = COALESCE($5, email),
                    hourlywage = COALESCE($6, hourlywage),
                    hiredate = COALESCE($7, hiredate),
                    deactivateddate = COALESCE($8, deactivateddate)
                WHERE employeenum = $1
                RETURNING employeenum;
            """)
            self.conn.commit()

            # Prompt for employee number or name search
            employee_number = input("Enter Employee Number (leave blank to search by name): ").strip()

            if not employee_number:
                first_name = input("Enter First Name (leave blank to search by Last Name): ").strip()
                search_results = self.search_employee(cur, first_name=first_name)

                if not first_name or len(search_results) > 1:
                    last_name = input("Enter Last Name: ").strip()
                    search_results = self.search_employee(cur, first_name=first_name, last_name=last_name)

                if len(search_results) == 1:
                    employee_number = search_results[0][0]
                else:
                    print("ERROR: No employee found by the information. Try again.")
                    return

            print("\n-------------------------")

            first_name = input("Enter First Name (leave blank to keep current): ").strip() or None
            last_name = input("Enter Last Name (leave blank to keep current): ").strip() or None
            phone = input("Enter Phone Number (leave blank to keep current): ").strip() or None
            email = input("Enter Email (leave blank to keep current): ").strip() or None
            hourly_wage = input("Enter Hourly Wage (leave blank to keep current): ").strip() or None
            hire_date = input("Enter Hire Date (YYYY-MM-DD, leave blank to keep current): ").strip() or None
            deactivated_date = input("Enter Deactivated Date (YYYY-MM-DD, leave blank to keep current): ").strip() or None

            print("-------------------------")

            # Execute the prepared statement with employee_number and update values
            cur.execute("EXECUTE edit_employee(%s, %s, %s, %s, %s, %s, %s, %s)",
                        (employee_number, first_name, last_name, phone, email, hourly_wage, hire_date, deactivated_date))
            result = cur.fetchone()
            self.conn.commit()

            if result:
                print(f"\nEmployee {result[0]} updated successfully.")
                return {"confirmation": f"Employee {result[0]} updated successfully."}
            else:
                print("Error: Employee not found.")
                return {"errorMessage": "EmployeeNumber not found."}
            
        except Exception as e:
            self.conn.rollback()
            print("Error updating employee:", e)
            return {"errorMessage": str(e)}
        
        finally:
            cur.close()

    def display_brief(self, index):
        print(f"{index}. EditEmployee - Updates an existing employee record.")

    def display_details(self):
        print("\n--- EditEmployee ---")
        print("Description: Updates details of an existing employee. Only provided fields are updated.")
        print("Parameters:")
        print("\t- firstName (text, optional)")
        print("\t- lastName (text, optional)")
        print("\t- phone (text, optional)")
        print("\t- email (text, optional)")
        print("\t- hourlyWage (money, optional)")
        print("\t- hireDate (date, optional)")
        print("\t- deactivatedDate (date, optional)")
        print("Returns: { confirmation of update, errorMessage if EmployeeNumber, firstName, or lastName not found }")
        print("-------------------------\n")
