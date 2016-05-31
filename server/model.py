# -*- coding: utf-8 -*-
from app import *
import datetime

from model_helpers import model_method, model_dict

@model_method
def status(db, cursor):
    res = {}

    for entity in ['user', 'thread', 'forum', 'post']:
        cursor.execute('SELECT COUNT(*) FROM %ss' % entity.capitalize())
        data = cursor.fetchone()
        res[entity] = data[0]

    return res

@model_method
def clear(db, cursor):
    cursor.execute('SET FOREIGN_KEY_CHECKS=0')
    db.commit()
    for entity in ['follower', 'subscription', 'post', 'thread', 'forum', 'user']:
        cursor.execute('TRUNCATE %ss' % entity.capitalize())
        db.commit()

    cursor.execute('SET FOREIGN_KEY_CHECKS=1')
    db.commit()
    return True

@model_method
def user_create(db, cursor, fields):
    cursor.execute("""INSERT INTO
                Users (username, about, name, email, isAnonymous)
                VALUES (%s, %s, %s, %s, %s)""",
                (
                    fields.get('username'),
                    fields.get('about'),
                    fields.get('name'),
                    fields.get('email'),
                    fields.get('isAnonymous', False)
                    ))
    db.commit()

    return cursor.rowcount > 0

@model_method
def user_exists(db, cursor, email):
    cursor.execute("""SELECT 1
                    FROM Users
                    WHERE email = %s""",
                    (email, ))

    return cursor.rowcount > 0

@model_method
def user_data(db, cursor, email, follow_data=True, subscriptions=True):
    cursor.execute("""SELECT id, username, about, name, email, isAnonymous
                    FROM Users
                    WHERE email = %s""",
                    (email, ))

    if cursor.rowcount == 0:
        return None

    udata = cursor.fetchone()
    res = model_dict(udata, cursor.description)

    if follow_data:
        res['followers'] = user_list_followers(email)
        res['following'] = user_list_following(email)

    if subscriptions:
        cursor.execute("""SELECT thread
                        FROM Subscriptions
                        WHERE user = %s """,
                        (email, ))
        threads = cursor.fetchall()
        res['subscriptions'] = [int(t[0]) for t in threads]
    
    return res

def user_data_short(email):
    return user_data(email, follow_data=False, subscriptions=False)

@model_method
def users_data(db, cursor, emails, follow_data=True, subscriptions=True):
    cursor.execute("""SELECT id, username, about, name, email, isAnonymous
                    FROM Users
                    WHERE email IN (%s)"""
                    % sql_in(emails))

    res = {}
    udata = cursor.fetchone()

    while udata is not None:
        ures = model_dict(udata, cursor.description)
        res[ures['email']] = ures

        udata = cursor.fetchone()

    if not len(res):
        return res

    if follow_data:
        following = {}
        cursor.execute("""SELECT follower, GROUP_CONCAT(followee, ',')
                        FROM Followers
                        WHERE follower IN (%s)
                        GROUP BY follower"""
                        % sql_in(emails))

        follow_row = cursor.fetchone()
        while follow_row is not None:
            follower = follow_row[0]
            followees = follow_row[1]
            following[follower] = filter(None, followees.split(','))
            follow_row = cursor.fetchone()

        followers = {}
        cursor.execute("""SELECT followee, GROUP_CONCAT(follower, ',')
                        FROM Followers
                        WHERE followee IN (%s)
                        GROUP BY followee"""
                        % sql_in(emails))

        follow_row = cursor.fetchone()
        while follow_row is not None:
            followee = follow_row[0]
            ufollowers = follow_row[1]
            followers[followee] = filter(None, ufollowers.split(','))
            follow_row = cursor.fetchone()

    if subscriptions:
        threads = {}
        cursor.execute("""SELECT user, GROUP_CONCAT(thread, ',')
                        FROM Subscriptions
                        WHERE user IN (%s)
                        GROUP BY user"""
                        % sql_in(emails))

        thread_row = cursor.fetchone()

        while thread_row is not None:
            user = thread_row[0]
            uthreads = thread_row[1]
            threads[user] = map(int, filter(None, uthreads.split(',')))
            thread_row = cursor.fetchone()
    
    if follow_data or subscriptions:
        for key in res:
            if follow_data:
                res[key]['followers'] = followers.get(key, [])
                res[key]['following'] = following.get(key, [])
            if subscriptions:
                res[key]['subscriptions'] = threads.get(key, [])

    return res

