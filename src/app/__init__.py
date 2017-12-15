from flask import Flask, jsonify, session

from app.exceptions import ServiceBrokerException


import os

app = Flask(__name__)


app.config.from_object('config')

@app.errorhandler(ServiceBrokerException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

from app.service_broker.controllers import service_broker as service_broker_module

app.register_blueprint(service_broker_module, url_prefix='')


#db.create_all()
