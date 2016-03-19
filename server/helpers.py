# -*- coding: utf-8 -*-
from werkzeug.exceptions import BadRequest
from flask import jsonify, request

CODE_SUCCESS = 0
CODE_NOT_FOUND = 1
CODE_INVALID = 2
CODE_INVALID_SEMANTIC = 3
CODE_UNKNOWN = 4
CODE_USER_EXISTS = 5

def get_request_json():
    json = request.get_json(True)
    return json

def get_request_arg(key, default=None):
    if default is None:
        return request.args.get(key)
    else:
        return request.args.get(key, default)

def get_request_args(key):
    return request.values.getlist(key)

def result(response, code = CODE_SUCCESS):
    return jsonify({
        'code': code,
        'response': response
        })

def result_not_found(response):
    return result(response, CODE_NOT_FOUND)

def result_invalid(response):
    return result(response, CODE_INVALID)

def result_invalid_semantic(response):
    return result(response, CODE_INVALID_SEMANTIC)

def result_unknown(response):
    return result(response, CODE_UNKNOWN)

def result_user_exists(response):
    return result(response, CODE_USER_EXISTS)


def date_normal(date):
    if date is None:
        return ''
    return date.strftime('%Y-%m-%d %H:%M:%S')

def check_enum(enum, allowed=[]):
    for i in enum:
        if i not in allowed:
            return False
    return True
