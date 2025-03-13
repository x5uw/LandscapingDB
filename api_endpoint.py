# api_endpoint.py

class APIEndpoint:
    # Abstract base class for all API endpoints
    # Each API must implement:
    #   - display_brief(index): Print a one-line summary
    #   - display_details(): Print detailed usage information
    #   - execute(): Prompt for input and perform the database operation
    
    def display_brief(self, index):
        raise NotImplementedError
    
    def display_details(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

