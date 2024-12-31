

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
from .settings_email import *
from .settings_logs import *
# from .settings_security import *
from .settings_summernote import *
X_FRAME_OPTIONS = 'SAMEORIGIN'
# SESSION_COOKIE_SAMESITE = 'Secure'
SESSION_COOKIE_SECURE = True

from .settings_material_dash import *







RECAPTCHA_PUBLIC_KEY = str('6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')
RECAPTCHA_PRIVATE_KEY = str('6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe')
RECAPTCHA_DOMAIN = 'www.recaptcha.net'
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']







