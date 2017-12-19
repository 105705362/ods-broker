X_BROKER_API_VERSION = (2, 3)
X_BROKER_API_VERSION_NAME = 'X-Broker-Api-Version'

from app import app
from itertools import chain

def _unfoldservice(d, t = "s"):
    _srv_keys = ('name',
             'description',
             'bindable',
             'tags',
             'metadata'
    )
    _plan_keys = ('name', 'description')
    if t == 's':
        return [ dict(chain([("id", s)],
                           [(k, v[k]) for k in _srv_keys],
                           [("plans", _unfoldservice(v["plans"], 'p') )]))
                 for s,v in list(d.items()) 
        ]
    else:
        return [ dict(chain([("id", s)],
                           [(k, v[k]) for k in _plan_keys]))
                 for s,v in list(d.items())
        ]
    
    
vm_services = _unfoldservice(app.config["ALL_SERVICE_CATALOGUES"])
all_services = app.config["ALL_SERVICE_CATALOGUES"]

def checkversion(x):
    client_version = [int(y) for y in  x.split('.')]
    comp = [ y - x for x,y in zip(X_BROKER_API_VERSION, client_version) ]
    if comp[0] > 0:
        return True
    if comp[0] <0:
        return False
    if comp[1] <0:
        return False
    else:
        return True
    return false
