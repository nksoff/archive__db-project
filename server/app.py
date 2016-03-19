import MySQLdb
from flask import Flask

app = Flask(__name__)
app.debug = True

database_config = {
        'host': 'localhost',
        'user': 'db',
        'passwd': 'db',
        'db': 'db'
        }


def get_db():
    database = MySQLdb.connect(**database_config)
    database.set_character_set('utf8')
    return database

global_db = get_db()
def sql_in(values):
    return ','.join(map(global_db.literal, values))
