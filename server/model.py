# -*- coding: utf-8 -*-
from _mysql_exceptions import IntegrityError
from app import *

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
