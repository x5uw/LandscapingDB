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

#from financialmanagement import (
#
#)

from propertymanagement import (
    ListPropertiesAPI, 
    UpdateClientPropertiesAPI, 
    )

# Returns a list of API endpoint instances.
# Each module’s API class is instantiated with the same DB connection.
def get_all_apis(conn):    
    return (
        UpdateClientAPI(conn),
        RetrieveClientAPI(conn),
        ListClientsAPI(conn),
        AssignRecurringService(conn),
        UpdateService(conn),
        GetServiceHistory(conn),  
        ListAssignedServices(conn),
        ListEmployeesAPI(conn),
        CreateEmployeeAPI(conn),
        EditEmployeeAPI(conn),
        ListPropertiesAPI(conn),
        UpdateClientPropertiesAPI(conn), 
    )
