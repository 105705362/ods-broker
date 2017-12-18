import os, re
__pat = re.compile("^([a-zA-Z].*)\.py$")
__dir_pat = re.compile("^([a-zA-Z].*)$")
__all__ = [j.groups()[0] 
           for j in [__pat.match(i.name) if i.is_file() else __dir_pat.match(i.name) if i.is_dir() else None
                     for i in os.scandir(__path__[0])]
           if j is not None]
from . import *
