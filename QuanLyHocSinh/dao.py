import hashlib
from models import UserRole, Account, LoaiKhoi, HocSinh, User, MonHoc

from flask import flash

from models import Account


def auth_user(username, password, role):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = Account.query.filter(Account.username.__eq__(username.strip()),
                             Account.password.__eq__(password))

    if role:
        u = u.filter(Account.user_role.__eq__(role))

    return u.first()





def get_user_by_id(id):
    return Account.query.get(id)

def revenue_stats():
    return db.session.query()