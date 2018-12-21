# -*- coding: utf-8 -*-
# project/user/views.py


#################
#### imports ####
#################

import datetime

from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask_login import login_user, logout_user, \
    login_required, current_user

from app.models import User
from app.myemail import send_email
from app.token import generate_confirmation_token, confirm_token
from app.decorators import check_confirmed
from app import db, bcrypt
from .forms import LoginForm, RegisterForm, ChangePasswordForm, ForgotForm


################
#### config ####
################

user_blueprint = Blueprint('user', __name__,)


################
#### routes ####
################

@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=form.password.data,
            confirmed=False
        )
        db.session.add(user)
        db.session.commit()

        token = generate_confirmation_token(user.email)
        confirm_url = url_for('user.confirm_email', token=token, _external=True)
        html = render_template('user/activate.html', confirm_url=confirm_url)
        subject = "请确认您的帐号"
        send_email(user.email, subject, html)

        login_user(user)

        flash('一封帐号确认邮件已发送至您的邮箱', 'success')
        return redirect(url_for("user.unconfirmed"))

    return render_template('user/register.html', form=form)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
                user.password, request.form['password']):
            login_user(user)
            flash('欢迎来到团赢数据', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('邮件地址或者密码不正确', 'danger')
            return render_template('user/login.html', form=form, msg='邮件地址或者密码不正确')
    return render_template('user/login.html', form=form)


@user_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已安全退出系统', 'success')
    return redirect(url_for('user.login'))


@user_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
@check_confirmed
def profile():
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if user:
            user.password = bcrypt.generate_password_hash(form.password.data)
            db.session.commit()
            flash('成功修改密码', 'success')
            return redirect(url_for('user.profile'))
        else:
            flash('成功修改密码', 'danger')
            return redirect(url_for('user.profile'))
    return render_template('user/profile.html', form=form)


@user_blueprint.route('/confirm/<token>')
@login_required
def confirm_email(token):
    if current_user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
        return redirect(url_for('main.home'))
    email = confirm_token(token)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if user.email == email:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('已成功确认您的帐号，谢谢!', 'success')
    else:
        flash('帐号确认链接已经过期或者失效', 'danger')
    return redirect(url_for('main.home'))


@user_blueprint.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    flash('请通过邮件确认您的帐号!', 'warning')
    return render_template('user/unconfirmed.html')


@user_blueprint.route('/resend')
@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('user.confirm_email', token=token, _external=True)
    html = render_template('user/activate.html', confirm_url=confirm_url)
    subject = "请确认您的邮件地址"
    send_email(current_user.email, subject, html)
    flash('一封新的帐号确认邮件已发往您的邮箱', 'success')
    return redirect(url_for('user.unconfirmed'))


@user_blueprint.route('/forgot',  methods=['GET', 'POST'])
def forgot():
    form = ForgotForm(request.form)
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        token = generate_confirmation_token(user.email)

        user.password_reset_token = token
        db.session.commit()

        reset_url = url_for('user.forgot_new', token=token, _external=True)
        html = render_template('user/reset.html',
                               username=user.email,
                               reset_url=reset_url)
        subject = "重置密码"
        send_email(user.email, subject, html)

        flash('一封密码重置邮件已发往您的邮箱', 'success')
        return redirect(url_for("main.home"))

    return render_template('user/forgot.html', form=form)


@user_blueprint.route('/forgot/new/<token>', methods=['GET', 'POST'])
def forgot_new(token):

    email = confirm_token(token)
    user = User.query.filter_by(email=email).first_or_404()

    if user.password_reset_token is not None:
        form = ChangePasswordForm(request.form)
        if form.validate_on_submit():
            user = User.query.filter_by(email=email).first()
            if user:
                user.password = bcrypt.generate_password_hash(form.password.data)
                user.password_reset_token = None
                db.session.commit()

                login_user(user)

                flash('修改密码成功', 'success')
                return redirect(url_for('user.profile'))

            else:
                flash('修改密码失败', 'danger')
                return redirect(url_for('user.profile'))
        else:
            flash('您现在可以修改密码了', 'success')
            return render_template('user/forgot_new.html', form=form)
    else:
        flash('无法重置您的密码，请重试', 'danger')

    return redirect(url_for('main.home'))
