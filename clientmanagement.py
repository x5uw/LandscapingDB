# clientmanagement.py

from api_endpoint import APIEndpoint

# ---------------------------
# CreateClientAPI using prepared statement inline
# ---------------------------
class CreateClientAPI(APIEndpoint):
    # Initialize Class Instance
    def __init__(self, conn):
        self.conn = conn
        # Create a sequence for generating account numbers if it doesn't exist
        cur = self.conn.cursor()
        try:
            # create the sequence
            cur.execute("""
                CREATE SEQUENCE IF NOT EXISTS client_account_seq
                START WITH 1
                INCREMENT BY 1
                NO MINVALUE
                NO MAXVALUE
                CACHE 1;
            """)
            self.conn.commit()
            
            # prepare the statement
            cur.execute("""
                PREPARE create_client(text, text, text, text, boolean) AS
                INSERT INTO Client (accountNumber, firstName, lastName, phoneNumber, email, activeStatus)
                VALUES (
                    'C' || LPAD(CAST(nextval('client_account_seq') AS TEXT), 4, '0'), 
                    $1, 
                    $2, 
                    $3, 
                    $4, 
                    $5
                )
                RETURNING accountNumber;
            """)
            self.conn.commit()
            print("Prepared statement 'create_client' created successfully")
        except Exception:
            self.conn.rollback()
            print("Error preparing create_client statement.")
        finally:
            cur.close()

    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. CreateClient - Creates a new client in the system.")

    # Displays details of API and its use
    def display_details(self):
        print("\n--- CreateClient ---")
        print("Description: Creates a new client record in the system. Each client is assigned a unique account number upon creation.")
        print("Parameters:")
        print("\t- firstName (string): Client's first name")
        print("\t- lastName (string): Client's last name")
        print("\t- phoneNumber (string): Client's phone number (10 digits)")
        print("\t- email (string): Client's email address")
        print("\t- activeStatus (true/false): Whether the client is active")
        print("\tExample: firstName = John, lastName = Doe, phoneNumber = 5551234567, email = john.doe@example.com, activeStatus = true")
        print("-------------------------\n")

    # Function for executing API and collecting user input
    def execute(self):
        firstName = input("Enter client's first name: ").strip()
        lastName = input("Enter client's last name: ").strip()
        phoneNumber = input("Enter client's phone number: ").strip()
        email = input("Enter client's email: ").strip()
        activeStatus_input = input("Enter client's active status (true/false): ").strip().lower()
        
        # Input validation
        if not firstName or not lastName or not phoneNumber:
            print("Error: First name, last name, and phone number are required.")
            return
            
        if activeStatus_input not in ["true", "false"]:
            print("Error: Active status must be 'true' or 'false'.")
            return
            
        activeStatus = True if activeStatus_input == "true" else False

        cur = self.conn.cursor()
        try:
            # Begin a transaction
            cur.execute("BEGIN;")
            
            # Find the highest account number value to ensure uniqueness
            cur.execute("SELECT MAX(CAST(SUBSTRING(accountNumber, 2) AS INTEGER)) FROM Client")
            max_account_num = cur.fetchone()[0]
            
            # Default to 0 if no clients exist yet
            if max_account_num is None:
                max_account_num = 0
                
            # Create next account number by incrementing the highest existing one
            new_account_num = max_account_num + 1
            account_number = f"C{new_account_num:04d}"
            
            # Insert the new client
            cur.execute("""
                INSERT INTO Client (accountNumber, firstName, lastName, phoneNumber, email, activeStatus)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING accountNumber;
            """, (account_number, firstName, lastName, phoneNumber, email, activeStatus))
            
            # Get the result (the new account number)
            result = cur.fetchone()
            accountNumber = result[0] if result else None
            
            self.conn.commit()
            
            # Display Results
            if accountNumber:
                print(f"\nClient created successfully!")
                print(f"Account Number: {accountNumber}")
            else:
                print("Error: Failed to create client.")
                
        except Exception:
            self.conn.rollback()
            print("Error creating client. Please try again.")
        finally:
            cur.close()


