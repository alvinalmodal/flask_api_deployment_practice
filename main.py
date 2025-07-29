from flask import Flask, jsonify, abort, request
import redis
from datetime import datetime
from functools import wraps
import json
from .decorators.auth import auth_sample

app = Flask(__name__)

app.config["TOTAL_CALLS"] = 0
r = redis.Redis(host='localhost', port=6379, db=0)

def update_api_request_count(api_key: str) -> int:
    existing_redis = r.get(api_key)
    if existing_redis:
        existing_redis = str(int(existing_redis) + 1)
        r.set(api_key, existing_redis)
    else:
        existing_redis = str(1)
        r.set(api_key, existing_redis)
    return int(existing_redis)
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="ratelimit exceeded", message="You have exceeded your request rate"), 429


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error="Huy wala naman yun hinahanap mo"), 404



def logger_redis(func):
    @wraps(func)
    def inner(*args, **kwargs):
        log_key = datetime.now().strftime("%Y%m%d%H%M%S") + "_logs"
        r.set(log_key, "this is just a logging example")
        result = func(*args, **kwargs)
        query_params = request.args.to_dict()
        after_key_logs = datetime.now().strftime("%Y%m%d%H%M%S") + "_after_logs_query_params"
        object_to_log = {
            "query_params": query_params,
            "result": result,
        }
        r.set(after_key_logs, json.dumps(object_to_log))

        return result
    return inner


@app.route("/api/weather", methods=["GET"])
@logger_redis
@auth_sample
def get_weather():
    query_params = request.args.to_dict()
    api_key = query_params.get("apiKey","default")
    call_count = update_api_request_count(api_key)
    if call_count <= 12:
        return {
            "test": 123,
            "name": "testname",
            "counter": app.config["TOTAL_CALLS"],
            "call_count": call_count,
        }
    else:
        abort(429)

@app.route("/api/customers", methods=["GET"])
@auth_sample
def get_customers():
    return {
        "customers": ["alvin","diane","derick"]
    }
