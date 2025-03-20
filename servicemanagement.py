# servicemanagement.py

from api_endpoint import APIEndpoint

# ---------------------------
# AssignRecurringService API
# Author: Minh Tran
# ---------------------------
class AssignRecurringService(APIEndpoint):
    """ API to assign a new recurring service to a property """

    def __init__(self, conn):
        self.conn = conn
        cur = self.conn.cursor()
        try:
            # Prepare SQL statement for assigning a recurring service
            cur.execute("""
                PREPARE assign_recurring_service(text, text, interval, money, text) AS
                INSERT INTO RecurringService (serviceTypeID, name, allocatedManHours, price, orderStatusID)
                VALUES (
                    (SELECT id FROM ServiceType WHERE id = $1),  -- Get service type ID
                    $2,  -- Service name
                    $3,  -- Allocated hours
                    $4,  -- Price
                    'A'  -- Default OrderStatus to 'Active'
                )
                RETURNING serviceNum;
            """)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print("Error preparing assign_recurring_service:", e)
        finally:
            cur.close()

    def display_brief(self, index):
        # Display brief API description 
        print(f"{index}. AssignRecurringService - Assigns a new recurring service to a property.")

    def display_details(self):
        # Display detailed API usage information 
        print("\n--- AssignRecurringService ---")
        print("Assigns a new recurring service to a property with the required details.")
        print("Parameters:")
        print("\t- propertyNumber (text): The property number where the service will be assigned")
        print("\t- serviceType (text): Service Type Code. Options:")
        print("\t\tL: Lawncare")
        print("\t\tT: Tree Trimming")
        print("\t\tF: Flowerbed")
        print("\t\tS: Snow Removal")
        print("\t\tO: Other")
        print("\t- serviceName (text): Descriptive name of the service")
        print("\t- allocatedManHours (interval): Time allocated (e.g., '01:30:00')")
        print("\t- price (money): Cost of the service (e.g., '60.00')")
        print("\t- frequencyType (text): Frequency of the service. Options:")
        print("\t\tW: Weekly")
        print("\t\tB: Biweekly")
        print("\t\tM: Monthly")
        print("\t\tQ: Quarterly")
        print("\tReturns:")
        print("\t- The assigned service number (auto-generated)")
        print("\nExample Input:")
        print("propertyNumber = 'P001', serviceType = 'L', serviceName = 'Premium Lawn Mowing',")
        print("allocatedManHours = '01:30:00', price = 60.00, frequencyType = 'W'")
        print("-------------------------\n")

    def execute(self):
        # Execute the API by collecting user input
        property_number = input("Enter property number: ").strip()
        service_type = input("Enter service type code (L for Lawncare, T for Tree Trimming, F for Flowerbed, S for Snow Removal, O for Other): ").strip()
        service_name = input("Enter service name (e.g., Special Lawn Care): ").strip()
        allocated_man_hours = input("Enter allocated man hours (HH:MM:SS): ").strip()
        price = input("Enter price: ").strip()
        frequency_type = input("Enter frequency type code (W for Weekly, B for Biweekly, M for Monthly, Q for Quarterly): ").strip()

        cur = self.conn.cursor()
        try:
            # Ensure property exists before inserting service
            cur.execute("SELECT id FROM Property WHERE propertyNumber = %s;", (property_number,))
            property_id = cur.fetchone()

            if not property_id:
                print(f"Error: Property {property_number} does not exist.")
                return

            # Execute the prepared statement to insert into RecurringService
            cur.execute("EXECUTE assign_recurring_service(%s, %s, %s, %s, %s);", 
                        (service_type, service_name, allocated_man_hours, price, property_number))
            service_num = cur.fetchone()[0]

            # Retrieve the id of the newly created service using its serviceNum
            cur.execute("SELECT id FROM RecurringService WHERE serviceNum = %s;", (service_num,))
            new_service_id = cur.fetchone()[0]

            # Insert into RecurringServiceList to link the property with the new service.
            cur.execute("""
                INSERT INTO RecurringServiceList (propertyID, recurringServiceID, frequencyTypeID, activeStatus)
                VALUES (
                    (SELECT id FROM Property WHERE propertyNumber = %s),
                    %s,
                    %s,
                    TRUE
                );
            """, (property_number, new_service_id, frequency_type))

            self.conn.commit()
            print(f"Service assigned successfully with service number: {service_num}")
        except Exception as e:
            print("Error executing assign_recurring_service:", e)
            self.conn.rollback()
        finally:
            cur.close()