# ---------------------------
# UpdateClientAPI using prepared statement inline
# ---------------------------
class UpdateClientAPI(APIEndpoint):
    # Initialize Class Instance
    def __init__(self, conn):
        self.conn = conn
        # Prepare the SQL statement for updating clients
        cur = self.conn.cursor()
        try:
            cur.execute("""
                PREPARE update_client(text, text, text, text, text, boolean) AS
                UPDATE Client
                SET 
                    firstName = COALESCE($2, firstName),
                    lastName = COALESCE($3, lastName),
                    phoneNumber = COALESCE($4, phoneNumber),
                    email = COALESCE($5, email),
                    activeStatus = COALESCE($6, activeStatus)
                WHERE 
                    accountNumber = $1
                RETURNING accountNumber, firstName, lastName, phoneNumber, email, activeStatus;
            """)
            self.conn.commit() # Commit the prepare command
        except Exception:
            self.conn.rollback()
            print("Error preparing update_client statement.")
        finally:
            cur.close()

    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. UpdateClient - Updates an existing client's information.")

    # Displays details of API and its use
    def display_details(self):
        print("\n--- UpdateClient ---")
        print("Description: Updates specific details of an existing client. Fields not provided remain unchanged.")
        print("Parameters:")
        print("\t- accountNumber (string): Client's unique account number (required)")
        print("\t- firstName (string): Client's first name (optional)")
        print("\t- lastName (string): Client's last name (optional)")
        print("\t- phoneNumber (string): Client's phone number (optional)")
        print("\t- email (string): Client's email address (optional)")
        print("\t- activeStatus (true/false): Whether the client is active (optional)")
        print("\tExample: accountNumber = C0001, firstName = John, lastName = Smith")
        print("-------------------------\n")

    # Function for executing API and collecting user input
    def execute(self):
        accountNumber = input("Enter client's account number: ").strip()
        
        if not accountNumber:
            print("Error: Account number is required.")
            return
            
        print("Enter the fields you want to update (leave blank to keep current value):")
        firstName = input("Enter client's first name: ").strip()
        lastName = input("Enter client's last name: ").strip()
        phoneNumber = input("Enter client's phone number: ").strip()
        email = input("Enter client's email: ").strip()
        activeStatus_input = input("Enter client's active status (true/false): ").strip().lower()
        
        activeStatus = None
        if activeStatus_input:
            if activeStatus_input not in ["true", "false"]:
                print("Error: Active status must be 'true' or 'false'.")
                return
            activeStatus = True if activeStatus_input == "true" else False

        cur = self.conn.cursor()
        try:
            cur.execute("BEGIN;")
            
            # Execute the prepared statement with parameters
            cur.execute("EXECUTE update_client(%s, %s, %s, %s, %s, %s);", 
                       (accountNumber, 
                        firstName if firstName else None, 
                        lastName if lastName else None, 
                        phoneNumber if phoneNumber else None, 
                        email if email else None, 
                        activeStatus))
            
            result = cur.fetchone()
            
            if result:
                self.conn.commit()
                # Display Results
                print("\nClient updated successfully!")
                print(f"Account Number: {result[0]}")
                print(f"First Name: {result[1]}")
                print(f"Last Name: {result[2]}")
                print(f"Phone Number: {result[3]}")
                print(f"Email: {result[4]}")
                print(f"Active Status: {result[5]}")
            else:
                self.conn.rollback()
                print(f"Error: Client with account number {accountNumber} not found.")
                
        except Exception:
            self.conn.rollback()
            print("Error updating client. Please try again.")
        finally:
            cur.close()


