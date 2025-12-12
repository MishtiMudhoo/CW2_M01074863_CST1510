"""
User Repository
Handles user data persistence using database
"""

import sys
import os
from typing import Optional, Dict
from pathlib import Path

# Add parent directory to path for app imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user
import bcrypt
from ..models.user import User


class UserRepository:
    """Repository for user data management using SQLite database"""
    
    def __init__(self, use_database: bool = True):
        """
        Initialize repository
        
        Args:
            use_database: If True, use database; if False, use in-memory storage
        """
        self.use_database = use_database
        self._storage = {} if not use_database else None
    
    def create(self, user: User) -> bool:
        """
        Create a new user
        
        Args:
            user: User entity to create
            
        Returns:
            bool: True if created, False if username already exists
        """
        if self.use_database:
            # Check if user exists
            existing = get_user_by_username(user.username)
            if existing:
                return False
            
            # Hash password using bcrypt
            password_bytes = user.password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            password_hash = hashed.decode('utf-8')
            
            # Insert into database
            insert_user(user.username, password_hash, user.role)
            return True
        else:
            # In-memory storage
            if user.username in self._storage:
                return False
            self._storage[user.username] = user.to_dict()
            return True
    
    def find_by_username(self, username: str) -> Optional[User]:
        """
        Find user by username
        
        Args:
            username: Username to search for
            
        Returns:
            User if found, None otherwise
        """
        if self.use_database:
            user_data = get_user_by_username(username)
            if user_data:
                # user_data is a tuple: (id, username, password_hash, role)
                return User(
                    username=user_data[1],
                    password=user_data[2],  # This is the hash, not plain password
                    role=user_data[3]
                )
            return None
        else:
            if username in self._storage:
                return User.from_dict(self._storage[username])
            return None
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User if authenticated, None otherwise
        """
        if self.use_database:
            user_data = get_user_by_username(username)
            if not user_data:
                return None
            
            # Verify password using bcrypt
            stored_hash = user_data[2]  # password_hash column
            password_bytes = password.encode('utf-8')
            hash_bytes = stored_hash.encode('utf-8')
            
            if bcrypt.checkpw(password_bytes, hash_bytes):
                # Return user with hashed password (for consistency)
                return User(
                    username=user_data[1],
                    password=stored_hash,  # Store hash, not plain password
                    role=user_data[3]
                )
            return None
        else:
            # In-memory storage (plain password comparison)
            user = self.find_by_username(username)
            if user and user.password == password:
                return user
            return None
    
    def get_all(self) -> list[User]:
        """Get all users"""
        if self.use_database:
            conn = connect_database()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash, role FROM users")
            users_data = cursor.fetchall()
            conn.close()
            return [
                User(username=u[1], password=u[2], role=u[3])
                for u in users_data
            ]
        else:
            return [User.from_dict(data) for data in self._storage.values()]
    
    def exists(self, username: str) -> bool:
        """Check if username exists"""
        if self.use_database:
            user_data = get_user_by_username(username)
            return user_data is not None
        else:
            return username in self._storage

