class DataValidationError(Exception):
    """Raised when data fails schema validation or range constraints."""
    pass

class ModelRegistryError(Exception):
    """Raised when loading or saving model artifacts fails."""
    pass
