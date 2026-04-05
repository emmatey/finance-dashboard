import flask
import logging
from CommonQueries import CommonQueries
from flask.sessions import SessionMixin
from functools import wraps

logger = logging.getLogger(__name__)

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if flask.session.get("user_id") is None:
            return flask.redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def get_user_id_from_query_param_or_session(s: SessionMixin, r: flask.Request) -> tuple[bool, int]:
    """
    Check query paramater for username.
    If not found, check session for user id
    If not found in either place, return 400
    Prioratizes query parameter.

    Args:
        Flask session object 
        Flask request object
        Instance of CommonQueries class.
    
    Returns:
        (True, user_id),
        (False, HTTP_status_code)
        
    """
    cc = CommonQueries()
    username = r.args.get("username", "")
    user_id = s.get("user_id", 0)
    if username:
        user_id = cc.get_user_id_from_username(username=username)
        if user_id:
            return (True, user_id)
        else:
            logger.warning(f"Username {username} not found.")
            return (False, 404)
    elif user_id:
        return (True, user_id)
    else:
        logger.error("No username provided. Query param and session empty.")
        return (False, 400)