@model_method
def user_follow(db, cursor, follower, followee):
    cursor.execute("""INSERT INTO
                Followers (followee, follower)
                VALUES (%s, %s)""",
                (
                    followee,
                    follower
                    ))
    db.commit()
    return cursor.rowcount > 0

@model_method
def user_unfollow(db, cursor, follower, followee):
    cursor.execute("""DELETE
                FROM Followers 
                WHERE followee = %s AND follower = %s""",
                (
                    followee,
                    follower
                    ))
    db.commit()

    return cursor.rowcount > 0

@model_method
def user_follows(db, cursor, follower, followee):
    cursor.execute(""" SELECT 1
                    FROM Followers
                    WHERE follower = %s AND followee = %s """,
                    (follower, followee))

    return cursor.rowcount > 0

@model_method
def user_subscribed(db, cursor, email, thread):
    cursor.execute(""" SELECT 1
                    FROM Subscriptions
                    WHERE user = %s AND thread = %s """,
                    (email, thread))

    return cursor.rowcount > 0

@model_method
def user_list_followers(db, cursor, email, limit=0, order='desc', since_id=None, full=False):
    q = """SELECT f.follower
            FROM Followers f
            INNER JOIN Users u ON u.email = f.follower
            WHERE f.followee = %s """
    qargs = [email]

    if since_id is not None:
        q += " AND u.id >= %s "
        qargs.append(since_id)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " ORDER BY u.name " + order

    if limit:
        q += " LIMIT " + str(limit)

    cursor.execute(q, tuple(qargs))

    emails = [f[0] for f in cursor.fetchall()]

    if not full:
        return emails

    res = []
    if len(emails):
        users = users_data(emails)
        for email in emails:
            res.append(users.get(email))

    return res

@model_method
def user_list_following(db, cursor, email, limit=0, order='desc', since_id=None, full=False):
    q = """SELECT f.followee
            FROM Followers f
            INNER JOIN Users u ON u.email = f.follower
            WHERE f.follower = %s """
    qargs = [email]

    if since_id is not None:
        q += " AND u.id >= %s "
        qargs.append(since_id)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " ORDER BY u.name " + order

    if limit:
        q += " LIMIT " + str(limit)

    cursor.execute(q, tuple(qargs))

    emails = [f[0] for f in cursor.fetchall()]

    if not full:
        return emails

    res = []
    if len(emails):
        users = users_data(emails)
        for email in emails:
            res.append(users.get(email))

    return res

@model_method
def user_update(db, cursor, email, fields):
    cursor.execute("""UPDATE Users 
                    SET about = %s, name = %s
                    WHERE email = %s """,
                (
                    fields.get('about'),
                    fields.get('name'),
                    email
                    ))
    cursor.execute("""UPDATE Posts
                    SET user_name = %s
                    WHERE user = %s """,
                (
                    fields.get('name'),
                    email
                    ))
    db.commit()

    return True

def user_posts(email, limit=0, order='desc', since_date=None, related=[]):
    return posts_list({ 'user' : email }, limit, order, since_date, related)

def user_threads(email, limit=0, order='desc', since_date=None, related=[]):
    return threads_list({ 'user' : email }, limit, order, since_date, related)

@model_method
def forum_create(db, cursor, fields):
    cursor.execute("""INSERT INTO
                Forums (name, short_name, user)
                VALUES (%s, %s, %s)""",
                (
                    fields.get('name'),
                    fields.get('short_name'),
                    fields.get('user')
                    ))
    db.commit()

    return cursor.rowcount > 0

