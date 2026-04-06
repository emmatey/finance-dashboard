import flask
import logging
from CommonQueries import CommonQueries
from flask.sessions import SessionMixin
from functools import wraps

logger = logging.getLogger(__name__)

class UserNotFoundError(Exception):
    pass

class NoUserProvidedError(Exception):
    pass

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if flask.session.get("user_id") is None:
            return flask.redirect("/auth/logout")
        return f(*args, **kwargs)

    return decorated_function

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