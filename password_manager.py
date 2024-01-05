import hashlib
import os

filename = "secrets.txt"


def save_username_and_password(username, password):
    salt, secured_password = secure_password(password)
    save_password(username,salt, secured_password)

def secure_password(password):
    salt = os.urandom(32)
    secure_password = secure_password_with_salt(password, salt)
    return salt, secure_password

def secure_password_with_salt(password, salt):
    password_salted = password.encode() + salt
    secure_password = hashlib.sha256(password_salted).hexdigest()

    return secure_password

def is_username_already_stored(username):
    with open('user_credentials.txt', 'r') as f:
        for line in f:
            saved_username, saved_salt, saved_password = line.strip().split(';')
            if saved_username == username:
                return True
    return False

def save_password(username, salt, password):
    with open(filename, 'a') as f:
        f.write(f'{username};{salt};{password}\n')

def validate_password(username, entered_password):
    with open('user_credentials.txt', 'r') as f:
        for line in f:
            saved_username, saved_salt, saved_password = line.strip().split(';')
            if saved_username == username:
                entered_hashed_password = secure_password_with_salt(entered_password, salt=saved_salt)
                if entered_hashed_password == saved_password:
                    return True
                else:
                    return False
    return False
