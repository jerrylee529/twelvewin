# -*- coding: utf-8 -*-
# project/decorators.py


from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            return redirect(url_for('user.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function
