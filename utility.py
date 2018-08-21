import hmac
import hashlib

SECRET_KEY = b"It is a very big secret."

def init_hmac(secret_key):
    global SECRET_KEY
    SECRET_KEY = secret_key

def secrethash(msg):
    global SECRET_KEY
    return hmac.new(SECRET_KEY, msg.encode(), hashlib.sha1).hexdigest()

def make_secure_val(msg):
    return "{msg}|{hashed}".format(msg=msg, hashed=secrethash(msg))

def ret_secure_val(m):
    msg, hash_value = m.split("|")
    hashed = secrethash(msg)
    if hmac.compare_digest(hashed, hash_value.encode("ascii", "ignore")):
        print("number verified")
        return int(msg)
    else:
        print("fake number")