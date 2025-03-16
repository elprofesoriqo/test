class ApplicationException(Exception):
    """Base exception for application errors"""
    def __init__(self, message: str = "An application error occurred"):
        self.message = message
        super().__init__(self.message)


class DatabaseException(ApplicationException):
    """Exception for database operations"""
    def __init__(self, message: str = "A database error occurred"):
        super().__init__(message)


class TicketNotFoundException(ApplicationException):
    """Exception for when a ticket is not found"""
    def __init__(self, ticket_id: str):
        super().__init__(f"Ticket with ID {ticket_id} not found")


class LLMServiceException(ApplicationException):
    """Exception for LLM service errors"""
    def __init__(self, message: str = "An error occurred in the LLM service"):
        super().__init__(message)


class MessageBrokerException(ApplicationException):
    """Exception for message broker errors"""
    def __init__(self, message: str = "An error occurred in the message broker"):
        super().__init__(message)