from DbManager import DbManager
from werkzeug.security import check_password_hash, generate_password_hash


class AccountManager(DbManager):
    """
    This class handles login, registration, and account deletion.
    - User rank among active players.
    """

    def login(self, username, password, session):
        # Query database for username
        rows = self.select_query(
            "SELECT * FROM users WHERE username = ?", (username, )
            )
        
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], password
        ):
            return False

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        return True

    def register(self, username, password):
        # Make sure name isn't already used.
        check_name = self.select_query(
            "SELECT username FROM users WHERE username = ?", (username, )
                                )
        if check_name:
            return False

        hash = generate_password_hash(password)
        # update DB with username and pw hash.
        return self.modify_query(
            "INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash)
            )
