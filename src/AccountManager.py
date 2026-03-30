from CommonQueries import CommonQueries
from werkzeug.security import check_password_hash, generate_password_hash


class AccountManager(CommonQueries):
    """
    This class handles login, registration, and account deletion.
    - User rank among active players.
    """

    def login(self, username, password, session) -> bool:
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
            return 0

        hash = generate_password_hash(password)
        # update DB with username and pw hash.
        return self.modify_query(
            "INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash)
            )
