#propertymanagement.py

from api_endpoint import APIEndpoint



# ---------------------------
# ListPropertiesAPI using prepared statement inline
# ---------------------------
class ListPropertiesAPI(APIEndpoint):
    # Initialize Class Instance
    def __init__(self, conn):
        self.conn = conn
        # Prepare the SQL statement for listing properties.
        # This statement returns all columns from Property. It filters by activeStatus and city,
        # using bind variables ($1 and $2) and allowing for NULL values (which disable filtering).
        cur = self.conn.cursor()
        try:
            cur.execute("""
                PREPARE list_properties(boolean, text) AS
                SELECT *
                FROM Property
                WHERE ($1 IS NULL OR activeStatus = $1)
                    AND ($2 IS NULL OR city = $2);
            """)
            self.conn.commit() # Commit the prepare command
        except Exception as e:
            self.conn.rollback()
            print("Error preparing list_properties:", e)
        finally:
            cur.close()


    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. ListProperties - Lists property records (optional filters).")


    # Displays details of API and its use
    def display_details(self):
        print("\n--- ListProperties ---")
        print("Description: Retrieves a list of property records with optional filters.")
        print("Parameters:")
        print("\t- activeStatus (true/false) or leave empty for all")
        print("\t- city or leave empty for all")
        print("\tExample: activeStatus = true, city = Seattle")
        print("-------------------------\n")


    # Function for executing API and collecting user input
    def execute(self):
        filter_active = input("Enter activeStatus filter (true/false or leave empty for all): ").strip().lower()
        filter_city = input("Enter city filter (or leave empty for all): ").strip()

        # Convert inputs to proper types: if empty, then use None (which becomes SQL NULL)
        if filter_active == "":
            active_filter = None
        elif filter_active == "true":
            active_filter = True
        elif filter_active == "false":
            active_filter = False
        else:
            print("Invalid activeStatus input. Use true or false.")
            return

        city_filter = filter_city if filter_city != "" else None

        cur = self.conn.cursor()
        try:
            # Execute the prepared statement "list_properties" with parameters
            cur.execute("EXECUTE list_properties(%s, %s);", (active_filter, city_filter))
            rows = cur.fetchall()
            
            # Display Results
            print("\nList of Properties:")
            for row in rows: # Iterates through each row in table
                print(f"PropertyNumber: {row[3]}")
                print(f"StreetAddress: {row[4]}")
                print(f"StreetAddress2: {row[5]}")
                print(f"City: {row[6]}")
                print(f"State: {row[7]}")
                print(f"Zipcode: {row[8]}")
                print("\n")
        except Exception as e:
            print("Error executing prepared statement:", e)
        finally:
            cur.close()




# ---------------------------
# DetailPropertyAPI using prepared statement inline
# ---------------------------
class DetailPropertyAPI(APIEndpoint):
    # Initialize Class Instance
    def __init__(self, conn):
        self.conn = conn
        # Prepare the SQL statement for retrieving property details.
        # This join returns columns from both Property and Client tables.
        cur = self.conn.cursor()
        try:
            cur.execute("""
                PREPARE detail_property(text) AS
                SELECT *
                FROM Property
                    JOIN Client ON (Property.clientID = Client.id)
                WHERE propertynumber = $1;
            """)
            self.conn.commit() # Commit the prepare command
        except Exception as e:
            self.conn.rollback()
            print("Error preparing detail_property:", e)
        finally:
            cur.close()


    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. DetailProperty - Shows details for a given property with client ownership information")


    # Displays details of API and its use
    def display_details(self):
        print("\n--- DetailProperty ---")
        print("Description: Retrieves full details for a property identified by propertyNumber.")
        print("Parameters:")
        print("\t- propertyNumber (string)")
        print("\tExample: DetailProperty = P0001")
        print("-------------------------\n")


    # Function for executing API and collecting user input
    def execute(self):
        property_number = input("Enter property number: ").strip()
        cur = self.conn.cursor()
        try:
            # Execute the prepared statement "detail_property" with the provided property number
            cur.execute("EXECUTE detail_property(%s);", (property_number,))
            rows = cur.fetchall()
            
            # Display Results
            print("Property Details:")
            for row in rows: # Iterates through each row in table
                print(f"PropertyNumber: {row[3]}")
                print(f"StreetAddress: {row[4]}")
                print(f"StreetAddress2: {row[5]}")
                print(f"City: {row[6]}")
                print(f"State: {row[7]}")
                print(f"Zipcode: {row[8]}")
                print(f"Client Name: {row[12]} {row[13]}")
                print(f"Account Number: {row[11]}")
                print(f"Explanation: {row[-1]}")
                print("\n")
        except Exception as e:
            print("Error executing prepared statement:", e)
        finally:
            cur.close()




# ---------------------------
# CrupdateMultiplePropertiesAPI using prepared statement and transactions inline
# ---------------------------
class CrupdateMultiplePropertiesAPI(APIEndpoint):
    # Initialize Class Instance
    def __init__(self, conn):
        self.conn = conn
        # Prepare the SQL statement for updating properties
        cur = self.conn.cursor()
        try:
            cur.execute("""
                PREPARE update_properties(text, boolean) AS
                UPDATE Property
                SET activeStatus = $2
                WHERE clientID = (
                        SELECT id 
                        FROM Client 
                        WHERE accountNumber = $1
                    )
                RETURNING propertynumber, streetaddress, activeStatus, 'UpdateProperties executed' AS explanation;
            """)
            self.conn.commit() # Commit the prepare command
        except Exception as e:
            self.conn.rollback()
            print("Error preparing update_properties:", e)
        finally:
            cur.close()

    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. CrupdateMultipleProperties - Update multiple property records for a client.")

    # Displays details of API and its use
    def display_details(self):
        print("\n--- CrupdateMultipleProperties ---")
        print("Description: Updates activeStatus for all properties belonging to a specific client.")
        print("Parameters:")
        print("\t- accountNumber (string)")
        print("\t- new activeStatus (true/false)")
        print("\tExample: accountNumber = C0002, activeStatus = false")
        print("-------------------------\n")

    # Function for executing API
    def execute(self):
        accountNumber = input("Enter client account number to update properties: ").strip()
        new_status_input = input("Enter new activeStatus (true/false): ").strip().lower()
        if new_status_input not in ["true", "false"]:
            print("Invalid input for activeStatus. Please enter true or false.")
            return
        new_status = True if new_status_input == "true" else False

        cur = self.conn.cursor()
        try:
            # Begin a transaction
            cur.execute("BEGIN;")
            
            # Execute the prepared statement "update_properties" with parameters
            cur.execute("EXECUTE update_properties(%s, %s);", (accountNumber, new_status))
            updated_rows = cur.fetchall()
            self.conn.commit()
            print("Operation successful: Updated multiple records.\n")
            
            # Display Results
            print("Updated Properties:")
            for prop in updated_rows:
                print(f"PropertyNumber: {prop[0]}, StreetAddress: {prop[1]}, ActiveStatus: {prop[2]}")
                print(f"Explanation: {prop[-1]}")
        except Exception as e:
            self.conn.rollback()
            print("Error during update:", e)
        finally:
            cur.close()