@model_method
def forum_data(db, cursor, forum, related=[]):
    cursor.execute("""SELECT id, name, short_name, user
                    FROM Forums
                    WHERE short_name = %s""",
                    (forum, ))

    if cursor.rowcount == 0:
        return None

    fdata = cursor.fetchone()
    res = model_dict(fdata, cursor.description)

    if 'user' in related:
        res['user'] = user_data(res['user'])

    return res

@model_method
def forums_data(db, cursor, forums):
    cursor.execute("""SELECT id, name, short_name, user
                    FROM Forums
                    WHERE short_name IN (%s)"""
                    % sql_in(forums))

    res = {}
    fdata = cursor.fetchone()

    while fdata is not None:
        fres = model_dict(fdata, cursor.description)
        res[fres['short_name']] = fres

        fdata = cursor.fetchone()

    return res

@model_method
def forum_exists(db, cursor, forum):
    cursor.execute("""SELECT 1
                    FROM Forums
                    WHERE short_name = %s""",
                    (forum, ))

    return cursor.rowcount > 0

def forum_posts(forum, limit=0, order='desc', since_date=None, related=[]):
    return posts_list({ 'forum' : forum }, limit, order, since_date, related)

def forum_threads(forum, limit=0, order='desc', since_date=None, related=[]):
    return threads_list({ 'forum' : forum }, limit, order, since_date, related)

@model_method
def forum_users(db, cursor, forum, limit=0, order='desc', since_id=None, full=False):
    q = """SELECT DISTINCT p.user
            FROM Posts p
            INNER JOIN Users u ON u.email = p.user
            WHERE p.forum = %s """
    qargs = [forum]

    if since_id is None:
        since_id = 0

    q += " AND u.id >= %s "
    qargs.append(since_id)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " ORDER BY p.user_name " + order

    if limit:
        q += " LIMIT " + str(limit)

    cursor.execute(q, tuple(qargs))

    emails = [f[0] for f in cursor.fetchall()]

    if not full:
        return emails

    res = []
    if emails:
        users = users_data(emails)
        for email in emails:
            res.append(users.get(email))

    return res

