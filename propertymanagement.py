# propertymanagement.py

from api_endpoint import APIEndpoint

#********************************************************************************
#********************************************************************************

#List API
class ListPropertiesAPI(APIEndpoint):
    def __init__(self, conn):
        self.conn = conn

    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. ListProperties - Lists property records (optional filters).")

    # Displays details of API and its use
    def display_details(self):
        print("\n--- ListProperties ---")
        print("Description: Retrieves a list of property records. You may optionally filter by activeStatus and city.")
        print("Parameters: ")
        print("\t- activeStatus (true/false)") 
        print("\t- city")
        print("\t- Example: activeStatus = true, city = Seattle")
        print("-------------------------\n")

    # Function for executing API
    def execute(self):
        # EXAMPLE PSQL QUERY FOR REFERENCE:
        # SELECT * FROM Property;

        filter_active = input("Enter activeStatus filter (true/false or leave empty for all): ").strip()
        filter_city = input("Enter city filter (or leave empty for all): ").strip()

        # Create Query for Database
        query = "SELECT * FROM Property"
        conditions = []
        if filter_active:
            conditions.append(f"activestatus = {filter_active}")
        if filter_city:
            conditions.append(f"city = '{filter_city}'")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += ";"

        cur = self.conn.cursor()
        try:
            cur.execute(query)
            rows = cur.fetchall()
            print("\nList of Properties:")
            
            for row in rows:
                # Assuming columns: id, clientID, propertyTypeID, propertyNumber, streetAddress, streetAddress2, city, stateID, zipcode, activeStatus
                print(f"PropertyNumber: {row[3]}" )
                print(f"StreetAddress: {row[4]}" )
                print(f"StreetAddress2: {row[5]}" )
                print(f"City: {row[6]}" )
                print(f"State: {row[7]}" )
                print(f"Zipcode: {row[8]}" )
                print("\n")

        except Exception as e:
            print("Error executing query:", e)

        finally:
            cur.close()

#********************************************************************************
#********************************************************************************

#Detail API
class DetailPropertyAPI(APIEndpoint):
    def __init__(self, conn):
        self.conn = conn
    
    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. DetailProperty - Shows details for a given property and Client information")

    # Displays details of API and its use
    def display_details(self):
        print("\n--- DetailProperty ---")
        print("Description: Retrieves full details for a property identified by propertyNumber.")
        print("Parameters:")
        print("\t- propertyNumber (string)")
        print("\t- Example: DetailProperty('P00001')")
        print("----32---------------------\n")

    # Function for executing API
    def execute(self):
        #EXAMPLE PSQL QUERY FOR REFERENCE 
        # SELECT *
        # FROM Property
        #       JOIN Client ON (Property.clientid = Client.id)
        # WHERE propertynumber = 'P002';

        # Create query for database
        property_number = input("Enter property number: ").strip()
        query = f"SELECT * FROM Property JOIN Client ON (Property.clientID = Client.id) WHERE propertynumber = '{property_number}';"
        cur = self.conn.cursor()
        
        # Try to execute the query
        try:
            cur.execute(query)
            rows = cur.fetchall()
            print("Property Details")
            
            # Print details on each API
            for row in rows:
                print(f"PropertyNumber: {row[3]}" )
                print(f"StreetAddress: {row[4]}" )
                print(f"StreetAddress2: {row[5]}" )
                print(f"City: {row[6]}" )
                print(f"State: {row[7]}" )
                print(f"Zipcode: {row[8]}" )
                print(f"Property Type: ") # FIXME: NEED TO ADD PROPER ROW FOR THIS
                print(f"Client Name: {row[12]} {row[13]}" )
                print(f"Account Number: {row[11]}" )
                print("\n")

        except Exception as e:
            print("Error executing query:", e)

        finally:
            cur.close() 

#********************************************************************************
#********************************************************************************

#Crupdate Single Record API

#********************************************************************************
#********************************************************************************

#Crupdate Multiple API
class CrupdateMultiplePropertiesAPI(APIEndpoint):
    def __init__(self, conn):
        self.conn = conn

    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. CrupdateMultipleProperties - Update multiple property records for a client.")

    # Displays details of API and its use
    def display_details(self):
        print("\n--- CrupdateMultipleProperties ---")
        print("Description: Updates activeStatus for all properties belonging to a specific client.")
        print("Parameters:")
        print("\t- accountNumber")
        print("\t- new activeStatus (true/false)")
        print("\t- Example: accountNumber = C0002, activeStatus = false")
        print("-------------------------\n")

    # Function for executing API
    def execute(self):
        # Prompt for the accountNumber and the new activeStatus
        accountNumber = input("Enter client account number to update properties: ").strip()
        newStatus = input("Enter new activeStatus (true/false): ").strip().lower()
        
        # Create a cursor for executing queries
        cur = self.conn.cursor()
        try:
            # 1. Validate the accountNumber and retrieve the surrogate clientID
            cur.execute("SELECT id FROM Client WHERE accountnumber = %s;", (accountNumber,))
            client = cur.fetchone()
            if client is None:
                print("Invalid account number. No such client exists.")
                return
            clientID = client[0]
            
            # 2. Begin the transaction and perform the update
            # (psycopg2 manages transactions automatically; if an error occurs, we'll roll back)
            cur.execute("UPDATE Property SET activeStatus = %s WHERE clientID = %s;", (newStatus, clientID))
            
            # 3. After updating, fetch all properties for this client to show the changes
            cur.execute("SELECT propertynumber, streetaddress, activeStatus FROM Property WHERE clientID = %s;", (clientID,))
            properties = cur.fetchall()
            
            # 4. Commit the transaction.
            self.conn.commit()
            print("Operation successful: Updated multiple records.\n")
            
            # 5. Print out the updated property information.
            print("Updated Properties:")
            for prop in properties:
                print(f"PropertyNumber: {prop[0]}, StreetAddress: {prop[1]}") 
                print(f"ActiveStatus: {prop[2]}\n")

        except Exception as e:
            print("Error during update:", e)
            self.conn.rollback()

        finally:
            cur.close()
