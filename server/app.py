from flask import Flask
from flaskext.mysql import MySQL

app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'db'
app.config['MYSQL_DATABASE_PASSWORD'] = 'db'
app.config['MYSQL_DATABASE_DB'] = 'db'

mysql = MySQL()
mysql.init_app(app)

def get_db():
    return mysql.get_db()

global_db = get_db()
def sql_in(values):
    return ','.join(map(global_db.literal, values))
