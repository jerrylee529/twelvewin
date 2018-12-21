# -*- coding: utf-8 -*-

# project/util.py


from app import app, db
from app.models import User
from sqlalchemy.orm import class_mapper
import json
from werkzeug.utils import import_string

'''
class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    @classmethod
    def setUpClass(self):
        db.create_all()
        user = User(
            email="test@user.com",
            password="just_a_test_user",
            confirmed=False
        )
        db.session.add(user)
        db.session.commit()

    @classmethod
    def tearDownClass(self):
        db.session.remove()
        db.drop_all()
'''

# sqlalchemy对象转换为json
def model_to_json(model):
    """Transforms a model into a dictionary which can be dumped to JSON."""
    # first we get the names of all the columns on your model
    columns = [c.key for c in class_mapper(model.__class__).columns]
    # then we return their values in a dict
    d = dict((c, getattr(model, c)) for c in columns)
    return json.dumps(d)

def string_to_obj(obj):
    if isinstance(obj, (str,)):
        obj = import_string(obj)

    return obj