# ---------------------------
# UpdateService API
# Author: Minh Tran
# ---------------------------
class UpdateService(APIEndpoint):
    # API to update details of an existing recurring service 

    def __init__(self, conn):
        self.conn = conn
        cur = self.conn.cursor()
        try:
            # Prepare SQL statement for updating a recurring service in the RecurringService table
            cur.execute("""
                PREPARE update_service(text, text, interval, money, text, text) AS
                UPDATE RecurringService
                SET 
                    name = $2, 
                    allocatedManHours = $3, 
                    price = $4, 
                    serviceTypeID = (SELECT id FROM ServiceType WHERE id = $5),  -- Fetch serviceTypeID
                    orderStatusID = (SELECT id FROM OrderStatus WHERE id = $6)  -- Fetch orderStatusID
                WHERE serviceNum = $1
                RETURNING serviceNum;
            """)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print("Error preparing update_service:", e)
        finally:
            cur.close()

    def display_brief(self, index):
        # Display brief API description
        print(f"{index}. UpdateService - Updates details of an existing recurring service.")

    def display_details(self):
        # Display detailed API usage information 
        print("\n--- UpdateService ---")
        print("Description: Updates specific details of an existing recurring service.")
        print("Parameters:")
        print("\t- serviceNum (text): Unique service number, e.g., 'RS0083'")
        print("\t- serviceName (text): Updated service name")
        print("\t- allocatedManHours (interval): Updated allocated hours, e.g., '02:00:00'")
        print("\t- price (money): Updated cost, e.g., 100.00")
        print("\t- serviceType (text): Updated service type code. Options:")
        print("\t\tL: Lawncare")
        print("\t\tT: Tree Trimming")
        print("\t\tF: Flowerbed")
        print("\t\tS: Snow Removal")
        print("\t\tO: Other")
        print("\t- orderStatus (text): Updated order status code. Options:")
        print("\t\tA: Active")
        print("\t\tI: Inactive")
        print("\t\tP: Paused")
        print("\t- frequencyType (text): (Optional) Updated frequency type code for the service assignment. Options:")
        print("\t\tW: Weekly")
        print("\t\tB: Biweekly")
        print("\t\tM: Monthly")
        print("\t\tQ: Quarterly")
        print("\nExample Input:")
        print("serviceNum = 'RS0083', serviceName = 'Advanced Lawn Care', allocatedManHours = '02:00:00',")
        print("price = 100.00, serviceType = 'L', orderStatus = 'A', frequencyType = 'Q'")
        print("-------------------------\n")

    def execute(self):
        # Execute the API by collecting user input 
        service_num = input("Enter service number (e.g., RS0083): ").strip()
        service_name = input("Enter new service name (or press enter to keep current): ").strip() or None
        allocated_man_hours = input("Enter new allocated man hours (HH:MM:SS, or press enter to keep current): ").strip() or None
        price = input("Enter new price (or press enter to keep current): ").strip() or None
        service_type = input("Enter new service type code (L for Lawncare, T for Tree Trimming, F for Flowerbed, S for Snow Removal, O for Other, or press enter to keep current): ").strip() or None
        order_status = input("Enter new order status code (A for Active, I for Inactive, P for Paused, or press enter to keep current): ").strip() or None
        frequency_type = input("Enter new frequency type code (W for Weekly, B for Biweekly, M for Monthly, Q for Quarterly, or press enter to keep current): ").strip() or None

        cur = self.conn.cursor()
        try:
            # Ensure the service exists before attempting an update
            cur.execute("SELECT serviceNum FROM RecurringService WHERE serviceNum = %s;", (service_num,))
            existing_service = cur.fetchone()

            if not existing_service:
                print(f"Error: Service with number {service_num} does not exist.")
                return

            # Execute the prepared statement with updated details for the RecurringService table
            cur.execute("EXECUTE update_service (%s, %s, %s, %s, %s, %s);", 
                        (service_num, service_name, allocated_man_hours, price, service_type, order_status))
            updated_service_num = cur.fetchone()[0]

            # If the user provided a new frequency, update the RecurringServiceList table accordingly.
            if frequency_type:
                cur.execute("""
                    UPDATE RecurringServiceList
                    SET frequencyTypeID = %s
                    WHERE recurringServiceID = (SELECT id FROM RecurringService WHERE serviceNum = %s);
                """, (frequency_type, service_num))

            self.conn.commit()

            if updated_service_num:
                print(f"Service updated successfully with service number: {updated_service_num}")
            else:
                print("Failed to update service. Please check service number and inputs.")
        except Exception as e:
            print("Error executing update_service:", e)
            self.conn.rollback()
        finally:
            cur.close()

