from db import db
import users
from sqlalchemy.sql import text

def get_list(id):
    list = []
    sql = text("SELECT M.content, U.username, M.sent_at FROM messages M, users U, chains C WHERE M.chain_id=:id AND M.user_id=U.id ORDER BY M.id DESC")
    results = db.session.execute(sql, {"id":id}).fetchall()
    for result in results:
        if result in list:
            pass
        else:
            list.append(result)
    return list

def send(content, chain_id):
    user_id = users.user_id()
    if user_id == 0:
        return False
    sql = text("INSERT INTO messages (content, user_id, sent_at, chain_id, visible) VALUES (:content, :user_id, NOW(), :chain_id, TRUE)")
    db.session.execute(sql, {"content":content, "user_id":user_id, "chain_id":chain_id})
    db.session.commit()
    return True

def in_area(id):
    area = id
    sql = text("SELECT :area as area, COUNT(M) FROM messages M, areas A, chains C WHERE C.id=M.chain_id AND A.id=:id AND C.area_id=A.id")
    result = db.session.execute(sql, {"id":id, "area":area})
    return result.fetchall()

def search_messages(keyword):
    sql = text("SELECT id, content, user_id, sent_at, chain_id, visible FROM messages WHERE content LIKE :content ORDER BY sent_at DESC")
    result = db.session.execute(sql, {"content":"%"+keyword+"%"})
    messages = result.fetchall()
    return messages

def remove_message(id, user_id):
    sql = text("UPDATE messages SET visible=FALSE WHERE id=:id AND user_id=:user_id")
    db.session.execute(sql, {"id":id, "user_id":user_id})
    db.session.commit()