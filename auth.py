from werkzeug.security import generate_password_hash, check_password_hash
from db import get_user_by_email, create_user

def register(email, password):
    if get_user_by_email(email):
        return None, "email already in use"
    password_hash = generate_password_hash(password)
    user_id = create_user(email, password_hash)
    return user_id, None

def login(email, password):
    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return None, "invalid email or password"
    return user["id"], None
