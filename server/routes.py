# -*- coding: utf-8 -*-
import MySQLdb
from _mysql_exceptions import IntegrityError
from werkzeug.exceptions import NotFound
from app import *
from helpers import *


@app.errorhandler(400)
def bad_request(error):
    return result_invalid(error.description)

@app.errorhandler(404)
def not_found(error):
    return result_not_found(error.response)

### Common
@app.route('/db/api/status/', methods=['GET'])
def status():
    db = get_db()
    cursor = db.cursor()

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
    udata = get_request_json()
    username = udata.get('username')
    about = udata.get('about')
    name = udata.get('name')
    email = udata.get('email')
    isAnonymous = udata.get('isAnonymous', False)

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""INSERT INTO
                    Users (username, about, name, email, isAnonymous)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (username, about, name, email, isAnonymous))
        db.commit()

        return result({
            'about': about,
            'email': email,
            'id': cursor.lastrowid,
            'isAnonymous': isAnonymous,
            'name': name,
            'username': username
            })
    except IntegrityError:
        return result_user_exists("User %s already exists" % email)

@app.route('/db/api/user/details/', methods=['GET'])
def user_details():
    email = get_request_arg('user')

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""SELECT id, username, about, name, email, isAnonymous
                    FROM Users
                    WHERE email = %s""",
                    (email, ))

    if cursor.rowcount == 0:
        return result_not_found("User %s doesn't exist" % email)

    res = {}
    udata = cursor.fetchone()
    for keyn, val in enumerate(udata):
        field = cursor.description[keyn][0]
        if field[0:2] == 'is':
            val = bool(val)
        res[field] = val

    cursor.execute("""SELECT follower
                    FROM Followers
                    WHERE followee = %s """,
                    (email, ))

    followers = cursor.fetchall()
    res['followers'] = [f[0] for f in followers]

    cursor.execute("""SELECT followee
                    FROM Followers
                    WHERE follower = %s """,
                    (email, ))

    following = cursor.fetchall()
    res['following'] = [f[0] for f in following]

    cursor.execute("""SELECT thread
                    FROM Subscriptions
                    WHERE user = %s """,
                    (email, ))
    threads = cursor.fetchall()
    res['subscriptions'] = [int(t[0]) for t in threads]

    return result(res)

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
