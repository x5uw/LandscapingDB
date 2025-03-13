# LandscapingDB
LandscapeDB Project

## Overview
LandscapeDB is a command‑line Python application that interacts with a PostgreSQL database using psycopg2. The project is organized into separate modules so that each team member can develop their own API endpoints independently. Every API module (for client management, property management, service management, work record management, employee management, and financial management) implements a common interface defined by the APIEndpoint abstract class.  
**Note:** Each API module now leverages prepared statements for SQL queries. This ensures that queries are pre-compiled for efficiency and that user inputs are handled securely, reducing the risk of SQL injection.

Using this program requires importing "psycopg2" onto your local device for interfacing with PostgreSQL.

The system works as follows:

## Database Connection:
A global configuration (in config.py) provides the connection settings to the PostgreSQL database. The helper function in driver.py uses these settings to create a connection.

## API Modules:
- Each API module (e.g., clientmanagement.py, propertymanagement.py, etc.) contains one or more classes that inherit from APIEndpoint.
- These classes implement the following methods:
  - **display_brief(index):**  
    Shows a one-line summary of the API.
  - **display_details():**  
    Provides detailed usage information, including parameters and examples.
  - **execute():**  
    Prompts for user input, executes parameterized SQL queries (with prepared statements and proper transaction management), and displays results.
- **Prepared Statements:**  
  Each API module prepares its own SQL statements once upon instantiation. This means that each prepared statement is compiled only once per session, improving execution speed and security.

## API Aggregation:
The `apis.py` file imports the individual API classes and provides a function `get_all_apis(conn)` that returns a list of instantiated API objects. (Team members will add their modules here as they complete them.)

## Driver:
The `driver.py` file is the main entry point. It connects to the database, retrieves the list of API objects from `apis.py`, and presents a CLI menu. The user selects an API by number, after which the API’s details are displayed and its execution method is called.

## How to Add New APIs
1. **Create Your Module File:**  
   For example, if you're working on client management, create or update `clientmanagement.py`.
2. **Implement the API Endpoint:**  
   In your file, define one or more classes that inherit from APIEndpoint (from `api_endpoint.py`) and implement the required methods.  
   **Important:** Follow the pattern of preparing your SQL statements in the class constructor. This ensures the prepared statements are created only once per session.
3. **Update the APIs Aggregator:**  
   In `apis.py`, import your new class and add an instance of it (with the shared database connection) to the list returned by `get_all_apis()`.
4. **Test Your API:**  
   Run `python3 driver.py` and choose your API from the menu. Ensure that it correctly prompts for input, executes its queries using prepared statements, and properly manages transactions and resource cleanup.

## Global Configuration (config.py)
- **DB_CONFIG:**  
  Contains the database connection settings (host, dbname, user, password).
  ### **TEAM NOTE:**  
  Update the password or other values if your local settings for accessing your local database differ.

## Files Overview
- **config.py:** Global database settings.
- **database.py:** Contains `connect_to_db()` that creates a database connection using psycopg2.
- **api_endpoint.py:** Defines the abstract APIEndpoint class.
- **apis.py:** Aggregates API objects (each team member’s module will be added here).
- **clientmanagement.py, propertymanagement.py, servicemanagement.py, workrecordmanagement.py, employeemanagement.py, financialmanagement.py:**  
  Each file contains one or more API classes for its domain.
- **driver.py:** The main CLI driver that connects to the database, loads APIs, and interacts with the user.
