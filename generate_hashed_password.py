# generate_hashed_password.py

from passlib.context import CryptContext

# Initialize the password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Replace "gxHovp^j8nv" with your actual password that needs to be hashed
password_to_hash = "gxHovp^j8nv"  # Replace with your secure password

# Generate the hashed password
hashed_password = pwd_context.hash(password_to_hash)

# Print the hashed password
print(f"Hashed password: {hashed_password}")