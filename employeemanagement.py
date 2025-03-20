# Author: Hyobin Yook
# employeemanagement.py
# Note: Prepared for CSS475, Winter2025, UWB
# ---------------------------------------------

from api_endpoint import APIEndpoint
import re # Regex model for correct formatting

# ---------------------------
# ListEmployeesAPI (List API)
# Author: Hyobin Yook
# ---------------------------
class ListEmployeesAPI(APIEndpoint):

    #initalize class
    def __init__(self, conn):
        # Database connection and initialize the cursor
        self.conn = conn
        cur = self.conn.cursor()
        try:
            # Prepare the SQL statement for listing employees with optional filters
            cur.execute("""
                PREPARE list_employees(boolean, text, text, text) AS
                SELECT *
                FROM Employee
                WHERE ($1 IS NULL OR (CASE WHEN $1 THEN deactivateddate IS NULL ELSE deactivateddate IS NOT NULL END))
                    AND ($2 IS NULL OR employeenum ILIKE $2)
                    AND ($3 IS NULL OR LOWER(firstName) = LOWER($3))
                    AND ($4 IS NULL OR LOWER(lastName) = LOWER($4))
                ORDER BY employeenum;
            """)

            self.conn.commit()  # Commit the prepare command

        except Exception as e:
            self.conn.rollback() # Rollback the transaction if an error occurs
            print("Error preparing list_employees.") 
        finally:
            cur.close()

    # Function for executing API and collecting user input
    def execute(self):
        # Collect user input for filters
        filter_active = input("Filter: Enter activeStatus (true/false or leave empty for all): ").strip().lower()
        filter_employeeNum = input("Filter: Enter employeeNum ('eg. E0001' or leave empty for all): ").strip().lower()
        filter_firstName = input("Filter: Enter firstName (or leave empty for all): ").strip().lower()
        filter_lastName = input("Filter: Enter lastName (or leave empty for all): ").strip().lower()
        
        # Input validation: Handle input formats and 'quit' command
        if any(field.lower() == "quit" for field in [filter_active, filter_firstName, filter_lastName]):
            print("Operation terminated by user.")
            return  # Exit the API if "quit" is entered
        
        if filter_active == "":
            active_filter = None
        elif filter_active not in {"true", "false"}:
            print("Error: filter_active must be either 'true', 'false', or an empty string (case insensitive).")
            active_filter = None
        else:
            active_filter = filter_active == "true"

        employeenum_filter = filter_employeeNum if filter_employeeNum else None
        firstName_filter = filter_firstName if filter_firstName else None
        lastName_filter = filter_lastName if filter_lastName else None
        
        cur = self.conn.cursor()

        try:
            # Execute the prepared statement with the provided filter(s)
            cur.execute("EXECUTE list_employees(%s, %s, %s, %s);", (active_filter, employeenum_filter, firstName_filter, lastName_filter))
            rows = cur.fetchall()
            
            # Print the results
            print("\nemployeenum | firstname | lastname |    phone     |            email           |  hiredate  | deactivateddate | hourlywage")
            print("------------+-----------+----------+--------------+---------------------------+------------+-----------------+------------")

            for row in rows:
                id, employeenum, firstname, lastname, phone, email, hiredate, deactivateddate, hourlywage = row
                hiredate_str = hiredate.strftime('%Y-%m-%d') if hiredate else None
                deactivateddate_str = deactivateddate.strftime('%Y-%m-%d') if deactivateddate else None

                print(f"{employeenum:11} | {firstname:9} | {lastname:8} | {phone:12} | {email or '':26} | {hiredate_str or '':10} | {deactivateddate_str or '':15} | {hourlywage:9}")

            print(f"({len(rows)} rows)")

        except Exception as e:
            print("Error executing list_employees.")
        finally:
            cur.close()
    
    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. ListEmployees - Lists employee records (optional filters).") 

    # Display details of API and its use
    def display_details(self):
        print("\n--- ListEmployees ---")
        print("Description: Retrieves a list of employee records with optional filters.")
        print("Parameters:")
        print("\t- Employee activeStatus (true/false) or leave empty for all")
        print("\t- employeeNumber or leave empty for all")
        print("\t- firstName or leave empty for all")
        print("\t- lastName or leave empty for all")
        print("Example: ativeStatus = true, firstName = , lastName = ")
        print("-------------------------\n")



