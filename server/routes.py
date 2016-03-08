# -*- coding: utf-8 -*-
import MySQLdb
from app import *
from flask import jsonify

@app.route('/db/api/status/', methods=['GET'])
def status():
    cursor = database.cursor()

    response = {}

    for entity in ['user', 'thread', 'forum', 'post']:
        cursor.execute('SELECT COUNT(*) FROM %ss' % entity.capitalize())
        data = cursor.fetchone()
        response[entity] = data[0]

    return jsonify({
            "code": 0,
            "reponse": response
            })
