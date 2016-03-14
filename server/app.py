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

database = MySQLdb.connect(**database_config)
