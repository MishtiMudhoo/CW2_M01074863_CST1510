import bcrypt
import os
import re
from pathlib import Path 

USER_DATA_FILE = Path("users.txt")


def hash_password(plain_text_password: str) -> str:
	"""Hash a plaintext password using bcrypt and return the string form.

	Args:
		plain_text_password: The plaintext password to hash.

	Returns:
		The bcrypt hash as a UTF-8 string.
	"""
	# Encode to bytes
	password_bytes = plain_text_password.encode("utf-8")

	# Generate salt
	salt = bcrypt.gensalt()

	# Hash the password
	hashed = bcrypt.hashpw(password_bytes, salt)

	# Return decoded string form
	return hashed.decode("utf-8")


def verify_password(plain_text_password: str, hashed_password: str) -> bool:
	"""Verify a plaintext password against a stored bcrypt hash.

	Args:
		plain_text_password: The password to verify.
		hashed_password: The stored bcrypt hash string.

	Returns:
		True if password matches, False otherwise.
	"""
	try:
		pw_bytes = plain_text_password.encode("utf-8")
		hash_bytes = hashed_password.encode("utf-8")
		return bcrypt.checkpw(pw_bytes, hash_bytes)
	except Exception:
		return False


def user_exists(username: str) -> bool:
	"""Return True if `username` exists in the USER_DATA_FILE."""
	if not USER_DATA_FILE.exists():
		return False

	with USER_DATA_FILE.open("r", encoding="utf-8") as f:
		for line in f:
			parts = line.strip().split(",")
			if len(parts) >= 1 and parts[0] == username:
				return True
	return False


def register_user(username: str, password: str, role: str = "user") -> tuple:
	"""Register a new user by hashing their password and storing credentials.

	Returns (success: bool, message: str).
	"""
	if user_exists(username):
		return False, f"Username '{username}' already exists."

	hashed = hash_password(password)

	# Append to file as: username,hashed_password,role
	with USER_DATA_FILE.open("a", encoding="utf-8") as f:
		f.write(f"{username},{hashed},{role}\n")

	return True, f"User '{username}' registered successfully."


def login_user(username: str, password: str) -> tuple:
	"""Authenticate a user by verifying username and password.

	Returns (success: bool, message: str).
	"""
	if not USER_DATA_FILE.exists():
		return False, "No users registered yet."

	with USER_DATA_FILE.open("r", encoding="utf-8") as f:
		for line in f:
			parts = line.strip().split(",")
			if len(parts) >= 2 and parts[0] == username:
				stored_hash = parts[1]
				if verify_password(password, stored_hash):
					return True, f"Welcome, {username}!"
				else:
					return False, "Invalid password."

	return False, "Username not found."


def validate_username(username: str) -> tuple:
	"""Validate username: 3-20 alphanumeric characters.

	Returns (is_valid: bool, error_message: str)
	"""
	if not username:
		return False, "Username cannot be empty."
	if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
		return False, "Username must be 3-20 characters: letters, numbers, or underscore."
	return True, ""


def validate_password(password: str) -> tuple:
	"""Validate password strength. Returns (is_valid, error_msg).

	Rules: 6-50 chars, contains letters and digits (basic check).
	"""
	if not password:
		return False, "Password cannot be empty."
	if len(password) < 6:
		return False, "Password must be at least 6 characters long."
	if len(password) > 50:
		return False, "Password must be 50 characters or fewer."
	if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
		return False, "Password must contain both letters and numbers."
	return True, ""


def display_menu():
	print("\n" + "=" * 50)
	print("  MULTI-DOMAIN INTELLIGENCE PLATFORM")
	print("  Secure Authentication System")
	print("=" * 50)
	print("\n[1] Register a new user")
	print("[2] Login")
	print("[3] Exit")
	print("-" * 50)


def main():
	print("\nWelcome to the Week 7 Authentication System!")

	while True:
		display_menu()
		choice = input("\nPlease select an option (1-3): ").strip()

		if choice == "1":
			print("\n--- USER REGISTRATION ---")
			username = input("Enter a username: ").strip()
			is_valid, err = validate_username(username)
			if not is_valid:
				print(f"Error: {err}")
				continue

			password = input("Enter a password: ").strip()
			is_valid, err = validate_password(password)
			if not is_valid:
				print(f"Error: {err}")
				continue

			password_confirm = input("Confirm password: ").strip()
			if password != password_confirm:
				print("Error: Passwords do not match.")
				continue

			success, msg = register_user(username, password)
			if success:
				print(f"Success: {msg}")
			else:
				print(f"Error: {msg}")

		elif choice == "2":
			print("\n--- USER LOGIN ---")
			username = input("Enter your username: ").strip()
			password = input("Enter your password: ").strip()

			success, msg = login_user(username, password)
			if success:
				print(f"\nSuccess: {msg}")
				input("\nPress Enter to return to main menu...")
			else:
				print(f"Error: {msg}")

		elif choice == "3":
			print("\nThank you for using the authentication system.")
			print("Exiting...")
			break

		else:
			print("\nError: Invalid option. Please select 1, 2, or 3.")


if __name__ == "__main__":
	main()

