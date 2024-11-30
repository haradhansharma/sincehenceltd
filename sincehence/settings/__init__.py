import os
import environ
from pathlib import Path


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
env = environ.Env()


SECRET_KEY = env("SH_SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("No SH_SECRET_KEY set for production!")

DEBUG = env.bool("SH_DEBUG", default=False)

if DEBUG:
    ALLOWED_HOSTS = ['*']
    CSRF_TRUSTED_ORIGINS = ["https://127.0.0.1", "https://localhost"]
else:
    ALLOWED_HOSTS = env("SH_CSRF_TRUSTED_ORIGINS").split(",")
    CSRF_TRUSTED_ORIGINS = env("SH_CSRF_TRUSTED_ORIGINS").split(",")

SITE_ID=1

INSTALLED_APPS = [
    'material',
    'material.admin',
    # 'django.contrib.admin',
    'nested_admin',    
    'django_summernote',
    
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    "whitenoise.runserver_nostatic",
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_user_agents',
    # 'django_cron',
    'core',  
    'django.contrib.sitemaps',
    'captcha',  
    'accounts',    
    'contact',
    'cms',    
    'payment_method',
    'policy_concent',   
    'service',
    'django_extensions',
    'sourcing',  
    'shcurrency',   
    'django_humanize', 
    'django_celery_results',
    'django_celery_beat',
    'calendar_app',
    # 'whoischeck',

      
]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("SH_CACHES_LOCATION"),   
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

USER_AGENTS_CACHE = 'default'
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_RESULT_EXTENDED = True

CELERY_BROKER_URL = env("SH_CELERY_BROKER_URL")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

CACHE_MIDDLEWARE_SECONDS = 3600

TEMPLATE_TAGS = ['django_summernote.templatetags.summernote']
AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

LOGIN_URL = "/accounts/login/"

LOGIN_REDIRECT_URL = "/accounts/dashboard/"

LOGOUT_REDIRECT_URL = '/'

MAXIMUM_APPROVAL_REQUEST_ALLOWED = 10

if DEBUG:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        "whitenoise.middleware.WhiteNoiseMiddleware",
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.sites.middleware.CurrentSiteMiddleware',
        # 'django.middleware.cache.UpdateCacheMiddleware',  #new    
        'django.middleware.common.CommonMiddleware',
        # 'django.middleware.cache.FetchFromCacheMiddleware', #new    
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django_user_agents.middleware.UserAgentMiddleware',
        'shcurrency.middleware.CurrencyMiddleware',
    ]
else:
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.sites.middleware.CurrentSiteMiddleware',
        # 'django.middleware.cache.UpdateCacheMiddleware',  #new    
        'django.middleware.common.CommonMiddleware',
        # 'django.middleware.cache.FetchFromCacheMiddleware', #new    
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django_user_agents.middleware.UserAgentMiddleware',
        'shcurrency.middleware.CurrencyMiddleware',
    ]
    
ROOT_URLCONF = 'sincehence.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processor.core_con'
            ],
        },
    },
]

WSGI_APPLICATION = 'sincehence.wsgi.application'

from .settings_database import *
from .settings_local import *
# from .settings_security import *


STATIC_URL = '/static/'

if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


if DEBUG:
    from .dev import *
else:
    from .pro import *
    
ACTIVE_PAYMENT_METHODS = [
# 'payment_method.gateways.stripe.StripePaymentGateway',
# 'payment_method.gateways.paypal.PayPalPaymentGateway',
'payment_method.gateways.bkash.bKashPaymentGateway',
'payment_method.gateways.rocket.RocketPaymentGateway',
'payment_method.gateways.eximbd.EximBdPaymentGateway',


]











IPINFO_TOKEN = env('SH_IPINFO_TOKEN')

ALLOWED_COUNTRY = ['BD']


INVOICE_UPLOAD_TO = 'payment_instruction/'

ORDER_STATUS =(
        ('pending', 'Pending'),  
        ('invoice_initiatd', 'Invoice Initiatd'),          
        ('processing', 'Processing'),
        ('confirm', 'Confirm'),
        ('payment_reject', 'Payment Reject'),
        ('payment_pending', 'Payment Pending'),       
        ('shipped', 'Shipped'),        
        ('completed', 'Completed'),  
        ('canceled', 'Canceled'),
        ('abandoned', 'Abandoned')       
              
    )
PAYMENT_CONFIRM_STATUS = 'confirm'
PAYMENT_REJECT_STATUS = 'payment_reject'

PAYMENT_PROCESSING_STATUS = 'processing'
INCOMPLETE_STATUS = ['pending', 'canceled']
ABANDONED_STATUS = 'abandoned'
PAYMENT_PENDING_STATUS = ['invoice_initiatd', 'payment_reject' ] ## do not add payment pending status here as it can delete using cronjob
COMPLETED_STATUS = ['shipped', 'completed']
PROCESSING_ORDERS = ['processing', 'confirm' ]
INVOICE_PAYMENT_VALIDITY_DAYS = 7

# MILESTONE_TYPE = (
#     ('backend', 'Backend'),  
#     ('frontend', 'Front End'),          
#     ('design', 'Design'),
#     ('copywriting', 'Copy Writing'),
    
    
# )

DAY_CHOICES = [
        (0, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        
    ]
OFFICE_START_TIME = '09:00'
OFFICE_END_TIME = '17:00'


# CRON_CLASSES = [
#     "core.cron_job.RunSinceHenceCronJobs",
#     # ...
# ]


STRIPE_SECRET_KEY = env('SH_STRIPE_SECRET_KEY')
STRIPE_WEBHOOK = env('SH_STRIPE_WEBHOOK')
STRIPE_PUBLISHABLE_KEY = env('SH_STRIPE_PUBLISHABLE_KEY')
DEFAULT_CURRENCY_CODE = env('SH_DEFAULT_CURRENCY_CODE')
OPEN_EXCHANGE_APP_ID = env('SH_OPEN_EXCHANGE_APP_ID')

ALLOED_STATUS_TO_CHECKOUT = ['pending', 'abandoned', 'canceled']

PRICE_TYPES =(
        ('one_time', 'One Time'),
        ('recurring', 'Recurring'),          
    )

INTERVAL =(
        ('month', 'Month'),
        ('year', 'Year'),
        ('week', 'Week'),  
        ('day', 'Day')       
    )

PAYMENT_STATUS =(
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),        
         
    )

QUOTATION_STATUS = [
            ('open', 'Open'), 
            ('expired', 'Expired'), 
            ('denied', 'Denied'), 
            ('response_sent', 'Response Sent'), 
            ('accepted_by_client', 'Accepted By Client'), 
            ('rejected_by_client', 'Rejected By CLient')
            ]

TRANSACTION_TYPE = [
            ('add', 'Add'), 
            ('sub', 'Sub'), 
            
            ]

TRANSACTION_FOR = [
            ('service', 'Service'), 
            ('quotation', 'Quotation'), 
            ('return', 'Return'), 
            ('topup', 'Top Up'), 
            
            
            
            ]


SALING_SERVICE = False