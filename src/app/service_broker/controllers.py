import json, sys
gm = Manager()
last_ops = gm.dict()

from flask import Blueprint, request, g, abort, jsonify

from app import app

from app.exceptions import *

from app.metadata import *

from app.auth import auth

service_broker = Blueprint('srvbrk', __name__, url_prefix="/")

from functools import wraps

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
        if all(service_id is not None,
               plan_id is not None,
               service_id in all_services,
               'plans' in all_services[service_id],
               plan_id in all_services[service_id]['plans']):
            request.adapter_cls = all_services[service_id][plan_id]["adapter"]
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
    bosh_env = app.config["BOSH"]
    ada = request.adapter_cls(instance_id, bosh_env)
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
    if hasattr(g, 'last_ops'):
        last_ops = g.last_ops
    else:
        g.last_ops = {}
        last_ops = g.last_ops
    n,t = last_ops.pop(op, op.split(":"))
    bosh_env = app.config["BOSH"]
    if request.adapter_cls is None:
        return jsonify({"state":"failed", "description": "can't find plan_id"}), 200
    ada = request.adapter_cls(instance_id, bosh_env)
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
        last_ops[op]=(n,t)
        return jsonify(r), 200
    if op.find("delete") ==0:
        if n == "finish":
            return jsonify({}), 410
        if n == "error":
            r["state"] = "failed"
            return jsonify(r), 200
        r["state"] = "in progress"
        last_ops[op]=(n,t)
        return jsonify(r), 200

@service_broker.route('/v2/service_instances/<instance_id>', methods=['DELETE'])
@auth.login_required
@prepare_adapter
def deprovision(instance_id):
    bosh_env = app.config["BOSH"]
    if request.adapter_cls is None:
        return jsonify({"state":"failed", "description": "can't find plan_id"}), 503
    ada = request.adapter_cls(instance_id, bosh_env)
    n, t = ada.workflow("deploy", None)

    if n == "finish":
        return jsonify({}), 200
    if n == "error":
        return jsonify({"description": "%s:%s Failed"%(n,t)}), 503
    return jsonify({"operation": "%s:%s"%(n,t)}), 202
    
    

@service_broker.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['PUT'])
@auth.login_required
@prepare_adapter
def bind(instance_id, binding_id):
    bosh_env = app.config["BOSH"]
    if request.adapter_cls is None:
        return jsonify({"state":"failed", "description": "can't find plan_id"}), 503
    ada = request.adapter_cls(instance_id, bosh_env)
    creds = ada.get_creds()
    return jsonify(
        creds
    ), 200

@service_broker.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['DELETE'])
@auth.login_required
def unbind(instance_id, binding_id):
    print >> sys.stderr, request.data


    return jsonify(
        {}
    ), 200