@model_method
def thread_create(db, cursor, fields):
    cursor.execute("""INSERT INTO
                Threads (title, slug, message, date, isClosed, isDeleted, forum, user)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    fields.get('title'),
                    fields.get('slug'),
                    fields.get('message'),
                    fields.get('date'),
                    fields.get('isClosed', False),
                    fields.get('isDeleted', False),
                    fields.get('forum'),
                    fields.get('user')
                    ))
    db.commit()

    return cursor.lastrowid

@model_method
def thread_data(db, cursor, thread, related=[], counters=True):
    cursor.execute("""SELECT id, title, slug, message, date, likes, dislikes, (likes - dislikes) AS points, isClosed, isDeleted, posts, forum, user
                    FROM Threads
                    WHERE id = %s""",
                    (thread, ))

    if cursor.rowcount == 0:
        return None

    tdata = cursor.fetchone()
    remove = []
    if not counters:
        remove = ['likes', 'dislikes', 'points']
    res = model_dict(tdata, cursor.description, remove=remove)

    if 'user' in related:
        res['user'] = user_data(res['user'])

    if 'forum' in related:
        res['forum'] = forum_data(res['forum'])

    return res

@model_method
def threads_data(db, cursor, threads):
    cursor.execute("""SELECT id, title, slug, message, date, likes, dislikes, (likes - dislikes) AS points, isClosed, isDeleted, posts, forum, user
                    FROM Threads
                    WHERE id IN (%s)"""
                    % sql_in(threads))

    res = {}
    tdata = cursor.fetchone()

    while tdata is not None:
        tres = model_dict(tdata, cursor.description)
        res[tres['id']] = tres

        tdata = cursor.fetchone()

    return res

@model_method
def threads_list(db, cursor, search_fields, limit=0, order='desc', since_date=None, related=[]):
    q = """SELECT *, (likes - dislikes) AS points
            FROM Threads
            WHERE 1=1 """
    qargs = []

    for k in search_fields:
        q += "AND %s = " % k
        q += " %s "
        qargs.append(search_fields.get(k))

    if since_date is not None:
        q += " AND `date` >= %s "
        qargs.append(since_date)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " ORDER BY `date` " + order

    if limit:
        q += " LIMIT " + str(limit)

    cursor.execute(q, tuple(qargs))

    res = []
    row = cursor.fetchone()

    forums = []
    users = []

    while row is not None:
        rowres = model_dict(row, cursor.description)

        if 'forum' in related:
            forums.append(rowres['forum'])
        if 'user' in related:
            users.append(rowres['user'])
        res.append(rowres)
        row = cursor.fetchone()

    if 'forum' in related and forums:
        forums = forums_data(forums)
        for keyn, val in enumerate(res):
            res[keyn]['forum'] = forums.get(val['forum'])

    if 'user' in related and users:
        users = users_data(users)
        for keyn, val in enumerate(res):
            res[keyn]['user'] = users.get(val['user'])

    return res

def thread_posts(thread, limit=0, order='desc', since_date=None, related=[], sort='flat'):
    return posts_list({ 'thread' : thread }, limit, order, since_date, related, sort)

@model_method
def thread_exists(db, cursor, thread):
    cursor.execute("""SELECT 1
                    FROM Threads
                    WHERE id = %s""",
                    (thread, ))

    return cursor.rowcount > 0

@model_method
def thread_subscribe(db, cursor, user, thread):
    cursor.execute("""INSERT INTO
                Subscriptions (thread, user)
                VALUES (%s, %s)""",
                (
                    thread,
                    user
                    ))
    db.commit()
    return cursor.rowcount > 0

@model_method
def thread_unsubscribe(db, cursor, user, thread):
    cursor.execute("""DELETE
                FROM Subscriptions 
                WHERE thread = %s AND user = %s""",
                (
                    thread,
                    user
                    ))
    db.commit()

    return cursor.rowcount > 0

@model_method
def post_create(db, cursor, fields):
    sorter = sorter_date = str(fields.get('thread'))

    if fields.get('parent') is not None:
        parent_data = post_data(fields.get('parent'))
        sorter = parent_data.get('sorter')
        sorter_date = parent_data.get('sorter_date')

    cursor.execute("""INSERT INTO
                Posts (message, date, isApproved, isHighlighted, isEdited, isSpam, isDeleted, parent, user, user_name, thread, forum)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, (SELECT name FROM Users WHERE email = %s),  %s, %s)""",
                (
                    fields.get('message'),
                    fields.get('date'),
                    fields.get('isApproved', False),
                    fields.get('isHighlighted', False),
                    fields.get('isEdited', False),
                    fields.get('isSpam', False),
                    fields.get('isDeleted', False),
                    fields.get('parent', None),
                    fields.get('user'),
                    fields.get('user'),
                    fields.get('thread'),
                    fields.get('forum')
                    ))

    id = cursor.lastrowid

    sorter_date_part = fields.get('date').replace('-', '').replace(':', '').replace(' ', '')[2:]
    cursor.execute("""UPDATE Posts
                        SET sorter = %s,
                        sorter_date = %s
                        WHERE id = %s""",
                        (
                            str(sorter) + "." + str(id),
                            str(sorter_date) + "-" + sorter_date_part + "-" + str(id),
                            id,
                        ))

    cursor.execute("""UPDATE Threads
                        SET posts = posts + 1
                        WHERE id = %s""",
                        (
                            fields.get('thread'),
                        ))

    db.commit()

    return id

@model_method
def thread_set_closed(db, cursor, thread, closed=True):
    cursor.execute("""UPDATE Threads
                    SET isClosed = %s
                    WHERE id = %s """,
                    (closed, thread,))
    db.commit()

    return True

def thread_close(thread):
    return thread_set_closed(thread, True)

def thread_open(thread):
    return thread_set_closed(thread, False)

@model_method
def thread_set_deleted(db, cursor, thread, deleted=True):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""UPDATE Threads
                    SET isDeleted = %s
                    WHERE id = %s """,
                    (deleted, thread,))

    cursor.execute("""UPDATE Posts
                    SET isDeleted = %s
                    WHERE thread = %s""",
                    (-int(deleted), thread, ))
    cursor.execute("""UPDATE Threads
                    SET posts = (SELECT COUNT(*) FROM Posts WHERE thread = %s AND isDeleted = 0)
                    WHERE id = %s """,
                    (thread, thread,))

    db.commit()

    return True