# ---------------------------
# GetServiceHistory API
# Author: Kat Tran
# ---------------------------
class GetServiceHistory(APIEndpoint):  # Detail API for retrieving client service history
    """
    This class retrieves a client's full service history, including:
    - Service start and end times
    - Type of service performed
    - Duration of the service
    - Cost of the service
    """

    def __init__(self, conn):
        """
        Initializes the class with a database connection.
        
        :param conn: Database connection object
        """
        self.conn = conn  # Store the database connection object for executing queries

    def display_brief(self, index: int):
        """
        Displays a brief description of this API's functionality.
        
        :param index: Index of the API in a list of available APIs
        """
        print(f"{index}. GetServiceHistory - Retrieve service history for a client.")

    def display_details(self):
        """
        Displays detailed information about what this API does.
        """
        print("\n--- GetServiceHistory ---")
        print("Retrieves full service history for a client, including date, type, duration, and cost.")
        print("\nParameters:")
        print("\t- accountNumber (text): The unique account number of the client.")
        print("\tReturns:")
        print("\t The list of service records for the given client, showing when each service was performed, the type of service, the duration, and the cost.")
        
        print("\nExample Input:")
        print("accountNumber = 'C0001'")
        print("-------------------------\n")

    def execute(self):
        """
        Executes the query to fetch a client's service history.
        - Prompts the user for the client’s account number
        - Queries the database to retrieve historical service records
        - Prints the service history or an error message if no records are found
        """
        
        # Prompt the user to enter the client's unique account number
        account_number = input("Enter Client Account Number (Example: C0001): ").strip()

        # SQL query to fetch service history for a given client account number
        # Join with RecurringService to get service details
        # Join with Client table to match the account number
        query = """
        SELECT wr.startTime, wr.endTime, rs.name AS serviceType, rs.allocatedManHours, rs.price
        FROM WorkRecord wr
            JOIN RecurringService rs ON wr.recurringServiceID = rs.id  
            JOIN Property p ON p.id = (
                SELECT propertyID FROM RecurringServiceList WHERE recurringServiceID = wr.recurringServiceID
            )  
            JOIN Client c ON c.id = p.clientID 
        WHERE c.accountNumber = %s;
        """

        try:
            # Open a database cursor using 'with' to ensure it's properly closed after execution
            with self.conn.cursor() as cur:
                # Execute the SQL query safely using parameterized queries to prevent SQL injection
                cur.execute(query, (account_number,))
                
                # Fetch all matching service history records
                records = cur.fetchall()
                
                # If no records found, print an error message
                if not records:
                    print("Error: Client not found or no service history available.")
                else:
                    # Display the retrieved service history in a readable format
                    print("\nService History:")
                    for row in records:
                        print(f"Start Time: {row[0]}, End Time: {row[1]}, Service: {row[2]}, Duration: {row[3]} hours, Cost: ${row[4]}")
        
        except Exception as e:
            # Print a error message if a database error occurs
            print("An error occurred while retrieving service history.")

