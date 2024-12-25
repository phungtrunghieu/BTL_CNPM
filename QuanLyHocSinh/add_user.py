from sqlite3 import IntegrityError
from sqlalchemy.exc import IntegrityError
from  QuanLyHocSinh import app, db, login
from models import HocSinh, Account, LoaiKhoi, User, QTV,GiaoVien, NhanVien, UserRole
from datetime import date
from flask import render_template, request, redirect, session, jsonify, flash
import hashlib
def add_hocsinh(first_name, last_name, date_of_birth, phone, Email, thuoc_khoi):
    try:
        existing_user = HocSinh.query.filter(
            (HocSinh.PhoneNumber == phone) | (HocSinh.email == Email)
        ).first()

        if existing_user:
            flash("Số điện thoại hoặc email đã được sử dụng!", category='error')
            return render_template('signup.html')
        hoc_sinh = HocSinh(
            first_name=first_name,
            last_name=last_name,
            DateBirth=date.fromisoformat(date_of_birth),
            PhoneNumber=phone,
            email=Email,
            thuocKhoi=LoaiKhoi[thuoc_khoi]
        )
        db.session.add(hoc_sinh)
        db.session.commit()

        # Hiển thị thông báo thành công và trả về đối tượng hoc_sinh
        flash("Đăng ký thành công!", category='success')
        return hoc_sinh

    except ValueError:
        flash("Định dạng ngày sinh không hợp lệ!", category='error')
        return None  # Trả về None khi có lỗi định dạng ngày sinh
    except KeyError:
        flash("Loại khối không hợp lệ!", category='error')
        return None  # Trả về None khi loại khối không hợp lệ
    except Exception as e:
        db.session.rollback()  # Khôi phục trạng thái khi có lỗi
        flash(f"Lỗi không xác định: {e}", category='error')
        return None  # Trả về None khi có lỗi không xác định

def add_account(user, user_role):
    try:
        account = Account(
            name = "123123",
            username = user.PhoneNumber,
            password = str(hashlib.md5("123".encode('utf-8')).hexdigest()),
            user_role = UserRole(user_role),
            status = True,
            user = user
        )
        db.session.add(account)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi không xác định: {e}", category='error')