# ---------------------------
# RetrieveClientAPI using prepared statement inline
# ---------------------------
class RetrieveClientAPI(APIEndpoint):
    # Initialize Class Instance
    def __init__(self, conn):
        self.conn = conn
        # Prepare the SQL statement for retrieving clients
        cur = self.conn.cursor()
        try:
            cur.execute("""
                PREPARE retrieve_client(text) AS
                SELECT 
                    accountNumber, 
                    firstName, 
                    lastName, 
                    phoneNumber, 
                    email, 
                    activeStatus
                FROM 
                    Client
                WHERE 
                    accountNumber = $1;
            """)
            self.conn.commit() 
        except Exception:
            self.conn.rollback()
            print("Error preparing retrieve_client statement.")
        finally:
            cur.close()

    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. RetrieveClient - Retrieves details of a specific client.")

    # Displays details of API and its use
    def display_details(self):
        print("\n--- RetrieveClient ---")
        print("Description: Retrieves full details of a specific client using their unique account number.")
        print("Parameters:")
        print("\t- accountNumber (string): Client's unique account number")
        print("\tExample: accountNumber = C0001")
        print("-------------------------\n")

    # Function for executing API and collecting user input
    def execute(self):
        accountNumber = input("Enter client's account number: ").strip()
        
        if not accountNumber:
            print("Error: Account number is required.")
            return

        cur = self.conn.cursor()
        try:
            # Execute the prepared statement with parameters
            cur.execute("EXECUTE retrieve_client(%s);", (accountNumber,))
            
            result = cur.fetchone()
            
            if result:
                # Display Results
                print("\nClient Details:")
                print(f"Account Number: {result[0]}")
                print(f"First Name: {result[1]}")
                print(f"Last Name: {result[2]}")
                print(f"Phone Number: {result[3]}")
                print(f"Email: {result[4] or 'N/A'}")
                print(f"Active Status: {result[5]}")
            else:
                print(f"Error: Client with account number {accountNumber} not found.")
                
        except Exception:
            print("Error retrieving client. Please try again.")
        finally:
            cur.close()


# ---------------------------
# ListClientsAPI using prepared statement inline
# ---------------------------
class ListClientsAPI(APIEndpoint):
    # Initialize Class Instance
    def __init__(self, conn):
        self.conn = conn
        # Prepare the SQL statement for listing clients
        cur = self.conn.cursor()
        try:
            cur.execute("""
                PREPARE list_clients(boolean) AS
                SELECT 
                    accountNumber, 
                    firstName, 
                    lastName, 
                    phoneNumber, 
                    email, 
                    activeStatus
                FROM 
                    Client
                WHERE 
                    ($1 IS NULL OR activeStatus = $1)
                ORDER BY 
                    lastName, firstName;
            """)
            self.conn.commit() 
        except Exception:
            self.conn.rollback()
            print("Error preparing list_clients statement.")
        finally:
            cur.close()

    # Displays brief description of API for API Listing Page
    def display_brief(self, index):
        print(f"{index}. ListClients - Lists all clients with optional active status filter.")

    # Displays details of API and its use
    def display_details(self):
        print("\n--- ListClients ---")
        print("Description: Retrieves a list of all clients, optionally filtering by active status.")
        print("Parameters:")
        print("\t- activeStatus (true/false or leave empty for all)")
        print("\tExample: activeStatus = true (to show only active clients)")
        print("-------------------------\n")

    # Function for executing API and collecting user input
    def execute(self):
        activeStatus_input = input("Enter active status filter (true/false or leave empty for all): ").strip().lower()
        
        # Process activeStatus input
        activeStatus = None
        if activeStatus_input:
            if activeStatus_input not in ["true", "false"]:
                print("Error: Active status must be 'true' or 'false'.")
                return
            activeStatus = True if activeStatus_input == "true" else False

        cur = self.conn.cursor()
        try:
            # Execute the prepared statement with parameters
            cur.execute("EXECUTE list_clients(%s);", (activeStatus,))
            
            results = cur.fetchall()
            
            if results:
                # Display Results
                print("\nClient List:")
                print("--------------------------------------------------------------")
                print(f"{'Account Number':<15} {'Name':<30} {'Phone':<15} {'Email':<30} {'Active':<6}")
                print("--------------------------------------------------------------")
                
                for row in results:
                    account_num = row[0]
                    name = f"{row[1]} {row[2]}"
                    phone = row[3]
                    email = row[4] or "N/A"
                    active = "Yes" if row[5] else "No"
                    
                    print(f"{account_num:<15} {name:<30} {phone:<15} {email:<30} {active:<6}")
                
                print("--------------------------------------------------------------")
                print(f"Total clients: {len(results)}")
            else:
                print("No clients found with the specified criteria.")
                
        except Exception:
            print("Error listing clients. Please try again.")
        finally:
            cur.close()
