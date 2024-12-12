import os
from .common import *

IS_IN_PRODUCTION = os.environ.get('IS_IN_PRODUCTION')

if int(IS_IN_PRODUCTION):
    from .production import *
else:
    from .development import *
