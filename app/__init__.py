# -*- coding: utf-8 -*-


#################
#### imports ####
#################

import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from redis_op import RedisOP
import logging



################
#### config ####
################

def _check_config_variables_are_set(config):
    assert config['MAIL_USERNAME'] is not None,\
           'MAIL_USERNAME is not set, set the env variable APP_MAIL_USERNAME '\
           'or MAIL_USERNAME in the production config file.'
    assert config['MAIL_PASSWORD'] is not None,\
           'MAIL_PASSWORD is not set, set the env variable APP_MAIL_PASSWORD '\
           'or MAIL_PASSWORD in the production config file.'

    assert config['SECRET_KEY'] is not None,\
           'SECRET_KEY is not set, set it in the production config file.'
    assert config['SECURITY_PASSWORD_SALT'] is not None,\
           'SECURITY_PASSWORD_SALT is not set, '\
           'set it in the production config file.'

    assert config['SQLALCHEMY_DATABASE_URI'] is not None,\
           'SQLALCHEMY_DATABASE_URI is not set, '\
           'set it in the production config file.'

    if os.environ['APP_SETTINGS'] == 'project.config.ProductionConfig':
        assert config['STRIPE_SECRET_KEY'] is not None,\
               'STRIPE_SECRET_KEY is not set, '\
               'set it in the production config file.'
        assert config['STRIPE_PUBLISHABLE_KEY'] is not None,\
               'STRIPE_PUBLISHABLE_KEY is not set, '\
               'set it in the production config file.'


app = Flask(__name__)


print(os.environ['APP_SETTINGS'])

app.config.from_object(os.environ['APP_SETTINGS'])
#_check_config_variables_are_set(app.config)

handler = logging.FileHandler('flask.log', encoding='UTF-8')
handler.setLevel(logging.DEBUG)
logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)

# 创建redis连接池
RedisOP.create_pool(app.config)


####################
#### extensions ####
####################

login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
toolbar = DebugToolbarExtension(app)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

from analyzer import Analyzer
analyzer = Analyzer(app, db)

####################
#### blueprints ####
####################

from app.main.views import main_blueprint
from app.user.views import user_blueprint
from app.stock.views import stock_blueprint
from app.business.views import business_blueprint
from app.strategy_analysis.views import strategy_analysis_blueprint
from app.technical_analysis.views import technical_analysis_blueprint
from app.self_selected_stock.views import self_selected_stock_blueprint
from app.industry_analysis.views import industry_analysis_blueprint
from app.cluster_analysis.views import cluster_analysis_blueprint
from app.annual_report.views import annual_report_blueprint
app.register_blueprint(main_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(stock_blueprint)
app.register_blueprint(business_blueprint)
app.register_blueprint(strategy_analysis_blueprint)
app.register_blueprint(technical_analysis_blueprint)
app.register_blueprint(self_selected_stock_blueprint)
app.register_blueprint(industry_analysis_blueprint)
app.register_blueprint(cluster_analysis_blueprint)
app.register_blueprint(annual_report_blueprint)


####################
#### flask-login ####
####################

from app.models import User

login_manager.login_view = "user.login"
login_manager.login_message_category = "danger"


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


########################
#### error handlers ####
########################

@app.errorhandler(403)
def forbidden_page(error):
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("errors/500.html"), 500