# ---------------------------
# CreateEmployeeAPI (Crupdate Single Records API)
# Author: Hyobin Yook
# ---------------------------
class CreateEmployeeAPI(APIEndpoint):
    def __init__(self, conn):
        # Database connection and initialize the cursor
        self.conn = conn
        cur = self.conn.cursor()

    def execute(self):
        # Loop to enfore input of all required fields
        while True:
            print("Enter 'quit' at any time to terminate the operation.")
            print("-------------------------")
            firstName = input("Enter first name: ").strip()
            lastName = input("Enter last name: ").strip()
            phone = input("Enter phone (XXX-XXX-XXXX): ").strip()
            email = input("Enter email: ").strip()
            hireDate = input("Enter hire date (YYYY-MM-DD): ").strip()
            hourlyWage = input("Enter hourly wage: ").strip()
            print("-------------------------")

            # Input validation: Handle formats and 'quit' command
            if any(field.lower() == "quit" for field in [firstName, lastName, phone, email, hireDate, hourlyWage]):
                print("Operation terminated by user.")
                return  # Exit the API if "quit" is entered

            # Ensure all required inputs received
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
                # Prepare the insert statement
                cur.execute("""
                    PREPARE create_employee AS
                    INSERT INTO Employee (firstName, lastName, phone, email, hireDate, hourlyWage)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING employeeNum, firstName, lastName, phone, email, hireDate, hourlyWage;
                """, (firstName, lastName, phone, email, hireDate, hourlyWage))

                # Execute the prepared statement
                cur.execute("EXECUTE create_employee (%s, %s, %s, %s, %s, %s);", 
                            (firstName, lastName, phone, email, hireDate, hourlyWage))
                
                new_employee = cur.fetchone()
                self.conn.commit()
                print(f"Success! Employee created")

                # Print the results
                print("\nemployeenum | firstname | lastname |    phone     |            email           |  hiredate  | hourlywage")
                print("------------+-----------+----------+--------------+----------------------------+------------+------------")
                
                employeeNum, firstName, lastName, phone, email, hireDate, hourlyWage = new_employee
                hireDate_str = hireDate.strftime('%Y-%m-%d') if hireDate else 'N/A'
                
                print(f"{employeeNum:11} | {firstName:9} | {lastName:8} | {phone:12} | {email:26} | {hireDate_str:10} | {hourlyWage:9}")

                break

            except Exception as e:
                self.conn.rollback()
                print("Error creating employee")
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
        print("\nExample: firstName = 'John', lastName = 'Doe', phone = '123-123-1234',")
        print("\temail = 'jd@gmail.com, hireDate = '2025-01-01', hourlyWage = '30'")
        print("----------------------------------------\n")


