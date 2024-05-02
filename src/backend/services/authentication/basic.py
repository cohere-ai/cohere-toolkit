from backend.services.authentication.base import BaseAuthenticationStrategy
from backend.models.user import User
import bcrypt


class BasicAuthentication(BaseAuthenticationStrategy):
    """Basic email/password auth strategy."""

    @staticmethod
    def should_auth_redirect() -> bool:
        return False

    @staticmethod
    def hash_and_salt_password(plain_text_password: str) -> str:
        """
        Hashes a given plain-text password with a randomly generated salt.

        Args:
            plain_text_password (str): Password to hash.

        Returns:
            str: Hashed password
        """
        return bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt())

    @staticmethod
    def check_password(plain_text_password: str, hashed_password: str) -> bool: 
        """
        Hashes a given plain-text password with a randomly generated salt.

        Args:
            plain_text_password (str): Password to check.
            hashed_password (str): Password to check against.

        Returns:
            bool: Whether the plain-text password matches the given hashed password.
        """
        return bcrypt.checkpw(plain_text_password.encode("utf-8"), hashed_password)

    def login(self, plain_text_password: str, user: User) -> bool: 
        """
        Logs user in, checking the if the hashed input password corresponds to the
        one stored in the DB.

        Args:
            plain_text_password (str): Password to check.
            user (User): DB User.

        Returns:
            bool: Whether the user successfully logged in.
        """
        return self.check_password(plain_text_password, user.hashed_password)
