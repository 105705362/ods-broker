import ods_adapter
from bosh_api import *
import yaml
from jsonpath_ng.ext import parse
from . import SampleOdsAdapter
class SampleOdsAdapter2(SampleOdsAdapter):
    _render_rules = [("$.instance_groups[?name=app]..properties.password", "adadasdda"),
                     ("$.instance_groups[?name=app].instances", 2),
                     ("$.instance_groups[?name=app].vm_type", "small")
    ]

service_catalogue = {"962ce7a9-edc2-4bc6-9751-bb528acd9757":
                     {"name": "learn-bosh",
                      'description': "an example service",
                      'bindable': True,
                      'plan_updateable': True,
                      'tags': ['ruby'],
                      'metadata': {"longDescription": "Simple example service"},
                      "plans": {
                          '21dc84ee-ae61-4017-8c77-367fc8ea1383': {
                              "name": "TEST_Plan_Small",
                              "is_ods": True,
                              "adapter": SampleOdsAdapter2,
                              "description": "Test Plan using small vm type."}}}}
    
