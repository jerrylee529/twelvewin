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

print(config)