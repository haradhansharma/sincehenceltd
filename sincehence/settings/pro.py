import os
from . import BASE_DIR, env


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

from .settings_email import *

from .settings_logs import *

from .settings_security import *

from .settings_summernote import *

from .settings_material_dash import *

# CACHES = {  
#     'default': {
#         'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#         'LOCATION': os.path.join(BASE_DIR, 'cache'),
#         'TIMEOUT': 3600,
#         'OPTIONS': {
#             'MAX_ENTRIES': 1000
#         }
#     }
# }
# USER_AGENTS_CACHE = 'default'
# CACHE_MIDDLEWARE_SECONDS = 3600

RECAPTCHA_PUBLIC_KEY = env("SH_RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = env("SH_RECAPTCHA_PRIVATE_KEY-XbLm")
# RECAPTCHA_DOMAIN = 'www.recaptcha.net'
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']