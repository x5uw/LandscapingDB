# driver.py

import psycopg2                 # Import the PostgreSQL adapter library for Python
from apis import get_all_apis   # Import the function that retrieves all API objects
from config import DB_CONFIG    # Import the database configuration dictionary



# Function to connect to the PostgreSQL database
# It uses the connection settings specified in DB_CONFIG
# Returns a connection object if successful, otherwise returns None
def connect_to_db():
    try: # Attempt to establish a connection to the database by unpacking the DB_CONFIG dictionary
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

    # Retrieve a list of API endpoint objects from the database
    apis = get_all_apis(dbConnection)

    # Start an infinite loop to continuously prompt the user for input until they choose to exit
    while True:
        print("\n=== Available APIs ===")
        
        # Iterate over the list of API objects
        for i, api in enumerate(apis): # The enumerate function is used to display a numbered list (starting at 1)
            api.display_brief(i + 1) # Display a brief summary of API
        
        # Provide an option for the user to exit
        print("0. Exit")
        
        # Prompt the user to select an API by entering its corresponding number
        choice = input("Enter the number corresponding to the API you want to view: ").strip()

        # If the user enters "0", break out of the loop and exit the program
        if choice == "0":
            print("Exiting CLI. Goodbye!")
            break

        # Convert the user input to an integer, and run the API chosen
        try:
            choice = int(choice) 
            
            if 1 <= choice <= len(apis): # Check if the chosen number is within the valid range of available APIs
                apis[choice - 1].display_details()      # Display detailed information about the selected API
                apis[choice - 1].execute()              # Execute the selected API's action
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
