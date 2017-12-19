from itertools import chain
from functools import reduce
import adapters
import os
import os.path
from bosh_api import *

_all_catalogues = [getattr(getattr(adapters, m), 'service_catalogue')
                 for m in adapters.__all__
                 if 'service_catalogue' in dir(getattr(adapters, m))]
print(_all_catalogues)
print(( adapters.__all__))
print([dir(getattr(adapters, m)) for m in adapters.__all__])

_merge = lambda l, r: {k: _merge(r.get(k), l.get(k) )
                       if all(isinstance(i.get(k,None), dict) for i in (r, l))
                       else
                       r.get(k, l.get(k))
                       for k in chain(r, l)}

ALL_SERVICE_CATALOGUES = reduce(_merge, _all_catalogues, {})

bosh_env_ip = os.getenv("BOSH_ENVIRONMENT")
bosh_client = os.getenv("BOSH_CLIENT")
bosh_client_secret = os.getenv("BOSH_CLIENT_SECRET")

_e_bosh_cacert = os.getenv("BOSH_CACERT")
if os.path.exists(_e_bosh_cacert):
    bosh_cacert = _e_bosh_cacert
else:
    import tempfile
    _f , bosh_cacert = tempfile.mkstemp(".cert", "bosh_ca_", "/tmp/")
    _fp = os.fdopen(_f, "w")
    _fp.write(_e_bosh_cacert)
    _fp.close()

BOSH = BoshEnv(bosh_env_ip, bosh_client, bosh_client_secret, cacert=bosh_cacert)
