# -*- coding: utf-8 -*-
from _mysql_exceptions import IntegrityError
from app import *
from helpers import date_normal

def model_method(func):
    def f(*args, **kwargs):
        db = get_db()
        cursor = db.cursor()

        try:
            res = func(db, cursor, *args, **kwargs)
        except IntegrityError:
            return False
        cursor.close()
        return res

    return f

def model_dict(obj, description, remove=[]):
    res = {}
    for keyn, val in enumerate(obj):
        field = description[keyn][0]
        if field == 'date':
            val = date_normal(val)
        if field[0:2] == 'is':
            val = bool(val)

        if field in remove:
            continue
        res[field] = val

    return res
