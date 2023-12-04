from werkzeug.security import check_password_hash, generate_password_hash
import datasource

def register_user(username, password):
    if username is None or password is None:
        raise ValueError("[username|password] cannot be None")

    existingUser = datasource.DB.execute("SELECT * from users WHERE username = ?", username)

    if existingUser:
        raise RunTimeError("Username already exist")

    db.execute(
        "INSERT INTO users (username, hash) VALUES (?,?)",
        username,
        generate_password_hash(password),
    )

def login_user(username, password):
    rows = datasource.DB.execute("SELECT * FROM users WHERE username = ?", username)

    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        return None

    return rows[0]

def get_user(user_id):
    userQuery = datasource.DB.execute("SELECT * FROM users WHERE id = ?", user_id)

    if len(userQuery) != 1:
        return None

    return userQuery[0]
