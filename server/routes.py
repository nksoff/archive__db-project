# -*- coding: utf-8 -*-
import MySQLdb
from app import *
from helpers import *
import model

@app.errorhandler(400)
def bad_request(error):
    return result_invalid(error.description)

@app.errorhandler(404)
def not_found(error):
    return result_not_found(error.description)

### Common
@app.route('/db/api/status/', methods=['GET'])
def status():
    response = model.status()
    return result(response)

@app.route('/db/api/clear/', methods=['POST'])
def clear():
    res = model.clear()

    if res:
        return result("OK")
    else:
        return result_unknown("Couldn't clear data")


### User
@app.route('/db/api/user/create/', methods=['POST'])
def user_create():
    udata = get_request_json()

    res = model.user_create(udata)

    if res:
        udata = model.user_data_short(udata.get('email'))
        return result(udata)
    else:
        return result_user_exists("User %s already exists" % udata.get('email'))

@app.route('/db/api/user/details/', methods=['GET'])
def user_details():
    email = get_request_arg('user')

    res = model.user_data(email)
    if res is None:
        return result_not_found("User %s doesn't exist" % email)

    return result(res)

@app.route('/db/api/user/follow/', methods=['POST'])
def user_follow():
    data = get_request_json()

    follower = data.get('follower')
    followee = data.get('followee')

    if not model.user_exists(follower):
        return result_not_found("User %s doesn't exist" % follower)

    if follower == followee:
        return result_invalid_semantic("User %s cannot follow himself" % follower)

    if not model.user_exists(followee):
        return result_not_found("User %s doesn't exist" % followee)

    if not model.user_follows(follower, followee):
        res = model.user_follow(follower, followee)

        if res:
            udata = model.user_data(follower)
            return result(udata)
        else:
            return result_unknown("Couldn't follow %s by %s" % (followee, follower))
    else:
        return result_unknown("User %s already follows %s" % (follower, followee))

@app.route('/db/api/user/listFollowers/', methods=['GET'])
def user_list_followers():
    email = get_request_arg('user')
    limit = get_request_arg('limit', 0)
    since_id = get_request_arg('since_id')
    order = get_request_arg('order', 'desc')

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    if not model.user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    res = model.user_list_followers(email, limit=limit, order=order, since_id=since_id, full=True)
    return result(res)

@app.route('/db/api/user/listFollowing/', methods=['GET'])
def user_list_following():
    email = get_request_arg('user')
    limit = get_request_arg('limit', 0)
    since_id = get_request_arg('since_id')
    order = get_request_arg('order', 'desc')

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    if not model.user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    res = model.user_list_following(email, limit=limit, order=order, since_id=since_id, full=True)
    return result(res)

@app.route('/db/api/user/listPosts/', methods=['GET'])
def user_list_posts():
    email = get_request_arg('user')
    limit = get_request_arg('limit', 0)
    since_date = get_request_arg('since')
    order = get_request_arg('order', 'desc')

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order: %s" % order)

    if not model.user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    posts = model.user_posts(email, limit=limit, order=order, since_date=since_date)
    return result(posts)

@app.route('/db/api/user/unfollow/', methods=['POST'])
def user_unfollow():
    data = get_request_json()

    follower = data.get('follower')
    followee = data.get('followee')

    if not model.user_exists(follower):
        return result_not_found("User %s doesn't exist" % follower)

    if not model.user_exists(followee):
        return result_not_found("User %s doesn't exist" % followee)

    if model.user_follows(follower, followee):
        res = model.user_unfollow(follower, followee)

        if res:
            udata = model.user_data(follower)
            return result(udata)
        else:
            return result_unknown("Couldn't unfollow %s by %s" % (followee, follower))
    else:
        return result_unknown("User %s doesn't follow %s" % (follower, followee))

@app.route('/db/api/user/updateProfile/', methods=['POST'])
def user_update_profile():
    data = get_request_json()

    email = data.get('user')
    name = data.get('name')
    about = data.get('about')

    if not model.user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    res = model.user_update(email, data)

    if res:
        udata = model.user_data(email)
        return result(udata)
    else:
        return result_unknown("Couldn't update user profile for %s" % (email))



