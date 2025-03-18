#propertymanagement.py

from api_endpoint import APIEndpoint

# ---------------------------
# ListPropertiesAPI (List API)
# ---------------------------
class ListPropertiesAPI(APIEndpoint):
    # Initialize Class Instance
    def __init__(self, conn):
        self.conn = conn            # Store the database connection
        cur = self.conn.cursor()    # Create a cursor object for executing SQL statements
        
        # Prepare the SQL statement for listing properties
        # This statement explicitly selects the columns we want to display from Property and Client tables.
        # It filters by active status, city, and client account number using bind variables ($1, $2, and $3),
        # allowing for NULL values to disable filtering.
        try:
            cur.execute("""
                PREPARE list_properties(boolean, text, text) AS
                SELECT 
                    P.propertynumber,  -- unique identifier visible to the user
  	                P.streetaddress, 	
 	                P.streetaddress2, 
    	            P.city, 
   	                P.stateid,         -- state code (not a surrogate key)
    	            P.zipcode, 
  	                P.activestatus,
	                C.firstname,
	                C.lastname,
	                C.accountnumber
                FROM Property P
	                JOIN Client C ON (P.clientid = C.id)
                WHERE ($1 IS NULL OR P.activestatus = $1)
                    AND ($2 IS NULL OR P.city = $2)
                    AND ($3 IS NULL OR C.accountnumber = $3);
            """)
            self.conn.commit()  # Commit the prepare command

        # Print error message if the prepare command fails
        except Exception as e:
            self.conn.rollback()
            print("Error preparing list_properties PREPARE statement")
        
        # Close the cursor
        finally:
            cur.close()


    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. ListProperties - Lists property records and client ownership (optional filters).")


    # Displays details of API and its use
    def display_details(self):
        print("\n--- ListProperties ---")
        print("Description: Retrieves a list of property records with optional filters. Lists the client's name and account number.")
        print("Parameters:")
        print("\t- active status (true/false) or leave empty for all")
        print("\t- city name or leave empty for all (case-sensitive)")
        print("\t- client account number or leave empty for all")
        print("\tExample: activeStatus = true, city = Seattle, account number = C0001")
        print("-------------------------\n")


    # Function for executing API and collecting user input
    def execute(self):
        # Collect user input for filtering properties listed
        filter_active = input("Enter active status filter (true/false or leave empty for all): ").strip().lower()
        filter_city = input("Enter city filter (or leave empty for all): ").strip()
        filter_account = input("Enter client account number filter (or leave empty for all): ").strip()

        # Convert inputs to proper types: if empty, then use None (which becomes SQL NULL)
        if filter_active == "":
            active_filter = None
        elif filter_active == "true":
            active_filter = True
        elif filter_active == "false":
            active_filter = False
        else:
            print("Invalid active status input. Use true, false, or leave empty for all.")
            return

        # If city filter is empty, set it to None (no filtering by city)
        city_filter = filter_city if filter_city != "" else None
        # If client account number filter is empty, set it to None (no filtering by account number)
        account_filter = filter_account if filter_account != "" else None

        cur = self.conn.cursor()  # Create a cursor object for executing SQL statements
        
        # Execute the prepared statement "list_properties" with parameters
        try:
            cur.execute("EXECUTE list_properties(%s, %s, %s);", (active_filter, city_filter, account_filter))
            rows = cur.fetchall()
            
            # Display Results
            print("\nList of Properties:")
            for row in rows:  # Iterate over the result rows
                print(f"Property Number:\t{row[0]}")
                print(f"Street Address:\t\t{row[1]}")
                print(f"Street Address2:\t{row[2]}")
                print(f"City:\t\t\t{row[3]}")
                print(f"State:\t\t\t{row[4]}")
                print(f"Zipcode:\t\t{row[5]}")
                print(f"Active Property:\t{row[6]}")
                print(f"Owner:\t\t\t{row[7]} {row[8]}")
                print(f"Owner Account Number:\t{row[9]}")
                print("\n")
        
        # Print error message if the execute command fails
        except Exception as e:
            print("Error executing prepared statement:")
       
        # Close the cursor
        finally:
            cur.close()




# ---------------------------
# UpdateClientPropertiesAPI (Crupdate Multiple Records API) 
# ---------------------------
class UpdateClientPropertiesAPI(APIEndpoint):
    # Initialize Class Instance
    def __init__(self, conn):
        self.conn = conn            # Store the database connection
        cur = self.conn.cursor()    # Create a cursor object for executing SQL statements
        # Prepare the SQL statement for updating properties
        try:
            cur.execute("""
                PREPARE update_properties(text, boolean) AS
                UPDATE property
                SET activestatus = $2
                WHERE clientid = (
                    SELECT id 
                    FROM client 
                    WHERE accountnumber = $1
                )
                RETURNING propertynumber, streetaddress, activestatus, 'UpdateProperties executed' AS explanation;
            """)
            self.conn.commit()  # Commit the prepare command

        # Print error message if the prepare command fails
        except Exception as e:
            self.conn.rollback()
            print("Error preparing update_properties PREPARE statement")

        # Close the cursor
        finally:
            cur.close()


    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. UpdateClientProperties - Updates activeStatus for all property records for a client.")


    # Displays details of API and its use
    def display_details(self):
        print("\n--- UpdateClientProperties ---")
        print("Description: Updates active status for all properties belonging to a specific client found via their account number.")
        print("Parameters:")
        print("\t- accountNumber")
        print("\t- new activeStatus (true/false)")
        print("\tExample: accountNumber = C0015, active status = false")
        print("-------------------------\n")


    # Function for executing API
    def execute(self):
        # Collect user input for updating properties
        account_number = input("Enter client account number to update properties: ").strip()
        new_status_input = input("Enter new activeStatus (true/false): ").strip().lower()

        # Validate the input for activeStatus
        if new_status_input not in ["true", "false"]:
            print("Invalid input for active status. Please enter true or false.")
            return
        new_status = True if new_status_input == "true" else False # Convert input to boolean

        cur = self.conn.cursor() # Create a cursor object for executing SQL statements
        
        # Try to update the properties
        try:
            cur.execute("BEGIN;") # Begin the transaction block
            
            # Execute the prepared statement "update_properties" with the given parameters
            cur.execute("EXECUTE update_properties(%s, %s);", (account_number, new_status))
            updated_rows = cur.fetchall() # Fetch all the updated rows
            self.conn.commit() # Commit the transaction only if the entire operation succeeds
            print("Operation successful: Updated multiple records.\n")
            
            # Display the updated properties
            print("Updated Properties:")

            # Display the updated properties
            for prop in updated_rows:
                print(f"PropertyNumber: {prop[0]}, StreetAddress: {prop[1]}, ActiveStatus: {prop[2]}")
                print(f"Explanation: {prop[-1]}")
        
        # Roll back the transaction to ensure data integrity if an error occurs
        except Exception as e:
            # Roll back the transaction to ensure data integrity if an error occurs
            self.conn.rollback()
            print("Error during update")

        # Close the cursor
        finally:
            cur.close()


