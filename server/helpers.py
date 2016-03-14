# -*- coding: utf-8 -*-
from flask import jsonify

CODE_SUCCESS = 0
CODE_NOT_FOUND = 1
CODE_INVALID = 2
CODE_INVALID_SEMANTIC = 3
CODE_UNKNOWN = 4
CODE_USER_EXISTS = 5

def result(response, code = CODE_SUCCESS):
    return jsonify({
        'code': code,
        'response': response
        })
