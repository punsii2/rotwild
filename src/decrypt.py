import base64
import secrets

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def _generate_salt():
    return secrets.token_bytes(16)


def _derive_key(salt, password: str):
    kdf = Scrypt(salt=salt, length=32, n=2 ** 20, r=8, p=1)
    return kdf.derive(password.encode())


def _generate_key(password: str):
    salt = open("./src/salt.salt", "rb").read()
    derived_key = _derive_key(salt, password)
    return base64.urlsafe_b64encode(derived_key)


def _encrypt(filename: str, key):
    fernet = Fernet(key)

    with open(filename, "rb") as data_file:
        data = data_file.read()

    encrypted_data = fernet.encrypt(data)

    with open(filename + ".enc", "wb") as encrypted_file:
        encrypted_file.write(encrypted_data)


def _decrypt(filename: str, key):
    fernet = Fernet(key)
    with open(filename, "rb") as encrypted_file:
        encrypted_data = encrypted_file.read()

    data = b""
    data = fernet.decrypt(encrypted_data)

    return data


def decrypt_with_password(filename: str, password: str):
    key = _generate_key(password)
    return _decrypt(filename, key).decode()


def main():
    # open("salt.salt", "wb").write(_generate_salt())
    key = _generate_key("example_password")
    # _encrypt("../red_deer_berchtesgarden_national_park.csv", key)
    data = _decrypt("./red_deer_berchtesgarden_national_park.csv.enc", key)


if __name__ == "__main__":
    main()
