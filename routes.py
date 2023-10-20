from app import app
from flask import flash, render_template, request, redirect
import messages, users, areas, chains
from db import db
from sqlalchemy.sql import text

@app.route("/")
def index():
    list_areas = areas.get_list()
    list_chains = []
    list_messages = []
    for area in list_areas:
        list_chains.append(chains.in_area(area[0]))
        list_messages.append(messages.in_area(area[0]))
    return render_template("index.html", count=len(list_areas), areas=list_areas, messages=list_messages, chains=list_chains)

@app.route("/send", methods=["POST"])
def send():
    users.check_csrf()
    content = request.form["content"]
    if len(content.strip()) == 0:
        return render_template('error.html', message='Viesti ei voi olla tyhjä')
    if len(content.strip()) > 450:
        return render_template('error.html', message='Liian pitkä viesti. Viestin tulee olla 1-450 merkkiä pitkä.')

    chain_id = request.form["chain_id"]
    if messages.send(content, chain_id):
        flash("Viesti lähetetty")
        return redirect("/chain/"+chain_id)
    else:
        return render_template("error.html", message="Viestin lähetys ei onnistunut")

@app.route("/add", methods=["GET", "POST"])
def add_area():
    if request.method == "GET":
        return render_template("add.html")
    if request.method == "POST":
        users.require_role(2)
        users.check_csrf()
        name = request.form["name"]
        if len(name) < 1 or len(name) > 25:
            return render_template("error.html", message="Keskustelualueen nimen tulee olla 1-25 merkkiä pitkä")

        areas.add_area(name, users.user_id())
        flash("Keskustelualue luotu")
        return redirect("/")
    
@app.route("/remove", methods=["GET", "POST"])
def remove():
    users.require_role(2)
    if request.method == "GET":
        list = areas.get_own_areas(users.user_id())
        return render_template("remove.html", list=list)
    if request.method == "POST":
        users.check_csrf()
        if "area" in request.form:
            area_id = request.form["area"]
            areas.remove_area(area_id, users.user_id())
            flash("Viestialue poistettu")
        return redirect("/")

@app.route("/create", methods=["POST"])
def create_chain():
    users.check_csrf()
    if request.method == "POST":
        subject = request.form["subject"]
        if len(subject) < 1 or len(subject) > 50:
            return render_template("error.html", message="Otsikon tulee olla 1-50 merkkiä pitkä")
        
        first_message = request.form["first_message"]
        if len(first_message) < 1 or len(first_message) > 300:
            return render_template("error.html", message="Aloitusviestin tulee olla 1-300 merkkiä pitkä")
    
        area_id = request.form["area_id"]

        if users.user_id() == 0:
            render_template("error.html", message="Ketjun luominen ei onnistunut")
        else:
            chains.create(area_id, subject, first_message)
            flash("Viestiketju luotu")
            return redirect("/area/"+area_id)

@app.route("/chain/<int:id>")
def chain(id):
    subject = chains.get_subject(id)
    first_message = chains.get_first_message(id)
    list = messages.get_list(id)

    likecounts = []
    dislikecounts = []

    for message in list:
        likecount = messages.likecount(message.id)
        dislikecount = messages.dislikecount(message.id)
        likecounts.append(likecount.scalar())
        dislikecounts.append(dislikecount.scalar())

    return render_template("chain.html", id=id, subject=subject, first_message=first_message,
                            count=len(list), messages=list, likecounts=likecounts, dislikecounts=dislikecounts)

@app.route("/area/<int:id>")
def area(id):
    name = areas.get_name(id)
    sql = text("SELECT id, subject, first_message FROM chains WHERE area_id=:id AND visible=TRUE ORDER BY id DESC")
    result = db.session.execute(sql, {"id":id})
    chains = result.fetchall()
    return render_template("area.html", id=id, name=name, chains=chains)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        users.check_csrf()
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            flash("Kirjauduttu sisään")
            return redirect("/")
        else:
            return render_template("error.html", message="Väärä tunnus tai salasana")

@app.route("/logout")
def logout():
    users.logout()
    flash("Kirjauduttu ulos")
    return redirect("/")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        users.check_csrf()
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        if password1 != password2:
            return render_template("error.html", message="Salasanat eivät täsmää")
        if len(password1.strip()) == 0:
            return render_template("error.html", message="Salasana ei voi olla tyhjä")

        role = request.form['role']
        if role not in ('1', '2'):
            return render_template("error.html", message="Tuntematon käyttäjärooli")
        
        if users.register(username, password1, role):
            flash("Rekisteröinti onnistui")
            return redirect("/")
        else:
            return render_template("error.html", message="Rekisteröinti ei onnistunut")
        
@app.route("/search_messages", methods=["POST"])
def search():
    users.check_csrf()
    keyword = request.form["content"]
    if len(keyword.strip()) == 0:
        return render_template("error.html", message="Hakusana ei voi olla tyhjä")
    messages_found = messages.search_messages(keyword)
    return render_template("search_results.html", messages_found=messages_found, keyword=keyword)

@app.route("/search")
def create_search():
    return render_template("search_messages.html")

@app.route("/edit_subject", methods=["GET", "POST"])
def edit_subject():
    if request.method == "GET":
        list = chains.get_own_chains(users.user_id())
        return render_template("edit_subject.html", list=list)

    if request.method == "POST":
        users.check_csrf()
        if "chain" in request.form:
            chain_id = request.form["chain"]
            subject = request.form["subject"]
            chains.edit_subject(chain_id, subject)
            flash("Ketjun otsikkoa muokattu")
        return redirect("/chain/"+chain_id)
    
@app.route("/edit_message", methods=["GET", "POST"])
def edit_message():
    if request.method == "GET":
        list = messages.get_own_messages(users.user_id())
        return render_template("edit_message.html", list=list)

    if request.method == "POST":
        users.check_csrf()
        if "message" in request.form:
            message_id= request.form["message"]
            content = request.form["newmessage"]
            messages.edit_message(message_id, content)
            flash("Viesti muokattu")
        return redirect("/")
    
@app.route("/delete_message", methods=["GET", "POST"])
def delete_message():
    if request.method == "GET":
        list = messages.get_own_messages(users.user_id())
        return render_template("delete_message.html", list=list)
    
    if request.method == "POST":
        users.check_csrf()
        if "message" in request.form:
            message_id = request.form["message"]
            messages.delete_message(message_id, users.user_id())
            flash("Viesti poistettu")
        return redirect("/")
    
@app.route("/delete_chain", methods=["GET", "POST"])
def delete_chain():
    if request.method == "GET":
        list = chains.get_own_chains(users.user_id())
        return render_template("delete_chain.html", list=list)
    
    if request.method == "POST":
        users.check_csrf()
        if "chain" in request.form:
            chain_id = request.form["chain"]
            chains.delete_chain(chain_id, users.user_id())
            flash("Ketju poistettu")
        return redirect("/")
    
@app.route("/like-message/<int:message_id>", methods=["POST"])
def like_message(message_id):
    action = request.form.get("action")
    if action == "like" or "dislike":
        user_id = users.user_id()
        like_check = messages.check_like(message_id, user_id)

        if like_check:
            return render_template("error.html", message = "Olet jo arvostellut tämän viestin")
        
        messages.add_like(action, user_id, message_id)
        flash("Viesti arvioitu")
    return redirect("/")