### Forum
@app.route('/db/api/forum/create/', methods=['POST'])
def forum_create():
    fdata = get_request_json()

    email = fdata.get('user')

    if not model.user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    forum = fdata.get('short_name')
    res = model.forum_create(fdata)
    fdata = model.forum_data(forum)

    if fdata:
        return result(fdata)
    else:
        return result_not_found("Couldn't create forum %s" % forum)

@app.route('/db/api/forum/details/', methods=['GET'])
def forum_details():
    forum = get_request_arg('forum')
    related = get_request_args('related')

    if not check_enum(related, ['user']):
        return result_invalid_semantic("Wrong value for related")

    fdata = model.forum_data(forum, related=related)
    if fdata:
        return result(fdata)
    else:
        return result_not_found("Forum %s doesn't exist" % forum)

@app.route('/db/api/forum/listPosts/', methods=['GET'])
def forum_list_posts():
    forum = get_request_arg('forum')
    if not model.forum_exists(forum):
        return result_not_found("Forum %s doesn't exist" % forum)

    limit = get_request_arg('limit', 0)
    since_date = get_request_arg('since')
    order = get_request_arg('order', 'desc')
    related = get_request_args('related')

    if not check_enum(related, ['user', 'forum', 'thread']):
        return result_invalid_semantic("Wrong value for related")

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    posts = model.forum_posts(forum, limit=limit, order=order, since_date=since_date, related=related)
    return result(posts)

@app.route('/db/api/forum/listThreads/', methods=['GET'])
def forum_list_threads():
    forum = get_request_arg('forum')
    if not model.forum_exists(forum):
        return result_not_found("Forum %s doesn't exist" % forum)

    limit = get_request_arg('limit', 0)
    since_date = get_request_arg('since')
    order = get_request_arg('order', 'desc')
    related = get_request_args('related')

    if not check_enum(related, ['user', 'forum']):
        return result_invalid_semantic("Wrong value for related")

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    threads = model.forum_threads(forum, limit=limit, order=order, since_date=since_date, related=related)
    return result(threads)

@app.route('/db/api/forum/listUsers/', methods=['GET'])
def forum_list_users():
    forum = get_request_arg('forum')
    if not model.forum_exists(forum):
        return result_not_found("Forum %s doesn't exist" % forum)

    limit = get_request_arg('limit', 0)
    since_id = get_request_arg('since_id')
    order = get_request_arg('order', 'desc')

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    users = model.forum_users(forum, limit=limit, order=order, since_id=since_id, full=True)
    return result(users)



### Thread
@app.route('/db/api/thread/close/', methods=['POST'])
def thread_close():
    # TODO:
    return result({})

@app.route('/db/api/thread/create/', methods=['POST'])
def thread_create():
    tdata = get_request_json()

    email = tdata.get('user')

    if not model.user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    forum = tdata.get('forum')

    if not model.forum_exists(forum):
        return result_not_found("Forum %s doesn't exist" % forum)

    thread_id = model.thread_create(tdata)
    tdata = model.thread_data(thread_id, counters=False)

    if tdata:
        return result(tdata)
    else:
        return result_not_found("Couldn't create thread %s" % tdata.get('title'))

@app.route('/db/api/thread/details/', methods=['GET'])
def thread_details():
    thread = get_request_arg('thread')
    related = get_request_args('related')

    if not check_enum(related, ['user', 'forum']):
        return result_invalid_semantic("Wrong value for related")

    tdata = model.thread_data(thread, related=related)
    if tdata:
        return result(tdata)
    else:
        return result_not_found("Thread %s doesn't exist" % thread)

