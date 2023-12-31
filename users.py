from db import db
from flask import session, abort, request
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text
import os

def login(username,password):
    sql = text("SELECT id, password, role FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = username
            session["user_role"] = user.role
            session['csrf_token'] = os.urandom(16).hex()
            return True
        else:
            return False

def logout():
    del session["user_id"]
    del session["username"]
    del session["user_role"]

def register(username, password, role):
    hash_value = generate_password_hash(password)
    try:
        sql = text("INSERT INTO users (username, password, role) VALUES (:username,:password,:role)")
        db.session.execute(sql, {"username":username, "password":hash_value, "role":role})
        db.session.commit()
    except:
        return False
    return login(username,password)

def user_id():
    return session.get("user_id",0)

def require_role(role):
    if role > session.get('user_role', 0):
        abort(403)

def check_csrf():
    if session['csrf_token'] != request.form['csrf_token']:
        abort(403)