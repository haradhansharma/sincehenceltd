import os
from . import BASE_DIR, env


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

from .settings_email import *

from .settings_logs import *

from .settings_security import *

from .settings_summernote import *

from .settings_material_dash import *


RECAPTCHA_PUBLIC_KEY = env("SH_RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = env("SH_RECAPTCHA_PRIVATE_KEY")
# RECAPTCHA_DOMAIN = 'www.recaptcha.net'
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']