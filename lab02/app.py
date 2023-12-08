from flask import Flask, redirect, render_template, request
from flask_wtf.csrf import CSRFProtect

from db import db
from forms import CreateSerialForm


app = Flask(__name__)
app.config.from_pyfile("settings.py")
csrf = CSRFProtect(app)


@app.route("/", methods=["GET"])
def index():
    serials = list(db.serials.find(limit=25, sort=[('created_at', -1)]))
    return render_template("pages/index.html", serials=serials)


@app.route("/serials/create", methods=["GET", "POST"])
def create_serials():
    form = CreateSerialForm()
    if form.validate_on_submit():
        form.save()
        return redirect('/', code=302)

    return render_template("pages/serials/create.html", form=form)


@app.route("/serials/search", methods=["GET"])
def search():
    filter = {}
    search = request.args.get("q", "")
    if search:
        filter["title"] = {
            "$regex": search,
            "$options": "i",
        }
    serials = list(db.serials.find(filter, limit=25, sort=[('created_at', -1)]))

    return render_template("pages/serials/search.html", serials=serials, search=search)
