# -*- coding: utf-8 -*-


#################
#### imports ####
#################

from flask import render_template
from flask import Blueprint
from flask_login import current_user
from flask_login import login_required

################
#### config ####
################

import sys   #reload()之前必须要引入模块
reload(sys)
sys.setdefaultencoding('utf-8')

main_blueprint = Blueprint('main', __name__,)


################
#### routes ####
################

@main_blueprint.route('/')
def home():
    return render_template('main/index.html', current_user=current_user)



