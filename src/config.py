from itertools import chain
from functools import reduce
import adapters

DASHBOARD_PREFIX="/cfbroker"

_all_catalogues = [getattr(getattr(adapters, m), 'service_catalogue')
                 for m in adapters.__all__
                 if 'service_catalogue' in dir(getattr(adapters, m))]
print(_all_catalogues)
print( adapters.__all__)
print([dir(getattr(adapters, m)) for m in adapters.__all__])

_merge = lambda l, r: {k: _merge(r.get(k), l.get(k) )
                       if all(isinstance(i.get(k,None), dict) for i in (r, l))
                       else
                       r.get(k, l.get(k))
                       for k in chain(r, l)}

ALL_SERVICE_CATALOGUES = reduce(_merge, _all_catalogues, {})
