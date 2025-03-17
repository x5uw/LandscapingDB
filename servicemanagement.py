# servicemanagement.py

from api_endpoint import APIEndpoint

# ---------------------------
# AssignRecurringService API
# ---------------------------
class AssignRecurringService(APIEndpoint):
    def __init__(self, conn):
        self.conn = conn
        cur = self.conn.cursor()
        try:
            # Prepare the SQL statement for creating a new recurring service
            cur.execute("""
                PREPARE assign_recurring_service(text, text, text, interval, money) AS
                INSERT INTO RecurringService(propertyNumber, serviceTypeCode, serviceName, allocatedManHours, price)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING serviceNum;
            """)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print("Error preparing assign_recurring_service:", e)
        finally:
            cur.close()

    def display_brief(self, index):
        print(f"{index}. AssignRecurringService - Assigns a new recurring service to a property.")

    def display_details(self):
        print("\n--- AssignRecurringService ---")
        print("Description: Assigns a new recurring service to a property with details including service type, name, allocated man-hours, and pricing.")
        print("Parameters:")
        print("\t- propertyNumber (text)")
        print("\t- serviceTypeCode (text)")
        print("\t- serviceName (text)")
        print("\t- allocatedManHours (interval)")
        print("\t- price (money)")
        print("\tExample: propertyNumber = 'P001', serviceTypeCode = 'L', serviceName = 'Lawn Mowing', allocatedManHours = '01:00:00', price = 50.00")
        print("-------------------------\n")

    def execute(self):
        property_number = input("Enter property number: ").strip()
        service_type_code = input("Enter service type code: ").strip()
        service_name = input("Enter service name: ").strip()
        allocated_man_hours = input("Enter allocated man hours (HH:MM:SS): ").strip()
        price = input("Enter price: ").strip()

        cur = self.conn.cursor()
        try:
            cur.execute("EXECUTE assign_recurring_service(%s, %s, %s, %s, %s);", (property_number, service_type_code, service_name, allocated_man_hours, price))
            service_num = cur.fetchone()[0]
            print(f"Assigned service number: {service_num}")
        except Exception as e:
            print("Error executing assign_recurring_service:", e)
        finally:
            cur.close()

# ---------------------------
# UpdateService API
# ---------------------------
class UpdateService(APIEndpoint):
    def __init__(self, conn):
        self.conn = conn
        cur = self.conn.cursor()
        try:
            # Prepare the SQL statement for updating an existing service
            cur.execute("""
                PREPARE update_service(integer, text, interval, money, text, text) AS
                UPDATE RecurringService
                SET serviceName = $2, allocatedManHours = $3, price = $4, serviceTypeID = $5, orderStatusName = $6
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
        print(f"{index}. UpdateService - Updates details of an existing recurring service.")

    def display_details(self):
        print("\n--- UpdateService ---")
        print("Description: Updates specific details of an existing recurring service.")
        print("Parameters:")
        print("\t- serviceNum (integer)")
        print("\t- serviceName (text)")
        print("\t- allocatedManHours (interval)")
        print("\t- price (money)")
        print("\t- serviceTypeID (text)")
        print("\t- orderStatusName (text)")
        print("\tExample: serviceNum = 101, serviceName = 'Advanced Lawn Mowing', allocatedManHours = '02:00:00', price = 100.00, serviceTypeID = 'L', orderStatusName = 'Active'")
        print("-------------------------\n")

    def execute(self):
        service_num = input("Enter service number: ").strip()
        service_name = input("Enter new service name: ").strip()
        allocated_man_hours = input("Enter new allocated man hours (HH:MM:SS): ").strip()
        price = input("Enter new price: ").strip()
        service_type_id = input("Enter service type ID: ").strip()
        order_status_name = input("Enter order status name: ").strip()

        cur = self.conn.cursor()
        try:
            cur.execute("EXECUTE update_service(%s, %s, %s, %s, %s, %s);", (service_num, service_name, allocated_man_hours, price, service_type_id, order_status_name))
            updated_service_num = cur.fetchone()[0]
            print(f"Updated service number: {updated_service_num}")
        except Exception as e:
            print("Error executing update_service:", e)
        finally:
            cur.close()