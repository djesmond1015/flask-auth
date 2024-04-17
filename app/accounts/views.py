from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

from app import db, bcrypt, oauth, google
from app.accounts.models import User
from app.accounts.token import confirm_token, generate_token
from app.utils.decorators import logout_required
from app.utils.email import send_email

from .forms import RegisterForm, LoginForm

accounts_bp = Blueprint("accounts", __name__)

@accounts_bp.route("/register", methods=["GET", "POST"])
@logout_required
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        token = generate_token(user.email)
        confirm_url = url_for('accounts.confirm_email', token = token, _external = True)
        html = render_template('accounts/confirm_email.html', confirm_url = confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)

        login_user(user)

        flash("A confirmation email has been sent via email.", "success")
        return redirect(url_for("accounts.inactive"))

    return render_template("accounts/register.html", form=form)


@accounts_bp.route("/login", methods=["GET", "POST"])
@logout_required
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("core.home"))
        else:
            flash("Invalid email or/and password", "danger")
            return render_template("accounts/login.html", form=form)
    return render_template("accounts/login.html", form=form)

@accounts_bp.route('/confirm/<token>')
@login_required
def confirm_email(token):
    if current_user.is_confirmed:
        flash('Account already confirmed', 'success')
    email = confirm_token(token)
    user = User.query.filter_by(email = current_user.email).first_or_404()
    if user.email == email:
        user.is_confirmed = True
        user.confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    else:
        flash('The confirmation link is invalid or expired', 'danger')
    return redirect(url_for('core.home'))

@accounts_bp.route('/inactive')
@login_required
def inactive():
    if current_user.is_confirmed:
        return redirect(url_for('core.home'))
    return render_template('accounts/inactive.html')

@accounts_bp.route('/resend')
@login_required
def resend_confirmation():
    if current_user.is_confirmed:
        flash('Your account has already been confirmed.', 'success')
        return redirect(url_for('core.home'))
    token = generate_token(current_user.email)
    confirm_url = url_for('accounts.confirm_email', token = token, _external = True)
    html = render_template('accounts/confirm_email.html', confirm_url= confirm_url)
    subject = 'Please confirm your email'
    send_email(current_user.email, subject, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('accounts.inactive'))

# Google OAuth
@accounts_bp.route('/auth/google')
@logout_required
def google_login():
    google_client = oauth.create_client("google")
    redirect_uri = url_for('accounts.google_auth', _external = True)
    return google_client.authorize_redirect(redirect_uri)

# todo: is the password hashed

@accounts_bp.route('/auth/google/callback')
@logout_required
def google_auth():
    google_client = oauth.create_client("google")
    token = google_client.authorize_access_token()
    resp = google_client.get('userinfo')
    user_info = resp.json()
    user = User.query.filter_by(email = user_info['email']).first()
    if user:
        login_user(user)
        return redirect(url_for('core.home'))
    else:
        user_dist = {
            'authProvider': 'google',
            'email': user_info['email'],
            'password': user_info['email'],
            'username': user_info['name'],
            'avatar_url': user_info['picture'],
            'is_admin': False,
            'is_confirmed': True,
            'confirmed_on': datetime.now()
        }
        user = User(**user_dist)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('core.home'))

@accounts_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out", "success")
    return redirect(url_for("accounts.login"))

