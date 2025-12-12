"""
User Service
Business logic for user management
"""

from typing import Optional, Tuple
from ..models.user import User
from ..repositories.user_repository import UserRepository


class UserService:
    """Service for user-related business logic"""
    
    def __init__(self, repository: UserRepository = None):
        """
        Initialize service
        
        Args:
            repository: User repository instance (creates new one if None)
        """
        self.repository = repository if repository is not None else UserRepository(use_database=True)
    
    def register_user(self, username: str, password: str, role: str) -> Tuple[bool, Optional[str]]:
        """
        Register a new user
        
        Args:
            username: Username
            password: Password (will be hashed)
            role: User role
            
        Returns:
            tuple: (success, error_message)
        """
        # Check if username exists
        if self.repository.exists(username):
            return False, "Username already exists. Choose another one."
        
        # Create user entity (password will be hashed in repository)
        try:
            user = User(username=username, password=password, role=role)
        except ValueError as e:
            return False, str(e)
        
        # Validate password
        is_valid, error_msg = user.validate_password()
        if not is_valid:
            return False, error_msg
        
        # Save user (repository will hash password if using database)
        if self.repository.create(user):
            return True, None
        return False, "Failed to create user"
    
    def login(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate and login user
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User if authenticated, None otherwise
        """
        return self.repository.authenticate(username, password)
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.repository.find_by_username(username)

