import json, sys
from flask import Blueprint, request, g, abort, jsonify
from app import app
from app.exceptions import *
from app.metadata import *
from app.auth import auth
from functools import wraps
from werkzeug.contrib.cache import SimpleCache

last_ops = SimpleCache()

service_broker = Blueprint('srvbrk', __name__, url_prefix="/")
def prepare_adapter(f):
    @wraps(f)
    def wrpr(*args, **kargs):
        if request.method in ('PUT', 'PATCH'):
            data = request.get_json()
            service_id = data.get('service_id')
            plan_id = data.get('plan_id')
        else:
            service_id = request.args.get('service_id')
            plan_id = request.args.get('plan_id')
        if all((service_id is not None,
                plan_id is not None,
                service_id in all_services,
                'plans' in all_services[service_id],
                plan_id in all_services[service_id]['plans'])):
            request.adapter_cls = all_services[service_id]['plans'][plan_id]["adapter"]
            request.adapter_cls._env = app.config["BOSH"]
        else:
            request.adapter_cls = None
        return f(*args, **kargs)
    return wrpr
        

@service_broker.route('/v2/catalog', methods=['GET'])
@auth.login_required
def catalog():
    """
    Return the catalog of services handled
    by this broker
    
    GET /v2/catalog:
    
    HEADER:
        X-Broker-Api-Version: <version>
        X-Api-Info-Location: cloud-info-location
    return:
        JSON document with details about the
        services offered through this broker
    """
    api_version = request.headers.get('X-Broker-Api-Version')
    cloud_api_location = request.headers.get('X-Api-Info-Location', None)
      
    if not api_version or not checkversion(api_version):
        raise ServiceBrokerException(409, "Missing or incompatible %s. Expecting version %0.1f or later" % (X_BROKER_API_VERSION_NAME, X_BROKER_API_VERSION))

    return jsonify({"services": vm_services})

@service_broker.route('/v2/service_instances/<instance_id>', methods=['PUT', 'PATCH'])
@auth.login_required
@prepare_adapter
def provision(instance_id):
    if request.args.get("accepts_incomplete", "false") != "true":
        return jsonify({"error": "AsyncRequired",
                        "description": "This service plan requires client support for asynchronous service operations."
            }),422
    ada = request.adapter_cls(instance_id)
    n, t = ada.workflow("deploy", None)

    if n == "finish":
        return jsonify({}), 200
    if n == "error":
        return jsonify({"description": "%s:%s Failed"%(n,t)}), 503
    return jsonify({"operation": "%s:%s"%(n,t)}), 202

@service_broker.route('/v2/service_instances/<instance_id>/last_operation', methods=['GET'])
@auth.login_required
@prepare_adapter
def poll(instance_id):
    op = request.args.get("operation")
    n,t = (lambda x, y: x if x is not None else y)(last_ops.get(op), op.split(":"))
    if request.adapter_cls is None:
        return jsonify({"state":"failed", "description": "can't find plan_id"}), 200
    ada = request.adapter_cls(instance_id)
    n,t = ada.workflow(n, int(t))
    r = {"description": "%s %s"%(n,t)}
    if op.find("deploy") == 0:
        if n == "finish":
            r["state"] = "succeeded"
            return jsonify(r), 200
        if n == "error":
            r["state"] = "failed"
            return jsonify(r), 200
        r["state"] = "in progress"
        last_ops.set(op,(n,t))
        return jsonify(r), 200
    if op.find("delete") ==0:
        if n == "finish":
            return jsonify({}), 410
        if n == "error":
            r["state"] = "failed"
            return jsonify(r), 200
        r["state"] = "in progress"
        last_ops.set(op,(n,t))
        return jsonify(r), 200

@service_broker.route('/v2/service_instances/<instance_id>', methods=['DELETE'])
@auth.login_required
@prepare_adapter
def deprovision(instance_id):
    if request.adapter_cls is None:
        return jsonify({"state":"failed", "description": "can't find plan_id"}), 503
    ada = request.adapter_cls(instance_id)
    n, t = ada.workflow("delete", None)

    if n == "finish":
        return jsonify({}), 200
    if n == "error":
        return jsonify({"description": "%s:%s Failed"%(n,t)}), 503
    return jsonify({"operation": "%s:%s"%(n,t)}), 202
    
    

@service_broker.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['PUT'])
@auth.login_required
@prepare_adapter
def bind(instance_id, binding_id):
    if request.adapter_cls is None:
        return jsonify({"state":"failed", "description": "can't find plan_id"}), 503
    ada = request.adapter_cls(instance_id)
    creds = ada.get_creds()
    return jsonify(
        creds
    ), 200

@service_broker.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['DELETE'])
@auth.login_required
def unbind(instance_id, binding_id):
    print(request.data, file=sys.stderr)


    return jsonify(
        {}
    ), 200
