
from flask import current_app, g
from werkzeug.local import LocalProxy
from pymongo import MongoClient
from pymongo.database import Database


def get_db() -> Database:
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = MongoClient(host=current_app.config.get('DATABASE_URI')).get_default_database()

    return db


db: Database = LocalProxy(get_db)
