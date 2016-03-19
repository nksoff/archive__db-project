# -*- coding: utf-8 -*-
from _mysql_exceptions import IntegrityError
from app import *
from helpers import date_normal

def status():
    db = get_db()
    cursor = db.cursor()

    res = {}

    for entity in ['user', 'thread', 'forum', 'post']:
        cursor.execute('SELECT COUNT(*) FROM %ss' % entity.capitalize())
        data = cursor.fetchone()
        res[entity] = data[0]

    return res

def clear():
    db = get_db()
    cursor = db.cursor()

    for entity in ['follower', 'subscription', 'post', 'thread', 'forum', 'user']:
        cursor.execute('TRUNCATE %ss' % entity.capitalize())

    db.commit()
    return True

def user_create(fields):
    db = get_db()
    cursor = db.cursor()

    try:
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
    except IntegrityError:
        return False

def user_exists(email):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""SELECT 1
                    FROM Users
                    WHERE email = %s""",
                    (email, ))

    return cursor.rowcount > 0

def user_data(email, follow_data=True, subscriptions=True):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""SELECT id, username, about, name, email, isAnonymous
                    FROM Users
                    WHERE email = %s""",
                    (email, ))

    if cursor.rowcount == 0:
        return None

    res = {}
    udata = cursor.fetchone()
    for keyn, val in enumerate(udata):
        field = cursor.description[keyn][0]
        if field[0:2] == 'is':
            val = bool(val)
        res[field] = val

    if follow_data:
        res['followers'] = user_followers(email)
        res['following'] = user_following(email)

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

def users_data(emails, follow_data=True, subscriptions=True):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""SELECT id, username, about, name, email, isAnonymous
                    FROM Users
                    WHERE email IN (%s)"""
                    % sql_in(emails))

    if cursor.rowcount == 0:
        return []

    res = {}
    udata = cursor.fetchone()

    while udata is not None:
        ures = {}
        for keyn, val in enumerate(udata):
            field = cursor.description[keyn][0]
            if field[0:2] == 'is':
                val = bool(val)
            ures[field] = val
        res[ures['email']] = ures

        udata = cursor.fetchone()

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

    res_final = []
    for email in emails:
        if res.has_key(email):
            res_final.append(res.get(email))

    return res_final

def user_follow(follower, followee):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""INSERT INTO
                    Followers (followee, follower)
                    VALUES (%s, %s)""",
                    (
                        followee,
                        follower
                        ))
        db.commit()
        return cursor.rowcount > 0
    except IntegrityError:
        return False

def user_unfollow(follower, followee):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""DELETE
                FROM Followers 
                WHERE followee = %s AND follower = %s""",
                (
                    followee,
                    follower
                    ))
    db.commit()

    return cursor.rowcount > 0

def user_follows(follower, followee):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(""" SELECT 1
                    FROM Followers
                    WHERE follower = %s AND followee = %s """,
                    (follower, followee))

    return cursor.rowcount > 0

def user_followers(email, limit=0, order='desc', since_id=None):
    db = get_db()
    cursor = db.cursor()

    q = """SELECT f.follower
            FROM Followers f
            INNER JOIN Users u ON u.email = f.follower
            WHERE f.followee = %s """
    qargs = (email, )

    if since_id is not None:
        q += " AND u.id > %d "
        qargs = (email, since_id)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " ORDER BY u.name " + order

    if limit:
        q += " LIMIT " + str(limit)

    cursor.execute(q, qargs)

    return [f[0] for f in cursor.fetchall()]

def user_following(email, limit=0, order='desc', since_id=None):
    db = get_db()
    cursor = db.cursor()

    q = """SELECT f.followee
            FROM Followers f
            INNER JOIN Users u ON u.email = f.follower
            WHERE f.follower = %s """
    qargs = (email, )

    if since_id is not None:
        q += " AND u.id > %d "
        qargs = (email, since_id)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " ORDER BY u.name " + order

    if limit:
        q += " LIMIT " + str(limit)

    cursor.execute(q, qargs)

    return [f[0] for f in cursor.fetchall()]

def user_update(email, fields):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""UPDATE Users 
                    SET about = %s, name = %s
                    WHERE email = %s """,
                (
                    fields.get('about'),
                    fields.get('name'),
                    email
                    ))
    db.commit()

    return True

def user_posts(email, limit=0, order='desc', since_date=None):
    return posts_data({ 'user' : email }, limit, order, since_date)

