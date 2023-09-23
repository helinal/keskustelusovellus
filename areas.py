from db import db
from sqlalchemy.sql import text

def get_list():
    sql = text("SELECT id, name FROM areas WHERE visible=1 ORDER BY id")
    result = db.session.execute(sql)
    return result.fetchall()

def get_name(id):
    sql = text("SELECT name FROM areas WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    return result.fetchone()[0]

def get_own_areas(user_id):
    sql = text("SELECT id, name FROM areas WHERE user_id=:user_id ORDER BY name")
    return db.session.execute(sql, {"user_id":user_id}).fetchall()

def add_area(name, user_id):
    sql = text("INSERT INTO areas (name, user_id, visible) VALUES (:name, :user_id, 1) RETURNING id")
    db.session.execute(sql, {"name":name, "user_id":user_id}).fetchone()[0]
    db.session.commit()

def remove_area(id, user_id):
    sql = text("UPDATE areas SET visible=0 WHERE id=:id AND user_id=:user_id")
    db.session.execute(sql, {"id":id, "user_id":user_id})
    db.session.commit()