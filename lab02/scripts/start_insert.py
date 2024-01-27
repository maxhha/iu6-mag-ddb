from settings import DATABASE_URI
from pymongo import MongoClient

db = MongoClient(host=DATABASE_URI).get_default_database()

o1, o2, o3 = db.owners.insert_many([{
    "name": "Иванов Иван Иванович",
    "address": "Январская улица, д 1",
    "residence": "Россия",
    "passport": "1111222233334444",
}, {
    "name": "Петухов Петр Петрович",
    "address": "Январская улица, д 1",
    "residence": "Россия",
    "passport": "1111222233334444",
}, {
    "name": "Кузнецов Кирилл Кириллович",
    "address": "Январская улица, д 1",
    "residence": "Россия",
    "passport": "1111222233334444",
}]).inserted_ids

c1, c2, c3 = db.cooperatives.insert_many([{
    "name": "Мир овощей",
    "residence": "Россия",
    "workers_number": 11,
    "capital_amount": 101,
    "profile": "Продукты",
}, {
    "name": "Мир пуговиц",
    "residence": "Россия",
    "workers_number": 22,
    "capital_amount": 304,
    "profile": "Галантерея",
}, {
    "name": "Мир ручек",
    "residence": "Россия",
    "workers_number": 33,
    "capital_amount": 609,
    "profile": "Канцелярия",
}]).inserted_ids

today = "2024-01-01"

db.memberships.insert_many([{
    "number": 1,
    "owner_id": o1, "cooperative_id": c1,
    "amount": 101,
    "date": today,
}, {
    "number": 2,
    "owner_id": o1, "cooperative_id": c2,
    "amount": 102,
    "date": today,
}, {
    "number": 3,
    "owner_id": o2, "cooperative_id": c2,
    "amount": 202,
    "date": today,
}, {
    "number": 4,
    "owner_id": o1, "cooperative_id": c3,
    "amount": 103,
    "date": today,
}, {
    "number": 5,
    "owner_id": o2, "cooperative_id": c3,
    "amount": 203,
    "date": today,
}, {
    "number": 6,
    "owner_id": o3, "cooperative_id": c3,
    "amount": 303,
    "date": today,
}])

db.memberships.create_index("owner_id")
db.memberships.create_index("cooperative_id")