def posts_data(search_fields, limit=0, order='desc', since_date=None):
    db = get_db()
    cursor = db.cursor()

    q = """SELECT *
            FROM Posts
            WHERE 1=1 """
    qargs = []

    for k in search_fields:
        q += "AND %s = " % k
        q += " %s "
        qargs.append(search_fields.get(k))

    if since_date is not None:
        q += " AND `date` > %s "
        qargs.append(since_date)

    if order not in ['desc', 'asc']:
        order = 'desc'

    q += " ORDER BY `date` " + order

    if limit:
        q += " LIMIT " + str(limit)

    cursor.execute(q, tuple(qargs))

    res = []
    row = cursor.fetchone()

    while row is not None:
        rowres = {}
        for keyn, val in enumerate(row):
            field = cursor.description[keyn][0]
            if field == 'date':
                val = date_normal(val)
            if field[0:2] == 'is':
                val = bool(val)
            rowres[field] = val
        res.append(rowres)
        row = cursor.fetchone()

    return res

def forum_create(fields):
    db = get_db()
    cursor = db.cursor()

    try:
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
    except IntegrityError:
        return False

def forum_data(forum, related=[]):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""SELECT id, name, short_name, user
                    FROM Forums
                    WHERE short_name = %s""",
                    (forum, ))

    if cursor.rowcount == 0:
        return None

    res = {}
    fdata = cursor.fetchone()
    for keyn, val in enumerate(fdata):
        field = cursor.description[keyn][0]
        res[field] = val

    if 'user' in related:
        res['user'] = user_data(res['user'])

    return res

def forums_data(forums):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""SELECT id, name, short_name, user
                    FROM Forums
                    WHERE short_name IN (%s)"""
                    % sql_in(forums))

    if cursor.rowcount == 0:
        return []

    res = {}
    fdata = cursor.fetchone()

    while fdata is not None:
        fres = {}
        for keyn, val in enumerate(fdata):
            field = cursor.description[keyn][0]
            fres[field] = val
        res[fres['short_name']] = ures

        fdata = cursor.fetchone()

    return fdata.values()

def forum_exists(forum):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""SELECT 1
                    FROM Forums
                    WHERE short_name = %s""",
                    (forum, ))

    return cursor.rowcount > 0

def forum_posts(forum, limit=0, order='desc', since_date=None):
    return posts_data({ 'forum' : forum }, limit, order, since_date)

def thread_create(fields):
    db = get_db()
    cursor = db.cursor()

    try:
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
    except IntegrityError:
        return False

def thread_data(thread, related=[], counters=True):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""SELECT id, title, slug, message, date, likes, dislikes, points, isClosed, isDeleted, posts, forum, user
                    FROM Threads
                    WHERE id = %s""",
                    (thread, ))

    if cursor.rowcount == 0:
        return None

    res = {}
    tdata = cursor.fetchone()
    for keyn, val in enumerate(tdata):
        field = cursor.description[keyn][0]
        if field == 'date':
            val = date_normal(val)
        if field[0:2] == 'is':
            val = bool(val)

        if not counters and field in ['likes', 'dislikes', 'posts']:
            continue
        res[field] = val

    if 'user' in related:
        res['user'] = user_data(res['user'])

    if 'forum' in related:
        res['forum'] = forum_data(res['forum'])

    return res

def thread_exists(thread):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""SELECT 1
                    FROM Threads
                    WHERE id = %s""",
                    (thread, ))

    return cursor.rowcount > 0

def post_create(fields):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""INSERT INTO
                    Posts (message, date, isApproved, isHighlighted, isEdited, isSpam, isDeleted, parent, user, thread, forum)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
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
                        fields.get('thread'),
                        fields.get('forum')
                        ))

        db.commit()

        return cursor.lastrowid
    except IntegrityError:
        return False

def post_data(post, related=[], counters=True):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""SELECT id, message, date, likes, dislikes, points, isApproved, isHighlighted, isEdited, isSpam, isDeleted, parent, user, thread, forum
                    FROM Posts
                    WHERE id = %s""",
                    (post, ))

    if cursor.rowcount == 0:
        return None

    res = {}
    pdata = cursor.fetchone()
    for keyn, val in enumerate(pdata):
        field = cursor.description[keyn][0]
        if field == 'date':
            val = date_normal(val)
        if field[0:2] == 'is':
            val = bool(val)

        if not counters and field in ['likes', 'dislikes', 'points']:
            continue
        res[field] = val

    if 'user' in related:
        res['user'] = user_data(res['user'])

    if 'forum' in related:
        res['forum'] = forum_data(res['forum'])

    if 'thread' in related:
        res['thread'] = thread_data(res['thread'])

    return res
