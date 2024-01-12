import base64
import hashlib
import os

# Password manager manages the password storing and validating
filename = "secrets.txt"


def save_username_and_password(username, password):
    salt, secured_password = secure_password(password)
    save_password(username,salt, secured_password)

def secure_password(password):
    salt = os.urandom(32)
    secure_password = secure_password_with_salt(password, salt)
    return salt, secure_password

def secure_password_with_salt(password, salt):
    print(salt)
    password_salted = password.encode() + salt
    secure_password = hashlib.sha256(password_salted).hexdigest()

    return secure_password

def is_username_already_stored(username):
    if not os.path.exists(filename):
        return False
    with open(filename, 'r') as f:
        for line in f:
            saved_username, saved_salt, saved_password = line.strip().split(';')
            if saved_username == username:
                return True
    return False

def save_password(username, salt, password):
    salt = base64.b64encode(salt).decode('utf-8')
    with open(filename, 'a') as f:
        f.write(f'{username};{salt};{password}\n')

def validate_password(username, entered_password):
    if not os.path.exists(filename):
        return True
    with open(filename, 'r') as f:
        for line in f:
            saved_username, saved_salt, saved_password = line.strip().split(';')
            saved_salt = base64.b64decode(saved_salt)
            print(saved_salt)
            if saved_username == username:
                entered_hashed_password = secure_password_with_salt(entered_password, salt=saved_salt)
                if entered_hashed_password == saved_password:
                    return True
                else:
                    return False
    return False
