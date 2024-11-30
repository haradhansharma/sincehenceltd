from . import DEBUG, env

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sincehenceltd2' if DEBUG else env("SH_DB_NAME"),
        'USER': 'root' if DEBUG else env("SH_DB_USER"),
        'PASSWORD': '' if DEBUG else env("SH_DB_PASSWORD"),
        'HOST': env("SH_DB_HOST"),
        'PORT': env("SH_DB_PORT"),
        'OPTIONS': {
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}


    
    


