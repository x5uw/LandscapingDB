#apis.py

#from clientmanagement import (
#
#)

from servicemanagement import (
    AssignRecurringService,
    UpdateService
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
    DetailPropertyAPI, 
    CrupdateMultiplePropertiesAPI
    )

# Returns a list of API endpoint instances.
# Each module’s API class is instantiated with the same DB connection.
def get_all_apis(conn):    
    return [
        ListPropertiesAPI(conn),
        DetailPropertyAPI(conn),
        CrupdateMultiplePropertiesAPI(conn),
        AssignRecurringService(conn),
        UpdateService(conn)
        ListEmployeesAPI(conn),
        CreateEmployeeAPI(conn),
        EditEmployeeAPI(conn)
    ]
