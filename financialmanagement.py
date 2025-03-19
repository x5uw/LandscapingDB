# Author: Manuel Rodriguez
# financialmanagement.py
# Note: Prepared for CSS475, Winter2025, UWB
# ---------------------------------------------

from api_endpoint import APIEndpoint

# ---------------------------
# WorkSummaryAPI (List API)
# Description: Retrieves a summary of work records for each employee
#              within a specified date range.
# Author: Manuel Rodriguez
# ---------------------------
class WorkSummaryAPI(APIEndpoint):

    # Initialize class and prepare the SQL statement with date range parameters.
    def __init__(self, conn):
        self.conn = conn            # Database connection object.
        cur = self.conn.cursor()    # Create a cursor object for executing SQL commands.
        
        # Prepare the postgres PREPARE statement with date range parameters
        try:
            cur.execute("""
                PREPARE my_work_summary(timestamp, timestamp) AS
                SELECT
                    E.employeenum,                -- Employee number from the Employee table
                    E.firstname,                  -- Employee first name
                    E.lastname,                   -- Employee last name
                    COUNT(W.id) AS total_work_records,  -- Count of work records for each employee in the specified date range
                    COALESCE(
                        (
                            -- Subquery: Sum the durations of work records for this employee that fall within the specified date range.
                            -- It subtracts the start time from the end time for each record to calculate the interval, then sums these intervals.
                            SELECT SUM(W2.endtime - W2.starttime)
                            FROM Workrecord W2
                            WHERE W2.employeeid = E.id
                              AND W2.starttime >= $1 -- Start time of the date range, first parameter
                              AND W2.endtime <= $2  -- End time of the date range, second parameter
                        ),
                        '0 seconds'::interval   -- If no work records exist in the date range, default to a zero-length interval.
                    ) AS total_duration     -- Total duration (as an interval) of work within the date range.
                FROM Employee E
                    LEFT JOIN Workrecord W ON       -- LEFT JOIN with date conditions ensures employees with no work records in this range are still included
                        (E.id = W.employeeid 
                            AND W.starttime >= $1   -- Start time of the date range, first parameter
                            AND W.endtime <= $2)    -- End time of the date range, second parameter
                GROUP BY E.id, E.firstname, E.lastname
                ORDER BY E.employeenum;
            """)
            self.conn.commit()  # Commit the prepare command.
        
        # Handle exceptions if the prepare statement fails
        except Exception as e:
            self.conn.rollback()
            print("Error preparing my_work_summary.")
        
        # Close the cursor object
        finally:
            cur.close()


    # Display brief description of the API for the API listing page.
    def display_brief(self, index):
        print(f"{index}. WorkSummary - Lists a summary of work records, and hours worked for each employee within a specified date range.")


    # Display detailed information about the API.
    def display_details(self):
        print("\n--- WorkSummary ---")
        print("Description: Retrieves a summary of work records for each employee within a specified date range.")
        print("Parameters:")
        print("\t- Start Date (timestamp, format: YYYY-MM-DD)")
        print("\t- End Date (timestamp, format: YYYY-MM-DD)")
        print("Example: Start Date = '2025-01-05', End Date = '2025-01-23'")
        print("-------------------------\n")


    # Function for executing the API and collecting user input for the date range.
    def execute(self):
        start_date = input("Enter start date (YYYY-MM-DD or YYYY-MM-DD HH:MI): ").strip()
        end_date = input("Enter end date (YYYY-MM-DD or YYYY-MM-DD HH:MI): ").strip()

        # Check if user wants to terminate the operation.
        if start_date.lower() == "quit" or end_date.lower() == "quit":
            print("Operation terminated by user.")
            return

        cur = self.conn.cursor() # Create a cursor object for executing SQL commands
        
        # Execute the prepared statement with the provided start and end date parameters
        try:
            cur.execute("EXECUTE my_work_summary(%s, %s);", (start_date, end_date))
            rows = cur.fetchall()

            print("\nemployeenum | first name | last name | total work records | total duration")
            print("------------+-----------+----------+--------------------+---------------")

            # Print the results of the query
            for row in rows:
                employeenum, firstname, lastname, total_work_records, total_duration = row
                print(f"{employeenum:12} | {firstname:9} | {lastname:8} | {total_work_records:18} | {total_duration}")

        # Print Error message if the query fails
        except Exception as e:
            print("Error executing my_work_summary.")
        
        # Close the cursor object
        finally:
            cur.close()
