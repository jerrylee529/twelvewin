# coding=utf8

"""analysis 目录批处理任务的配置加载模块。

从 TW_ANALYSIS_CONFIG_FILE 指定的 INI 文件读取 TW_ANALYSIS_ENV 对应配置段；
若 INI 不存在则回退到 Flask APP_SETTINGS（与 jobs/config.py 行为一致）。
"""

import os
import configparser

_analysis_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_analysis_dir)
_default_config_file = os.path.join(_analysis_dir, 'config.ini')


def _resolve_ini_section(parser, preferred_env):
    if preferred_env in parser:
        return preferred_env
    for fallback_env in ('local', 'debug', 'development', 'production'):
        if fallback_env in parser:
            return fallback_env
    sections = parser.sections()
    return sections[0] if sections else None


def _load_config_from_ini(config_file_path, env):
    parser = configparser.ConfigParser()
    parser.read(config_file_path, encoding='UTF-8')
    section = _resolve_ini_section(parser, env)
    if section is None:
        return None

    return {
        'DEBUG': parser.getboolean(section, 'DEBUG'),
        'SECRET_KEY': parser.get(section, 'SECRET_KEY'),
        'SECURITY_PASSWORD_SALT': parser.get(section, 'SECRET_KEY'),
        'MAIL_SERVER': parser.get(section, 'MAIL_SERVER'),
        'MAIL_PORT': parser.getint(section, 'MAIL_PORT'),
        'MAIL_USE_TLS': parser.getboolean(section, 'MAIL_USE_TLS'),
        'MAIL_USE_SSL': parser.getboolean(section, 'MAIL_USE_SSL'),
        'MAIL_USERNAME': parser.get(section, 'MAIL_USERNAME'),
        'MAIL_PASSWORD': parser.get(section, 'MAIL_PASSWORD'),
        'MAIL_DEFAULT_SENDER': parser.get(section, 'MAIL_DEFAULT_SENDER'),
        'SQLALCHEMY_DATABASE_URI': parser.get(section, 'SQLALCHEMY_DATABASE_URI'),
        'STRIPE_SECRET_KEY': parser.get(section, 'STRIPE_SECRET_KEY'),
        'STRIPE_PUBLISHABLE_KEY': parser.get(section, 'STRIPE_PUBLISHABLE_KEY'),
        'DAY_FILE_PATH': parser.get(section, 'DAY_FILE_PATH'),
        'RESULT_FILE_PATH': parser.get(section, 'RESULT_FILE_PATH'),
    }


def _load_config_from_flask():
    import sys

    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)

    os.environ.setdefault('TWELVEWIN_DISABLE_ANALYZER', '1')
    os.environ.setdefault('APP_SETTINGS', 'app.config.LocalConfig')

    from app import app

    day_file_path = app.config.get('DAY_FILE_PATH') or ''
    if day_file_path and not day_file_path.endswith(os.sep):
        day_file_path = day_file_path + os.sep

    result_path = app.config.get('RESULT_PATH') or app.config.get('RESULT_FILE_PATH') or ''

    return {
        'DEBUG': bool(app.config.get('DEBUG', True)),
        'SECRET_KEY': app.config.get('SECRET_KEY', 'local-dev'),
        'SECURITY_PASSWORD_SALT': app.config.get('SECURITY_PASSWORD_SALT', 'local-dev'),
        'MAIL_SERVER': app.config.get('MAIL_SERVER', ''),
        'MAIL_PORT': int(app.config.get('MAIL_PORT', 465)),
        'MAIL_USE_TLS': bool(app.config.get('MAIL_USE_TLS', False)),
        'MAIL_USE_SSL': bool(app.config.get('MAIL_USE_SSL', True)),
        'MAIL_USERNAME': app.config.get('MAIL_USERNAME'),
        'MAIL_PASSWORD': app.config.get('MAIL_PASSWORD'),
        'MAIL_DEFAULT_SENDER': app.config.get('MAIL_DEFAULT_SENDER'),
        'SQLALCHEMY_DATABASE_URI': app.config.get('SQLALCHEMY_DATABASE_URI'),
        'STRIPE_SECRET_KEY': app.config.get('STRIPE_SECRET_KEY'),
        'STRIPE_PUBLISHABLE_KEY': app.config.get('STRIPE_PUBLISHABLE_KEY'),
        'DAY_FILE_PATH': day_file_path,
        'RESULT_FILE_PATH': result_path,
    }


env = os.getenv('TW_ANALYSIS_ENV', 'debug')
config_file_path = os.getenv('TW_ANALYSIS_CONFIG_FILE', _default_config_file)

if not os.path.isabs(config_file_path):
    config_file_path = os.path.abspath(config_file_path)

print('env: {}, config file: {}'.format(env, config_file_path))

config = None
if os.path.isfile(config_file_path):
    config = _load_config_from_ini(config_file_path, env)

if config is None:
    print('analysis config: INI unavailable, using Flask APP_SETTINGS fallback')
    config = _load_config_from_flask()

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
