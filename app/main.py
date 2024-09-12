import os
from pathlib import Path
from typing import List
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restx import Api


import traceback

from requests import Response

from app.exceptions.forbidden_error import ForbiddenError
from app.exceptions.invalid_argument_exception import InvalidArgumentException
from app.routes.csv_routes import csv_api_ns
from .database import query_manager
from app.logger import logger


environment = os.getenv("ENVIRONMENT")
app = Flask(__name__)


app.config["PROPAGATE_EXCEPTIONS"] = True

app.app_context()

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

api = Api(app)
api.add_namespace(csv_api_ns)


@app.errorhandler(InvalidArgumentException)
def handle_invalid_argument_exception(error):
    response = jsonify({"error": "INVALID_ARGUMENT", "message": error.args[0]})
    response.status_code = 400  # Bad Request
    return response


@app.errorhandler(RuntimeError)
def handle_runtime_exception(error):
    logger.error(error, exc_info=True)
    if hasattr(error, "args") and len(error.args) > 0:
        response = jsonify({"error": "RUNTIME_ERROR", "message": error.args[0], "data": None})
    elif hasattr(error, "message"):
        response = jsonify({"error": "RUNTIME_ERROR", "message": error.message, "data": None})
    else:
        response = jsonify({"error": "RUNTIME_ERROR", "message": str(error), "data": None})
    response.status_code = 500  # Internal Server Error

    return response


@app.errorhandler(ValueError)
def handle_value_error(error) -> Response:
    response: Response = jsonify({"error": "VALUE_ERROR", "message": error.args[0], "data": None})
    response.status_code = 400  # Bad Request
    return response


# Custom 404 error handler
@app.errorhandler(404)
def page_not_found(error):
    return {
        "error": "PATH_NOT_FOUND",
        "message": f"error = {str(error)} | url = {request.url}",
        "data": None,
    }, 404


# Custom 403 error handler
@app.errorhandler(ForbiddenError)
def forbidden_request(error):
    return {
        "error": "INVALID_USER_TOKEN",
        "message": error.args[0],
        "data": None,
    }, 403


@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(error, exc_info=True)
    if hasattr(error, "args") and len(error.args) > 0:
        response = jsonify({"error": error.args[0]})
    elif hasattr(error, "message"):
        response = jsonify({"error": error.message})
    else:
        response = jsonify({"error": str(error)})
    response.status_code = 500  # Internal Server Error

    return response


def is_forbidden_url(url: str, forbidden_list: List[str]):
    return any(endpoint in url for endpoint in forbidden_list)


@app.before_request
def before():
    if "swagger" not in request.url:
        logger.info(
            "Request :%s",
            {"url": request.url, "header": request.headers, "body": request.get_data()},
        )


@app.after_request
def after(response):
    if response.json is not None and "swagger" not in request.url:
        logger.info(
            "Response: %s",
            {"url": request.url, "status_code": response.status, "data": response.json},
        )
    return response
