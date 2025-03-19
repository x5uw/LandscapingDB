# driver.py

import psycopg2                 # Import the PostgreSQL adapter library for Python
from apis import get_all_apis   # Import the function that retrieves all API objects grouped by category
from config import DB_CONFIG    # Import the database configuration dictionary



# Function to connect to the PostgreSQL database
# It uses the connection settings specified in config.py
# Returns a connection object if successful, otherwise returns None
def connect_to_db():
    try: # Attempt to establish a connection to the database 
        dbConnection = psycopg2.connect(**DB_CONFIG)
        return dbConnection 
    except psycopg2.Error as e: # Print an error message if the connection attempt fails
        print("Error connecting to database:", e)
        return None  # Return None to indicate that the connection was not successful



# The main function that acts as the entry point for the CLI program
def main():
    # Try to establish a connection to the database
    dbConnection = connect_to_db()
    if not dbConnection:
        print("Could not connect to the database. Exiting.")
        return

    # Retrieve a dictionary of API endpoint groups from apis.py
    apis_by_group = get_all_apis(dbConnection)
    
    # Define the group order as desired for display
    group_order = [
        "Client Management",
        "Service Management",
        "Employee Management",
        "Property Management",
        "Financial Management"
    ]
    
    # Build a sequential list of all API objects for later selection
    all_apis = []
    
    # Start an infinite loop to continuously prompt the user for input until they choose to exit
    while True:
        print("\n\n===== Available APIs =====\n")
        counter = 1  # Initialize sequential numbering
        
        # Iterate through groups in the defined order
        for group in group_order:
            print(f"--{group}--")
            
            for api in apis_by_group[group]:
                # Display a brief summary for each API
                api.display_brief(counter)
                all_apis.append(api)
                counter += 1
            print("")  # Blank line after each group
        
        print("--EXIT PROGRAM--")
        print("0. Exit")
        
        # Prompt the user to select an API by entering its corresponding number
        print("\n====================\n")
        choice = input("Enter the number corresponding to the API you want to view: ").strip()

        # If the user enters "0", break out of the loop and exit the program
        if choice == "0":
            print("Exiting CLI. Goodbye!")
            break

        # Convert the user input to an integer, and run the API chosen
        try:
            choice = int(choice)
            
            # Check if the chosen number is within the valid range of available APIs and run chosen API
            if 1 <= choice <= len(all_apis):
                all_apis[choice - 1].display_details()   
                all_apis[choice - 1].execute() 
            else: # Inform the user if the number is out of the valid range
                print("Invalid selection. Please try again.")
        
        # Catch the exception if the input could not be converted to an integer
        except ValueError:
            print("Invalid input. Please enter a number.")

    dbConnection.close() # After the user chooses to exit, close the database connection



# This conditional ensures that the main function is only executed when the script
# is run directly, and not when it is imported as a module in another script
if __name__ == "__main__":
    main()