# ---------------------------
# EditEmployeeAPI (Crupdate Single Records API)
# Author: Hyobin Yook
# ---------------------------
class EditEmployeeAPI(APIEndpoint):
    def __init__(self, conn):
        # Database connection and initialize the cursor
        self.conn = conn
        self.cur = self.conn.cursor()
    
    def execute(self):
        # Collect user input for finding the employee
        employee_number_search = input("Enter Employee Number to search (Eg.'E1234') (leave blank if not applicable): ").strip() or None
        first_name_search = input("Enter First Name to search (leave blank if not applicable): ").strip() or None
        last_name_search = input("Enter Last Name to search (leave blank if not applicable): ").strip() or None
       
        # Check if at least one search parameter is provided
        if not first_name_search and not last_name_search and not employee_number_search:
            print("Please provide at least one search parameter (first name, last name, or employee number).")
            return

        cur = self.conn.cursor()

        # Find & Save the employeeNum based on the provided search criteria 
        employeeNum = None
        try:
            if employee_number_search:
                cur.execute("SELECT employeeNum FROM employee WHERE employeenum iLIKE %s;", (employee_number_search,))
            elif first_name_search and last_name_search:
                cur.execute("SELECT employeeNum FROM employee WHERE firstname = %s AND lastname = %s;", (first_name_search, last_name_search))
            elif first_name_search:
                cur.execute("SELECT employeeNum FROM employee WHERE firstname = %s;", (first_name_search,))
            elif last_name_search:
                cur.execute("SELECT employeeNumd FROM employee WHERE lastname = %s;", (last_name_search,))

            result = cur.fetchone()
            
            if result:
                employeeNum = result[0] # Stored to used in the update query & print updated employee information
            
            else:
                print("Employee not found. Try again.")
                return

        except Exception as e:
            print(f"Error finding employee.")
            return

        print("\n-------------------------")
        print("Provide updated information for the employee. Leave blank to keep current information.")
        first_name = input("Enter First Name (leave blank to keep current): ").strip() or None
        last_name = input("Enter Last Name (leave blank to keep current): ").strip() or None
        phone = input("Enter Phone Number (leave blank to keep current): ").strip() or None
        email = input("Enter Email (leave blank to keep current): ").strip() or None
        hourly_wage = input("Enter Hourly Wage (leave blank to keep current): ").strip() or None
        hire_date = input("Enter Hire Date (YYYY-MM-DD, leave blank to keep current): ").strip() or None
        deactivated_date = input("Enter Deactivated Date (YYYY-MM-DD, leave blank to keep current): ").strip() or None

        print("-------------------------")

        # Input validation: Handle formats and 'quit' command
        if any(item and item.lower() == "quit" for item in [first_name, last_name, phone, email, hourly_wage, hire_date, deactivated_date]):
            print("Operation terminated by user.")
            return
        if phone and (not re.match(r"^\d{3}-\d{3}-\d{4}$", phone)):
                print("Error: Invalid phone number format.")
                return
        if email and ("@" not in email or "." not in email.split("@")[1]):
            print("Error: Invalid email format.")
            return
        if not any([first_name, last_name, phone, email, hourly_wage, hire_date, deactivated_date]):
            return

        # Update employee information
        try:
            cur.execute("BEGIN;") # Begin the transaction block
            update_fields = []
            update_values = []

            if first_name:
                update_fields.append("firstname = %s")
                update_values.append(first_name)
            if last_name:
                update_fields.append("lastname = %s")
                update_values.append(last_name)
            if phone:
                update_fields.append("phone = %s")
                update_values.append(phone)
            if email:
                update_fields.append("email = %s")
                update_values.append(email)
            if hourly_wage:
                update_fields.append("hourlywage = %s")
                update_values.append(hourly_wage)
            if hire_date:
                update_fields.append("hiredate = %s")
                update_values.append(hire_date)
            if deactivated_date:
                update_fields.append("deactivateddate = %s")
                update_values.append(deactivated_date)

            if update_fields:
                update_query = "UPDATE employee SET " + ", ".join(update_fields) + " WHERE employeeNum = %s"
                update_values.append(employeeNum)

                # Prepare and execute the update query
                cur.execute("PREPARE update_employee_prepared AS " + update_query, tuple(update_values))
                cur.execute("EXECUTE update_employee_prepared")
                cur.execute("DEALLOCATE update_employee_prepared")

                self.conn.commit() # Commit the transaction only if the entire operation succeeds
                print("Employee information updated successfully.")

                # Retrieve and print updated employee information ('Prepare' not needed as following the successful update)
                cur.execute("SELECT employeeNum, firstname, lastname, phone, email, hiredate, hourlywage FROM employee WHERE employeeNum = %s", (employeeNum,))
                updated_employee = cur.fetchone()
                if updated_employee:
                    print("\nemployeenum | firstname | lastname |    phone     |            email           |  hiredate  | hourlywage")
                    print("------------+-----------+----------+--------------+----------------------------+------------+------------")

                    employeeNum, firstName, lastName, phone, email, hireDate, hourlyWage = updated_employee
                    hireDate_str = hireDate.strftime('%Y-%m-%d') if hireDate else 'N/A'

                    print(f"{employeeNum:11} | {firstName:9} | {lastName:8} | {phone:12} | {email:26} | {hireDate_str:10} | {hourlyWage:9}")
                else:
                    print("Could not retrieve updated employee information.")
                
            else:
                print("No updates were provided.")

        except Exception as e:
            self.conn.rollback() # Rollback the transaction if an error occurs
            print(f"Error updating employee information. Try again.")

        finally:
            cur.close()
    
    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. EditEmployee - Updates employee information based on first name, last name, or employee number.")

    # Displays details of API and its use
    def display_details(self):
        print("\n--- EditEmployee ---")
        print("Description: Updates employee information based on first name, last name, or employee number.")
        print("Parameters:")
        print("\t- first_name (optional)")
        print("\t- last_name (optional)")
        print("\t- employeeNumber (optional)")
        print("\t- phone (optional)")
        print("\t- email (optional)")
        print("\t- hourly_wage (optional)")
        print("\t- hire_date (optional)")
        print("\t- deactivated_date (optional)")
        print("\tExample: first_name = John, last_name = Doe")
        print("-------------------------\n")