# from flask import Blueprint, render_template, request, redirect, session, jsonify
# from flask_login import login_user, logout_user, login_manager
# from models import UserRole, User
# from QuanLyHocSinh import dao

# auth = Blueprint('auth', __name__)
#
# @auth.route('/login', methods=['get', 'post'])
# def login_pro():
#     if request.method.__eq__('POST'):
#         username = request.form.get('username')
#         password = request.form.get('password')
#         u = dao.auth_user(username=username, password=password)
#         #u = User.query.filter(User.id==1).first()
#         if u:
#             login_user(u)
#             redirect('/')
#     return render_template('login.html')
# @auth.route("/login", methods=['get', 'post'])
#
# @auth.route('/signup', methods=['GET', 'POST'])
# def sign_up():
#     return render_template('signup.html')
# @auth.route('/logout')
# def logout():
#     return render_template('login.html')
#
#
