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

def result(response, code = CODE_SUCCESS):
    return jsonify({
        'code': code,
        'response': response
        })
