# -*- coding: utf-8 -*-
import MySQLdb
from app import *
from helpers import *

@app.route('/db/api/status/', methods=['GET'])
def status():
    cursor = database.cursor()

    response = {}

    for entity in ['user', 'thread', 'forum', 'post']:
        cursor.execute('SELECT COUNT(*) FROM %ss' % entity.capitalize())
        data = cursor.fetchone()
        response[entity] = data[0]

    return result(response)

@app.route('/db/api/clear/', methods=['POST'])
def clear():
    # TODO:
    return result("OK")

@app.route('/db/api/user/create/', methods=['POST'])
def user_create():
    # TODO:
    return result({})

@app.route('/db/api/user/details/', methods=['GET'])
def user_details():
    # TODO:
    return result({})

@app.route('/db/api/user/follow/', methods=['POST'])
def user_follow():
    # TODO:
    return result({})

@app.route('/db/api/user/listFollowers/', methods=['GET'])
def user_list_followers():
    # TODO:
    return result({})

@app.route('/db/api/user/listFollowing/', methods=['GET'])
def user_list_following():
    # TODO:
    return result({})

@app.route('/db/api/user/listPosts/', methods=['GET'])
def user_list_posts():
    # TODO:
    return result({})

@app.route('/db/api/user/unfollow/', methods=['POST'])
def user_unfollow():
    # TODO:
    return result({})

@app.route('/db/api/user/updateProfile/', methods=['POST'])
def user_update_profile():
    # TODO:
    return result({})
