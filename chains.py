from db import db
import users
from sqlalchemy.sql import text

def get_list():
    sql = text("SELECT C.subject, C.first_message, U.username, C.area_id FROM chains C, users U WHERE C.user_id=U.id ORDER BY C.id")
    result = db.session.execute(sql)
    return result.fetchall()

def get_id(id):
    sql = text("SELECT id FROM chains WHERE area_id=:id")
    result = db.session.execute(sql, {"id":id})
    return result.fetchall()

def get_subject(id):
    sql = text("SELECT subject FROM chains WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    return result.fetchone()[0]

def get_first_message(id):
    sql = text("SELECT first_message FROM chains WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    return result.fetchone()[0]

def get_own_chains(user_id):
    sql = text("SELECT id, subject, first_message FROM chains WHERE user_id=:user_id ORDER BY id")
    return db.session.execute(sql, {"user_id":user_id}).fetchall()

def create(area_id, subject, first_message):
    user_id = users.user_id()
    sql = text("INSERT INTO chains (area_id, subject, first_message, user_id) VALUES (:area_id, :subject, :first_message, :user_id)")
    db.session.execute(sql, {"area_id":area_id, "subject":subject, "first_message":first_message, "user_id":user_id})
    db.session.commit()

def in_area(id):
    area = id
    sql = text("SELECT :area AS area, COUNT(*) FROM chains WHERE area_id=:id")
    result = db.session.execute(sql, {"id":id, "area":area})
    return result.fetchall()

def edit_first_message(id, first_message):
    sql = text("UPDATE chains SET first_message=:first_message WHERE id=:id")
    db.session.execute(sql, {"id":id, "first_message":first_message})
    db.session.commit()

def edit_subject(id, subject):
    sql = text("UPDATE chains SET subject=:subject WHERE id=:id")
    db.session.execute(sql, {"id":id, "subject":subject})
    db.session.commit()