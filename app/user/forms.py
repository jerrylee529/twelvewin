# -*- coding: utf-8 -*-
# project/user/forms.py


from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from app.models import User


class LoginForm(FlaskForm):
    email = StringField('电子邮箱地址', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    #remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    email = StringField('电子邮箱地址', validators=[DataRequired(), Email(message=None), Length(min=6, max=255)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6, max=255)])
    confirm = PasswordField('重复密码', validators=[DataRequired(), EqualTo('password', message='密码不相同')])
    submit = SubmitField('注册')

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("邮箱地址已经存在")
            return False
        return True


class ForgotForm(FlaskForm):
    email = StringField(
        '电子邮箱地址',
        validators=[DataRequired(), Email(message=None), Length(min=6, max=255)])

    submit = SubmitField('发送')

    def validate(self):
        initial_validation = super(ForgotForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            self.email.errors.append("该邮箱未注册")
            return False
        return True


class ChangePasswordForm(FlaskForm):
    password = PasswordField(
        '密码',
        validators=[DataRequired(), Length(min=6, max=255)]
    )
    confirm = PasswordField(
        '重复密码',
        validators=[
            DataRequired(),
            EqualTo('password', message='密码不相同')
        ]
    )

    submit = SubmitField('修改')

