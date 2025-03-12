# apis.py

#from clientmanagement import (

#)

#from servicemanagement import (

#)

#from workrecordmanagement import (

#)

#from employeemanagement import (

#)

#from financialmanagement import (

#)

from propertymanagement import (
    ListPropertiesAPI, 
    DetailPropertyAPI, 
    ComplexQueryPropertiesAPI,
    CrupdateSinglePropertyAPI,
    CrupdateMultiplePropertiesAPI
    )

def get_all_apis(conn):
    
    # Returns a list of API endpoint instances.
    # Each module’s API class is instantiated with the same DB connection.

    return [
        ListPropertiesAPI(conn),
        DetailPropertyAPI(conn),
        ComplexQueryPropertiesAPI(conn),
        CrupdateSinglePropertyAPI(conn),
        CrupdateMultiplePropertiesAPI(conn),
    ]
