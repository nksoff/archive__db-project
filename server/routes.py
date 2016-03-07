import MySQLdb
from app import *

@app.route('/')
def hello():
    return 'hello!'