@app.route('/db/api/thread/list/', methods=['GET'])
def thread_list():
    limit = get_request_arg('limit', 0)
    since_date = get_request_arg('since')
    order = get_request_arg('order', 'desc')

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    forum = get_request_arg('forum')
    if forum is not None:
        if not model.forum_exists(forum):
            return result_not_found("Forum %s doesn't exist" % forum)

        threads = model.forum_threads(forum, limit=limit, order=order, since_date=since_date)
        return result(threads)

    email = get_request_arg('user')
    if email is not None:
        if not model.user_exists(email):
            return result_not_found("User %s doesn't exist" % email)

        threads = model.user_threads(email, limit=limit, order=order, since_date=since_date)
        return result(threads)

    return result_invalid_semantic("User and forum are not set")


@app.route('/db/api/thread/listPosts/', methods=['GET'])
def thread_list_posts():
    thread = get_request_arg('thread')
    if not model.thread_exists(thread):
        return result_not_found("Thread %s doesn't exist" % thread)

    limit = get_request_arg('limit', 0)
    since_date = get_request_arg('since')
    order = get_request_arg('order', 'desc')
    sort = get_request_arg('sort', 'flat')

    # TODO: sorts!!!
    if not check_arg(sort, ['flat', 'tree', 'parent_tree']):
        return result_invalid_semantic("Wrong value for sort")

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    posts = model.thread_posts(thread, limit=limit, order=order, since_date=since_date)
    return result(posts)

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
    pdata = get_request_json()

    email = pdata.get('user')

    if not model.user_exists(email):
        return result_not_found("User %s doesn't exist" % email)

    forum = pdata.get('forum')

    if not model.forum_exists(forum):
        return result_not_found("Forum %s doesn't exist" % forum)

    thread = pdata.get('thread')

    if not model.thread_exists(thread):
        return result_not_found("Thread %s doesn't exist" % thread)

    post_id = model.post_create(pdata)
    pdata = model.post_data(post_id, counters=False)

    if pdata:
        return result(pdata)
    else:
        return result_not_found("Couldn't create post") 

@app.route('/db/api/post/details/', methods=['GET'])
def post_details():
    post = get_request_arg('post')
    related = get_request_args('related')

    if not check_enum(related, ['user', 'forum', 'thread']):
        return result_invalid_semantic("Wrong value for related")

    pdata = model.post_data(post, related=related)
    if pdata:
        return result(pdata)
    else:
        return result_not_found("Post %s doesn't exist" % post)

@app.route('/db/api/post/list/', methods=['GET'])
def post_list():
    # TODO:
    return result({})
    limit = get_request_arg('limit', 0)
    since_date = get_request_arg('since')
    order = get_request_arg('order', 'desc')

    if not check_arg(order, ['desc', 'asc']):
        return result_invalid_semantic("Wrong value for order")

    forum = get_request_arg('forum')
    if forum is not None:
        if not model.forum_exists(forum):
            return result_not_found("Forum %s doesn't exist" % forum)

        threads = model.forum_threads(forum, limit=limit, order=order, since_date=since_date)
        return result(threads)

    thread = get_request_arg('thread')
    if thread is not None:
        if not model.thread_exists(thread):
            return result_not_found("Thread %s doesn't exist" % thread)

        posts = model.threads_posts(thread, limit=limit, order=order, since_date=since_date)
        return result(posts)

    return result_invalid_semantic("Thread and forum are not set")

@app.route('/db/api/post/remove/', methods=['POST'])
def post_remove():
    pdata = get_request_json()
    post = pdata.get('post')

    if not model.post_exists(post):
        return result_not_found("Post %s doesn't exist" % post)

    res = model.post_remove(post)
    return result({ 'post': post })

@app.route('/db/api/post/restore/', methods=['POST'])
def post_restore():
    pdata = get_request_json()
    post = pdata.get('post')

    if not model.post_exists(post):
        return result_not_found("Post %s doesn't exist" % post)

    res = model.post_restore(post)
    return result({ 'post': post })

@app.route('/db/api/post/update/', methods=['POST'])
def post_update():
    # TODO:
    return result({})

@app.route('/db/api/post/vote/', methods=['POST'])
def post_vote():
    # TODO:
    return result({})
