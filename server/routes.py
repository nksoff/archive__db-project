# -*- coding: utf-8 -*-
import MySQLdb
from app import *
from helpers import *

@app.errorhandler(400)
def bad_request(error):
    return result(error.description, CODE_INVALID), 400

@app.errorhandler(404)
def not_found(error):
    return result(error.description, CODE_NOT_FOUND), 404

### Common
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



### User
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



### Forum
@app.route('/db/api/forum/create/', methods=['POST'])
def forum_create():
    # TODO:
    return result({})

@app.route('/db/api/forum/details/', methods=['GET'])
def forum_details():
    # TODO:
    return result({})

@app.route('/db/api/forum/listPosts/', methods=['GET'])
def forum_list_posts():
    # TODO:
    return result({})

@app.route('/db/api/forum/listThreads/', methods=['GET'])
def forum_list_threads():
    # TODO:
    return result({})

@app.route('/db/api/forum/listUsers/', methods=['GET'])
def forum_list_users():
    # TODO:
    return result({})



### Thread
@app.route('/db/api/thread/close/', methods=['POST'])
def thread_close():
    # TODO:
    return result({})

@app.route('/db/api/thread/create/', methods=['POST'])
def thread_create():
    # TODO:
    return result({})

@app.route('/db/api/thread/details/', methods=['GET'])
def thread_details():
    # TODO:
    return result({})

@app.route('/db/api/thread/list/', methods=['GET'])
def thread_list():
    # TODO:
    return result({})

@app.route('/db/api/thread/listPosts/', methods=['GET'])
def thread_list_posts():
    # TODO:
    return result({})

@app.route('/db/api/thread/open/', methods=['POST'])
def thread_open():
    # TODO:
    return result({})

@app.route('/db/api/thread/remove/', methods=['POST'])
def thread_remove():
    # TODO:
    return result({})

@app.route('/db/api/thread/restore/', methods=['POST'])
def thread_restore():
    # TODO:
    return result({})

@app.route('/db/api/thread/subscribe/', methods=['POST'])
def thread_subscribe():
    # TODO:
    return result({})

@app.route('/db/api/thread/unsubscribe/', methods=['POST'])
def thread_unsubscribe():
    # TODO:
    return result({})

@app.route('/db/api/thread/update/', methods=['POST'])
def thread_update():
    # TODO:
    return result({})

@app.route('/db/api/thread/vote/', methods=['POST'])
def thread_vote():
    # TODO:
    return result({})



### Post
@app.route('/db/api/post/create/', methods=['POST'])
def post_create():
    # TODO:
    return result({})

@app.route('/db/api/post/details/', methods=['GET'])
def post_details():
    # TODO:
    return result({})

@app.route('/db/api/post/list/', methods=['GET'])
def post_list():
    # TODO:
    return result({})

@app.route('/db/api/post/remove/', methods=['POST'])
def post_remove():
    # TODO:
    return result({})

@app.route('/db/api/post/restore/', methods=['POST'])
def post_restore():
    # TODO:
    return result({})

@app.route('/db/api/post/update/', methods=['POST'])
def post_update():
    # TODO:
    return result({})

@app.route('/db/api/post/vote/', methods=['POST'])
def post_vote():
    # TODO:
    return result({})
