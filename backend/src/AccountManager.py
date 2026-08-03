import logging
import os

from CommonQueries import CommonQueries
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

logger = logging.getLogger(__name__)
load_dotenv()
secret_key = os.getenv("VERIFICATION_TOKEN_SECRET_KEY")


class AccountManager(CommonQueries):
    """
    This class handles login, registration, and password changing.
    """
    @staticmethod
    def generate_verification_token(context_salt: str, username: str) -> bool:
        """
        Generates a time sensitive, url safe, token to verify various actions.
        """
        if not isinstance(secret_key, str):
            logger.error(f"Secret key for token hashing not present of of wrong type. Must be str is {type(secret_key)}.")
            return False
        serializer = URLSafeTimedSerializer(secret_key=secret_key, salt=context_salt)
        print(serializer.dumps(username))
        

    @staticmethod
    def validate_verification_token(context_salt: str) -> bool:
        """
        Checks if a verification token passed is valid, allowing further actions if so.
        """
        pass
    def login(self, username, password, session) -> bool:
        # Query database for username
        rows = self.select_query(
            "SELECT * FROM users WHERE username = ?", (username, )
            )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], password
        ):
            logger.warning(f"Failed login attempt for username '{username}'")
            return False

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        logger.info(f"User '{username}' logged in (user_id={rows[0]['id']})")
        return True

    def register(self, username: str, password: str) -> int:
        """
        Returns "rows modified" count.
        If there's a conflict, i.e. username already exists,
        return 0,
        else return 1
        """
        # Make sure name isn't already used.
        check_name = self.select_query(
            "SELECT username FROM users WHERE username = ?", (username, )
                                )
        if check_name:
            logger.info(f"Registration rejected: username '{username}' already in use")
            return 0

        hash = generate_password_hash(password)
        # update DB with username and pw hash.
        result = self.modify_query(
            "INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash)
            )
        logger.info(f"User '{username}' registered")
        return result


if __name__ == "__main__":
    am = AccountManager()
    am.generate_verification_token("reset_pw", username="emma")