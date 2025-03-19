#apis.py

from clientmanagement import (
    UpdateClientAPI,
    RetrieveClientAPI,
    ListClientsAPI
)

from servicemanagement import (
    AssignRecurringService,
    UpdateService,
    GetServiceHistory,       
    ListAssignedServices
    )

#from workrecordmanagement import (
#
#)

from employeemanagement import (
    ListEmployeesAPI,
    CreateEmployeeAPI,
    EditEmployeeAPI
)

from financialmanagement import (
    WorkSummaryAPI
)

from propertymanagement import (
    ListPropertiesAPI, 
    UpdateClientPropertiesAPI, 
    )

# Returns a dictionary of API groups.
def get_all_apis(conn):
    return {
        "Client Management": get_client_apis(conn),
        "Service Management": get_service_apis(conn),
        "Employee Management": get_employee_apis(conn),
        "Property Management": get_property_apis(conn),
        "Financial Management": get_financial_apis(conn)
    }

# Group-specific functions returning lists of API endpoint instances.

def get_client_apis(conn):
    return [UpdateClientAPI(conn), RetrieveClientAPI(conn), ListClientsAPI(conn)]

def get_service_apis(conn):
    return [AssignRecurringService(conn), UpdateService(conn), GetServiceHistory(conn), ListAssignedServices(conn)]

def get_employee_apis(conn):
    return [ListEmployeesAPI(conn), CreateEmployeeAPI(conn), EditEmployeeAPI(conn)]

def get_property_apis(conn):
    return [ListPropertiesAPI(conn), UpdateClientPropertiesAPI(conn)]

def get_financial_apis(conn):
    return [WorkSummaryAPI(conn)]