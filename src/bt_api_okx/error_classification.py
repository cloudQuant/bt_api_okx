"""OKX native error-code classifications."""

_DEFINITE_REJECT_CODES = frozenset(
    {
        "50101",  # API key does not match the selected environment
        "50119",  # API key does not exist
        "50120",  # API key lacks permission for this function
        "50123",  # API key lacks crypto trading permission
        "51000",  # invalid request parameter
        "51008",  # insufficient balance or margin
        "51010",  # request unsupported by the account mode
        "51121",  # quantity is not a multiple of the lot size
    }
)
_AUTH_ENVIRONMENT_MISMATCH_CODES = frozenset(["50101", "50119"])
_PARAMETER_ERROR_CODES = frozenset(["50014", "50016", "51000"])


def classify_error(code):
    """Return category, environment mismatch, and definite-reject facts."""
    rejected = code in _DEFINITE_REJECT_CODES
    if code in _AUTH_ENVIRONMENT_MISMATCH_CODES:
        return "auth", True, rejected
    if code in _PARAMETER_ERROR_CODES:
        return "parameter", False, rejected
    return None, False, rejected
