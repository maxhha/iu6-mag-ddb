from bson import ObjectId
from flask import Flask, abort, redirect, render_template, request
from flask_wtf.csrf import CSRFProtect

from db import db
from forms import CreateOwnerForm, RegisterCooperativeForm, TransferMembershipForm


app = Flask(__name__)
app.config.from_pyfile("settings.py")
csrf = CSRFProtect(app)


@app.route("/", methods=["GET"])
def index():
    cooperatives = list(db.cooperatives.find(limit=25, sort=[('name', 1)]))
    return render_template("pages/index.html", cooperatives=cooperatives)


@app.route("/cooperatives/register", methods=["GET", "POST"])
def register_cooperative():
    form = RegisterCooperativeForm()
    if form.validate_on_submit():
        form.save()
        return redirect('/', code=302)

    return render_template("pages/cooperatives/register.html", form=form)


@app.route("/cooperatives/<cooperative_id>/memberships", methods=["GET"])
def view_cooperative_memberships(cooperative_id):
    try:
        cooperative_id = ObjectId(cooperative_id)
    except:
        return abort(400)

    cooperative = db.cooperatives.find_one({"_id": cooperative_id})
    if not cooperative:
        return abort(404)

    all_memberships = list(db.memberships.find({"cooperative_id": cooperative_id}, sort=[("number", -1)]))

    owners_set = {m.get("owner_id") for m in all_memberships}
    owners_filter = {"_id": {"$in": list(owners_set)}}
    search = request.args.get("q", "")
    if search:
        owners_filter["name"] = {
            "$regex": search,
            "$options": "i",
        }

    owners = {o["_id"]: o for o in db.owners.find(owners_filter)}
    showed_owners = set()

    memberships = []
    for member in all_memberships:
        owner_id = member.get('owner_id')
        member["can_transfer"] = owner_id not in showed_owners and member.get("amount", 0) > 0
        member["owner"] = owners.get(owner_id)
        showed_owners.add(owner_id)
        if member["owner"]:
            memberships.append(member)

    return render_template(
        "pages/cooperatives/memberships.html",
        cooperative=cooperative,
        memberships=memberships,
        search=search
    )


@app.route("/memberships/<membership_id>/transfer", methods=["GET", "POST"])
def transfer_membership(membership_id):
    try:
        membership_id = ObjectId(membership_id)
    except:
        return abort(400)

    membership = db.memberships.find_one({"_id": membership_id})
    if not membership:
        return abort(404)

    membership["owner"] = db.owners.find_one({"_id": membership.get("owner_id")})
    membership["cooperative"] = db.cooperatives.find_one({"_id": membership.get("cooperative_id")})

    form = TransferMembershipForm(membership)
    if form.validate_on_submit():
        form.save()
        return redirect(f"/cooperatives/{membership['cooperative_id']}/memberships", code=302)

    return render_template("pages/memberships/transfer.html", form=form)


@app.route("/cooperatives/search", methods=["GET"])
def search_cooperative():
    filter = {}
    search = request.args.get("q", "")
    if search:
        filter["name"] = {
            "$regex": search,
            "$options": "i",
        }
    cooperatives = list(db.cooperatives.find(filter, limit=25, sort=[('name', 1)]))

    return render_template("pages/cooperatives/search.html", cooperatives=cooperatives, search=search)


@app.route("/owners", methods=["GET"])
def list_owners():
    owners = list(db.owners.find(limit=25, sort=[('name', 1)]))
    return render_template("pages/owners/index.html", owners=owners)


@app.route("/owners/create", methods=["GET", "POST"])
def create_owner():
    form = CreateOwnerForm()
    if form.validate_on_submit():
        form.save()
        return redirect("/owners", code=302)

    return render_template("pages/owners/create.html", form=form)


@app.route("/owners/search", methods=["GET"])
def search_owner():
    filter = {}
    search = request.args.get("q", "")
    if search:
        filter["name"] = {
            "$regex": search,
            "$options": "i",
        }
    owners = list(db.owners.find(filter, limit=25, sort=[('name', 1)]))

    return render_template("pages/owners/search.html", owners=owners, search=search)
