import logging
import os

from classes.CommonQueries import CommonQueries
from dotenv import load_dotenv
from itsdangerous import BadData, BadSignature, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

logger = logging.getLogger(__name__)
load_dotenv()
secret_key = os.getenv("VERIFICATION_TOKEN_SECRET_KEY")


class AccountManager(CommonQueries):
    """
    This class handles login, registration, and password changing.
    """
    @staticmethod
    def generate_verification_token(context_salt: str, email: str) -> str:
        """
        Generates a time sensitive, url safe, token to verify various actions.
        """
        if not isinstance(secret_key, str):
            logger.error(f"Secret key for token hashing not present or of wrong type. Must be str is {type(secret_key)}.")
            raise TypeError("Secret key for token hashing not present or of wrong type.")
        
        serializer = URLSafeTimedSerializer(secret_key=secret_key, salt=context_salt)
        return serializer.dumps(email)

    @staticmethod
    def validate_verification_token(context_salt: str, token: str, max_age: int = 10*60) -> str:
        """
        Checks if a verification token passed is valid, returning the
        email it was issued for if so.
        """
        if not isinstance(secret_key, str):
            logger.error(f"Secret key for token hashing not present or of wrong type. Must be str is {type(secret_key)}.")
            raise TypeError("Secret key for token hashing not present or of wrong type.")
        
        serializer = URLSafeTimedSerializer(secret_key=secret_key, salt=context_salt)
        try:
            email = serializer.loads(token, max_age=max_age)
        except BadSignature:
            logger.warning(f"Verification token failed signature check (salt='{context_salt}').")
            raise
        except BadData:
            logger.warning(f"Verification token was malformed (salt='{context_salt}').")
            raise

        return email

    @staticmethod
    def check_username_valid(username: str) -> tuple[bool, str | None]:
        # Check if username meets website requirements.
        # Username must be ascii and without spaces.
        if not all(char.isascii() and char.isalnum() and char != " " for char in username):
            return False, "Username must be alphanumeric (A-Z, 0-9) with no spaces."
        if len(username) < 1:
            return False, "Username must be at least 1 char long."
        return True, None

    @staticmethod
    def check_pw_valid(pw: str) -> tuple[bool, str | None]:
        # Check if pw meets website requirements
        # Password must have one capital, one uppercase, one lowercase, and one non-letter, and be 5 chars long.
        if len(pw) < 5:
            return False, "Password must be at least 5 chars long."
        if not all((char.isascii() for char in pw)):
            # Checks for non-ascii
            return False, "Password must contain only ASCII chars."
        if not any((char.isupper() for char in pw)):
            # Checks for uppercase
            return False, "Password must contain at least one uppercase letter."
        if not any((char.islower() for char in pw)):
            # Checks for lowercase
            return False, "Password must contain at least one lowercase letter."
        if all((char.isalpha() for char in pw)):
            # Checks for non-letters
            return False, "Password must contain at least one non-letter character."
        return True, None

    def check_email_in_use(self, email: str) -> bool:
        email_sql = """
        SELECT * 
        FROM users
        WHERE email = ?
        """
        rows = self.select_query(email_sql, (email, ))
        if len(rows) >= 1:
            return True
        else:
            return False

    def change_password(self, password: str, username: str) -> bool:
        user_id = self.get_user_id_from_username(username=username)
        if not user_id:
            logger.error(f"Username {username} not found!")
            return False

        hash = generate_password_hash(password=password)
        password_sql = """
        UPDATE users
        SET hash = ?
        WHERE id = ?
        """
        try:
            self.modify_query(password_sql, (hash, user_id))
        except Exception:
            raise

        return True

    def register(self, username: str, password: str, email: str) -> int:
        """
        Assumes email has been validated, and username and pw meet the requirements.
        """
        hash = generate_password_hash(password)

        result = self.modify_query(
            """
            INSERT INTO users (username, email, hash)
            VALUES (?, ?)
            """, (username, email, hash))
        
        logger.info(f"User '{username}' registered")
        return result

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


if __name__ == "__main__":
    am = AccountManager()
    