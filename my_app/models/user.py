"""
User Entity Class
Represents a user in the system
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """User entity representing a system user"""
    username: str
    password: str
    role: str  # "Cyber Security", "Data Scientist", "IT Operations"
    
    def __post_init__(self):
        """Validate user data after initialization"""
        if not self.username:
            raise ValueError("Username cannot be empty")
        if not self.password:
            raise ValueError("Password cannot be empty")
        if self.role not in ["Cyber Security", "Data Scientist", "IT Operations"]:
            raise ValueError(f"Invalid role: {self.role}")
    
    def validate_password(self) -> tuple[bool, Optional[str]]:
        """
        Validate password meets requirements
        
        Returns:
            tuple: (is_valid, error_message)
        """
        has_capital = any(char.isupper() for char in self.password)
        has_number = any(char.isdigit() for char in self.password)
        
        if not has_capital or not has_number:
            missing = []
            if not has_capital:
                missing.append("at least one capital letter")
            if not has_number:
                missing.append("at least one number")
            error_msg = f"Password must contain: {', and '.join(missing)}."
            return False, error_msg
        
        return True, None
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            "username": self.username,
            "password": self.password,
            "role": self.role
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create user from dictionary"""
        return cls(
            username=data["username"],
            password=data["password"],
            role=data["role"]
        )