def thread_remove(thread):
    return thread_set_deleted(thread, True)

def thread_restore(thread):
    return thread_set_deleted(thread, False)

@model_method
def thread_vote(db, cursor, thread, like=True):
    field = 'likes'
    if not like:
        field = 'dis' + field

    cursor.execute("""UPDATE Threads
                    SET %s = %s + 1
                    WHERE id = %s """ % (field, field, '%s'),
                    (
                        thread,
                        ))
    db.commit()

    return True

@model_method
def thread_update(db, cursor, thread, fields):
    cursor.execute("""UPDATE Threads
                    SET message = %s,
                    slug = %s
                    WHERE id = %s """,
                    (
                        fields.get('message'),
                        fields.get('slug'),
                        thread,
                        ))
    db.commit()

    return True

@model_method
def post_data(db, cursor, post, related=[], counters=True):
    cursor.execute("""SELECT id, message, date, likes, dislikes, (likes - dislikes) AS points, isApproved, isHighlighted, isEdited, isSpam, isDeleted, parent, user, thread, forum, sorter, sorter_date
                    FROM Posts
                    WHERE id = %s""",
                    (post, ))

    if cursor.rowcount == 0:
        return None

    pdata = cursor.fetchone()
    remove = []
    if not counters:
        remove = ['likes', 'dislikes', 'points']
    res = model_dict(pdata, cursor.description, remove=remove)

    if 'user' in related:
        res['user'] = user_data(res['user'])

    if 'forum' in related:
        res['forum'] = forum_data(res['forum'])

    if 'thread' in related:
        res['thread'] = thread_data(res['thread'])

    return res

@model_method
def posts_list(db, cursor, search_fields, limit=0, order='desc', since_date=None, related=[], sort='flat'):
    if sort == 'tree':
        return posts_list_tree(search_fields, limit, order, since_date, related)
    if sort == 'parent_tree':
        return posts_list_parent_tree(search_fields, limit, order, since_date, related)

    q = """SELECT *, (likes - dislikes) AS points
            FROM Posts
            WHERE 1=1 """
    qargs = []

    for k in search_fields:
        q += "AND %s = " % k
        q += " %s "
        qargs.append(search_fields.get(k))

    if since_date is not None:
        q += " AND `date` >= %s "
        qargs.append(since_date)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " ORDER BY `date` " + order

    if limit:
        q += " LIMIT " + str(limit)

    cursor.execute(q, tuple(qargs))

    res = []
    row = cursor.fetchone()

    forums = []
    threads = []
    users = []

    while row is not None:
        rowres = model_dict(row, cursor.description)

        if 'forum' in related:
            forums.append(rowres['forum'])
        if 'thread' in related:
            threads.append(rowres['thread'])
        if 'user' in related:
            users.append(rowres['user'])
        res.append(rowres)
        row = cursor.fetchone()

    if 'forum' in related and forums:
        forums = forums_data(forums)
        for keyn, val in enumerate(res):
            res[keyn]['forum'] = forums.get(val['forum'])

    if 'thread' in related and threads:
        threads = threads_data(threads)
        for keyn, val in enumerate(res):
            res[keyn]['thread'] = threads.get(val['thread'])

    if 'user' in related and users:
        users = users_data(users)
        for keyn, val in enumerate(res):
            res[keyn]['user'] = users.get(val['user'])

    return res

def posts_list_tree(search_fields, limit=0, order='desc', since_date=None, related=[]):
    res = posts_list_parent_tree(search_fields, limit, order, since_date, related, True)

    return res

