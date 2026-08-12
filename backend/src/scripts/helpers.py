import flask
import logging
from classes.CommonQueries import CommonQueries
from flask.sessions import SessionMixin
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

logger = logging.getLogger(__name__)

class UserNotFoundError(Exception):
    pass

class NoUserProvidedError(Exception):
    pass

class TickerNotFoundError(Exception):
    """Raised when a ticker symbol cannot be found on Yahoo Finance."""
    pass

class InvalidJSONBodyError(Exception):
    """Raised when a request's JSON body is missing, malformed, or not an object."""
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code

def get_user_id_from_query_param_or_session(r: flask.Request, s: SessionMixin, cc: CommonQueries) -> int:
    """
    Resolve a user_id from a request query parameter or session.
    Prioritizes query parameter over session.

    Args:
        r: Flask request object
        s: Flask session object
        cc: CommonQueries instance

    Returns:
        user_id as int

    Raises:
        UserNotFoundError: Username in query parameter not found in database.
        NoUserProvidedError: No username in query parameter or session.
    """
    username = r.args.get("username", "")
    user_id = s.get("user_id", 0)
    
    if username:
        user_id = cc.get_user_id_from_username(username=username)
        if user_id:
            return user_id
        raise UserNotFoundError(f"Username {username} not found.")
    elif user_id:
        return user_id
    else:
        raise NoUserProvidedError("No username in query parameter or session.")

def parse_json_body(r: flask.Request) -> dict:
    """
    Parses and returns a request's JSON body as a dict.

    Args:
        r: Flask request object

    Returns:
        Parsed JSON body as a dict.

    Raises:
        InvalidJSONBodyError: Content-Type is not application/json, the body
            is malformed JSON, or the body does not parse to an object.
    """
    try:
        body = r.get_json()
    except UnsupportedMediaType:
        logger.warning(f"Request to {r.path} had wrong Content-Type header.")
        raise InvalidJSONBodyError("Content-Type must be application/json", 415)
    except BadRequest:
        logger.warning(f"Request to {r.path} had malformed JSON body.")
        raise InvalidJSONBodyError("Malformed JSON body", 400)

    try:
        return dict(body)
    except TypeError:
        logger.warning(f"Request to {r.path} body could not be parsed as an object.")
        raise InvalidJSONBodyError("Malformed request body", 400)