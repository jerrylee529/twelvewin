# coding=utf8

import os
import configparser

config_parser = configparser.ConfigParser()

env = os.getenv('TW_ANALYSIS_ENV', 'debug')
config_file_path = os.getenv('TW_ANALYSIS_CONFIG_FILE', 'config.ini')

print('env: {}, config file: {}'.format(env, config_file_path))

config_parser.read(config_file_path, encoding='UTF-8')

config = dict()

config['DEBUG'] = config_parser.getboolean(env, 'DEBUG')
config['SECRET_KEY'] = config_parser.get(env, 'SECRET_KEY')
config['SECURITY_PASSWORD_SALT'] = config_parser.get(env, 'SECRET_KEY')

# mail settings
config['MAIL_SERVER'] = config_parser.get(env, 'MAIL_SERVER')
config['MAIL_PORT'] = config_parser.getint(env, 'MAIL_PORT')
config['MAIL_USE_TLS'] = config_parser.getboolean(env, 'MAIL_USE_TLS')
config['MAIL_USE_SSL'] = config_parser.getboolean(env, 'MAIL_USE_SSL')

# mail authentication and sender
config['MAIL_USERNAME'] = config_parser.get(env, 'MAIL_USERNAME')
config['MAIL_PASSWORD'] = config_parser.get(env, 'MAIL_PASSWORD')
config['MAIL_DEFAULT_SENDER'] = config_parser.get(env, 'MAIL_DEFAULT_SENDER')

# database URI
config['SQLALCHEMY_DATABASE_URI'] = config_parser.get(env, 'SQLALCHEMY_DATABASE_URI')

# stripe keys
config['STRIPE_SECRET_KEY'] = config_parser.get(env, 'STRIPE_SECRET_KEY')
config['STRIPE_PUBLISHABLE_KEY'] = config_parser.get(env, 'STRIPE_PUBLISHABLE_KEY')

config['DAY_FILE_PATH'] = config_parser.get(env, 'DAY_FILE_PATH')
config['RESULT_FILE_PATH'] = config_parser.get(env, 'RESULT_FILE_PATH')

my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]

print(config)