@model_method
def posts_list_parent_tree(db, cursor, search_fields, limit=0, order='desc', since_date=None, related=[], limit_total=False):
    db = get_db()
    cursor = db.cursor()

    q = """SELECT p.*, (p.likes - p.dislikes) AS points
            FROM Posts p
            WHERE 1=1 """
    qargs = []

    for k in search_fields:
        q += "AND p.%s = " % k
        q += " %s "
        qargs.append(search_fields.get(k))

    if since_date is not None:
        q += " AND p.`date` >= %s "
        qargs.append(since_date)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " AND (LENGTH(sorter) - LENGTH(REPLACE(sorter, '.', ''))) = 1"
    q += " ORDER BY sorter_date " + order

    if limit:
        q += " LIMIT " + str(limit)

    cursor.execute(q, tuple(qargs))

    res = []
    ids = []
    row = cursor.fetchone()

    while row is not None:
        rowres = model_dict(row, cursor.description)

        ids.append(rowres['sorter'])
        res.append(rowres)
        row = cursor.fetchone()

    if not ids:
        return res

    ids = ' OR '.join(["sorter LIKE '" + id  + ".%'" for id in ids])
    cursor.execute("""SELECT *, (likes - dislikes) AS points
                FROM Posts
                WHERE 0=1 OR %s""" % ids)

    childs = {}

    row = cursor.fetchone()

    while row is not None:
        rowres = model_dict(row, cursor.description)

        row = cursor.fetchone()
        if childs.has_key(rowres['parent']):
            childs.get(rowres['parent']).append(rowres)
        else:
            childs[rowres['parent']] = [rowres]

    def find_childs(cur):
        if childs.has_key(cur.get('id')):
            for keyn, val in enumerate(childs[cur.get('id')]):
                child_childs = find_childs(val)
                if child_childs:
                    val['childs'] = child_childs
            return childs[cur.get('id')]
        return []

    for keyn, val in enumerate(res):
        cur_childs = find_childs(val)

        if cur_childs:
            val['childs'] = cur_childs

    def _flatten_tree(tree, arr, order, reverse_childs=False):
        get_datetime = lambda obj: datetime.datetime.strptime(obj.get('date'), '%Y-%m-%d %H:%M:%S')
        order = True if order in['desc', True] else False
        for node in tree:
            arr.append(node)
            _childs = node.get('childs', [])
            _childs.sort(key=get_datetime, reverse=reverse_childs)
            _flatten_tree(_childs, arr, order, reverse_childs)
            if node.has_key('childs'):
                del node['childs']
        return arr

    res = _flatten_tree(res, [], order, False)

    if limit_total and limit:
        return res[:int(limit)]

    return res

@model_method
def post_exists(db, cursor, post):
    cursor.execute("""SELECT 1
                    FROM Posts
                    WHERE id = %s""",
                    (post, ))

    return cursor.rowcount > 0

@model_method
def post_set_deleted(db, cursor, post, deleted=True):
    cursor.execute("""UPDATE Posts
                    SET isDeleted = %s
                    WHERE id = %s """,
                    (deleted, post,))

    pdata = post_data(post)

    sign = '-'
    if not deleted:
        sign = '+'

    cursor.execute("""UPDATE Threads
                        SET posts = posts %s 1
                        WHERE id = %s""" % (sign, '%s'),
                        (
                            pdata.get('thread'),
                        ))
    db.commit()

    return True

def post_remove(post):
    return post_set_deleted(post, True)

def post_restore(post):
    return post_set_deleted(post, False)

@model_method
def post_update(db, cursor, post, fields):
    cursor.execute("""UPDATE Posts
                    SET message = %s
                    WHERE id = %s """,
                    (
                        fields.get('message'),
                        post,
                        ))
    db.commit()

    return True

@model_method
def post_vote(db, cursor, post, like=True):
    field = 'likes'
    if not like:
        field = 'dis' + field

    cursor.execute("""UPDATE Posts
                    SET %s = %s + 1
                    WHERE id = %s """ % (field, field, '%s'),
                    (
                        post,
                        ))
    db.commit()

    return True