# ---------------------------
# ListAssignedService API
# Author: Kat Tran
# ---------------------------
class ListAssignedServices(APIEndpoint):  # List API for retrieving assigned services
    """
    This class retrieves all currently assigned services for a given property.
    - Includes service type, duration, and price
    - Supports filtering through limit and offset
    """

    def __init__(self, conn):
        """
        Initializes the class with a database connection.
        
        :param conn: Database connection object
        """
        self.conn = conn  # Store the database connection object for executing queries

    def display_brief(self, index: int):
        """
        Displays a brief description of this API's functionality.
        
        :param index: Index of the API in a list of available APIs
        """
        print(f"{index}. ListAssignedServices - List all services assigned to a property.")

    def display_details(self):
        """
        Displays detailed information about what this API does.
        """
        print("\n--- ListAssignedServices ---")
        print("Lists all active services currently assigned to a property, with optional filtering.")
        print("\nParameters:")
        print("\t- propertyNumber (text): The property number where services are assigned.")
        print("\t- limit (integer, optional): Max number of results per page (default: 10).")
        print("\t- offset (integer, optional): The number of records to skip (default: 0, starts from first record).")
        print("\nReturns:")
        print("\t- A list of active services assigned to the specified property, showing the service number, name, allocated time, and cost.")
        print("\nExample Input:")
        print("propertyNumber = 'P001', limit = 5, offset = 0")
        print("-------------------------\n")

    def execute(self):
        """
        Executes the query to fetch assigned services for a property.
        - Prompts the user for the property number
        - Queries the database to retrieve assigned services
        - Supports using LIMIT and OFFSET
        - Prints the list of services or an error message if no records are found
        """

        # Prompt the user to enter the property number (identifier for the property)
        property_number = input("Enter Property Number (Example: P001): ").strip()

        # Prompt the user for filtering options (limit and offset for pagination)
        limit = input("Enter max results per page (default 10): ").strip() or "10"  
        # Default value is 10
        offset = input("Enter offset (default 0, start from first result): ").strip() or "0"  
        # Default value is 0

        # SQL query to fetch assigned services for a given property
        query = """
        SELECT rs.serviceNum, rs.name, rs.allocatedManHours, rs.price
        FROM RecurringServiceList rsl
            JOIN RecurringService rs ON rsl.recurringServiceID = rs.id
            JOIN Property p ON p.id = rsl.propertyID
        WHERE p.propertyNumber = %s AND rsl.activeStatus = TRUE
        ORDER BY rs.name
        LIMIT %s OFFSET %s;
        """

        try:
            # Open a database cursor using 'with' to ensure it's properly closed after execution
            with self.conn.cursor() as cur:
                # Execute the SQL query with the provided inputs (ensuring safe parameterized query execution)
                cur.execute(query, (property_number, limit, offset))
                
                # Fetch all matching records from the database
                services = cur.fetchall()
                
                # If no records are found, display an error message
                if not services:
                    print("Error: No services found for this property.")
                else:
                    # Display the retrieved services in a user-friendly format
                    print("\nAssigned Services:")
                    for row in services:
                        print(f"Service Number: {row[0]}, Service: {row[1]}, Duration: {row[2]} hours, Cost: ${row[3]}")
        
        except Exception as e:
            # Print a error message if a database error occurs
            print("An error occurred while retrieving service history.")

