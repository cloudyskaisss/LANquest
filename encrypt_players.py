# imports
import json, os, stat
from cryptography.fernet import Fernet

# setup vars
KEY_FILE = "players.key"
DATA_FILE = "players.json.enc"

# secure the key file, so it cant be read or written outside of us. yes, this can still be exploited by running the "get_saved_players" command. however, nobody except for the host can edit player information, unless they run a "pdata["field"] == "value" command, which is impossible. as far as i can tell, this is a completely secure setup.
def _secure_key_file(path):
    """Set file permissions to owner-only (best-effort on Windows)."""
    if os.name == "nt":  #  Windows
        #  Windows doesn't support chmod 0o600, but we can clear read/write for 'others'
        os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
    else:  #  Linux/Mac
        os.chmod(path, 0o600)

# get the key.
def _get_cipher():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        _secure_key_file(KEY_FILE)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)

# save player data, completely encrypted.
def save_players_encrypted(obj, path=DATA_FILE):
    cipher = _get_cipher()
    plaintext = json.dumps(obj, indent=2).encode("utf-8")
    ciphertext = cipher.encrypt(plaintext)
    with open(path, "wb") as f:
        f.write(ciphertext)

# load player data and decrypt it.
def load_players_encrypted(path=DATA_FILE):
    if not os.path.exists(path):
        return {}
    cipher = _get_cipher()
    with open(path, "rb") as f:
        ciphertext = f.read()
    plaintext = cipher.decrypt(ciphertext)
    return json.loads(plaintext.decode("utf-8"))
