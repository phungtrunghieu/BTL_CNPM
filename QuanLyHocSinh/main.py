from operator import index

from wtforms.validators import email
from datetime import date
from QuanLyHocSinh import app, db, login
from flask import render_template, request, redirect, session, jsonify, flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from models import (UserRole, Account, LoaiKhoi, HocSinh, User,
                    MonHoc, BangDiem, Khoi, Lop, MonHocKhoi,
                    ChiTietCotDiem, CotDiem, NienKhoa, HocSinhLop, Diem,
                    HocKi, GiaoVien)
import dao
import add_user
import hashlib


@app.route('/')
def base():
    return render_template('login.html')


@app.route('/login', methods=['get', 'post'])
def login_proces():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user_role = request.form.get('user_role')
        u = dao.auth_user(username=username, password=password, role=user_role)
        if u:
            login_user(u)
            return redirect('/home')
        else:
            flash('Tài khoản không tồn tại', category='error')
    return render_template('login.html', UserRole=UserRole)


@app.route('/info', methods=['get', 'post'])
def info():
    if current_user.is_authenticated:
        return render_template('thongtin.html', user_role=UserRole)
    return render_template('login.html')


@app.route('/home', methods=['get', 'post'])
@login_required
def home():
    return render_template('index.html', UserRole=UserRole)


@app.route('/signup', methods=['GET', 'POST'])
@login_required
def sign_up():
    if current_user.user_role != UserRole.NhanVien:
        flash("access deny")
        return redirect('/home')
    if request.method.__eq__('POST'):
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        date_of_birth = request.form.get('birthdate')
        phone = request.form.get('phone')
        Email = request.form.get('email')
        thuoc_khoi = request.form.get('thuoc_khoi')
        user = add_user.add_hocsinh(first_name=first_name, last_name=last_name, date_of_birth=date_of_birth,
                                    phone=phone, Email=Email, thuoc_khoi=thuoc_khoi)
        account = add_user.add_account(user=user, user_role=UserRole.HocSinh)

    return render_template('signup.html')


@app.route("/quan_ly_mon_hoc")
def quan_ly_mon_hoc():
    if current_user.user_role != UserRole.QuanTriVien:
        flash("access deny")
        return redirect('/home')
    return render_template('subject_manager.html')


@app.route("/them_mon_hoc", methods=['get', 'post'])
def them_mon_hoc():
    if current_user.user_role != UserRole.QuanTriVien:
        flash("access deny")
        return redirect('/home')
    if request.method.__eq__('POST'):
        ten_mon_hoc = request.form.get('ten_mon_hoc')
        thuoc_khoi = request.form.get('thuoc_khoi')
        mo_ta = request.form.get('mo_ta')
        new_mon_hoc = MonHoc(
            tenMonHoc=ten_mon_hoc,
            moTa=mo_ta,
            TrangThai=True,
            thuocKhoi=LoaiKhoi[thuoc_khoi]
        )
        db.session.add(new_mon_hoc)
        db.session.commit()
        flash("Thêm môn học thành công", category='success')
    return render_template('subject_manager.html')


@app.route("/sua_mon_hoc")
def sua_mon_hoc():
    if current_user.user_role != UserRole.QuanTriVien:
        flash("access deny")
        return redirect('/home')
    return flash("Sửa môn học thành công", category='success')


@app.route("/xoa_mon_hoc")
def xoa_mon_hoc():
    if current_user.user_role != UserRole.QuanTriVien:
        flash("access deny")
        return redirect('/home')
    return flash("Xóa môn học thành công", category='success')


@app.route('/get_subject_class_by_grade_block')
def get_subject_class_by_grade_block():
    grade_block_id = request.args.get('grade_block_id')

    # Query for subjects and classes related to the selected grade block
    subjects = db.session.query(MonHoc).join(MonHocKhoi).filter(MonHocKhoi.idKhoi == grade_block_id).all()
    classes = db.session.query(Lop).filter(Lop.thuocKhoi == grade_block_id).all()

    # Prepare data for JSON response
    subjects_data = [{'id': subject.idMonHoc, 'tenMonHoc': subject.tenMonHoc} for subject in subjects]
    classes_data = [{'id': class_obj.idLop, 'tenLop': class_obj.tenLop} for class_obj in classes]

    return jsonify({'subjects': subjects_data, 'classes': classes_data})


@app.route('/get_grades_by_year')
def get_grades_by_year():
    academic_year_id = request.args.get('academic_year_id')

    # Lấy danh sách khối theo niên khóa
    grades = Khoi.query.filter_by(idNienKhoa=academic_year_id).all()
    grades_data = [{'idKhoi': g.idKhoi, 'tenKhoi': g.tenKhoi} for g in grades]

    return jsonify({'grades': grades_data})


@app.route('/get_classes_by_grade')
def get_classes_by_grade():
    grade_id = request.args.get('grade_id')

    # Lấy danh sách lớp theo khối
    classes = Lop.query.filter_by(thuocKhoi=grade_id).all()
    classes_data = [{'idLop': c.idLop, 'tenLop': c.tenLop} for c in classes]

    return jsonify({'classes': classes_data})


@app.route('/students_test', methods=['GET', 'POST'])
def students_1():
    # Querying all available academic years, grades, and classes for the filter options
    academic_years = NienKhoa.query.all()  # Get all academic years
    grades = Khoi.query.all()  # Get all grades
    classes = Lop.query.all()  # Get all classes

    # Get the selected filters from the form
    selected_academic_year = request.args.get('academic_year')
    selected_grade = request.args.get('grade')
    selected_class = request.args.get('class')

    # Build the query based on the selected filters
    query = db.session.query(
        HocSinh.first_name,
        HocSinh.last_name,
        Khoi.tenKhoi,  # Grade info
        Lop.tenLop,  # Class name
        NienKhoa.tenNienKhoa,  # Academic year
    ).join(HocSinhLop, HocSinhLop.idHocSinh == HocSinh.id).join(
        Lop, HocSinhLop.idLop == Lop.idLop).join(
        Khoi, Lop.thuocKhoi == Khoi.idKhoi).join(
        NienKhoa, Khoi.idNienKhoa == NienKhoa.idNienKhoa)  # Join necessary tables

    # Apply filters based on user selection
    if selected_academic_year:
        query = query.filter(NienKhoa.idNienKhoa == selected_academic_year)
    if selected_grade:
        query = query.filter(Khoi.idKhoi == selected_grade)
    if selected_class:
        query = query.filter(Lop.idLop == selected_class)

    # Execute the query
    students_list = query.all()

    # Render the template with the filtered student list and options
    return render_template(
        'danh_sach_hoc_sinh.html',
        students=students_list,
        academic_years=academic_years,
        grades=grades,
        classes=classes,
        selected_academic_year=selected_academic_year,
        selected_grade=selected_grade,
        selected_class=selected_class
    )


# Route hiển thị danh sách cột điểm
@app.route('/cot_diem')
def danh_sach_cot_diem():
    cot_diems = CotDiem.query.all()
    return render_template('danh_sach_cot_diem.html', cot_diems=cot_diems)


# Route xử lý tạo cột điểm
@app.route('/them-cot-diem', methods=['POST'])
def them_cot_diem():
    if request.method == 'POST':
        tenCot = request.form['tenCot']
        heSo = request.form['heSo']
        soCot = request.form['soCot']

        # Tạo đối tượng CotDiem và thêm vào cơ sở dữ liệu
        new_cot = CotDiem(tenCot=tenCot, heSo=heSo, soCot=soCot)
        db.session.add(new_cot)
        db.session.commit()

        # Redirect lại về trang danh sách cột điểm
        return redirect(url_for('danh_sach_cot_diem'))


@app.route('/tao_chi_tiet_cot_diem', methods=['GET', 'POST'])
def tao_chi_tiet_cot_diem():
    if request.method == 'POST':
        idCotDiem = request.form.get('idCotDiem')
        idNienKhoa = request.form.get('idNienKhoa')
        idMonHoc = request.form.get('idMonHoc')

        cot_diem = CotDiem.query.get(idCotDiem)
        nien_khoa = NienKhoa.query.get(idNienKhoa)
        mon_hoc = MonHoc.query.get(idMonHoc)

        if not cot_diem:
            return jsonify({"error": "Cột điểm không tồn tại."}), 400
        if not nien_khoa:
            return jsonify({"error": "Niên khóa không tồn tại."}), 400
        if not mon_hoc:
            return jsonify({"error": "Môn học không tồn tại."}), 400

        chi_tiet_moi = ChiTietCotDiem(
            idCotDiem=idCotDiem,
            idNienKhoa=idNienKhoa,
            idMonHoc=idMonHoc
        )
        try:
            db.session.add(chi_tiet_moi)
            db.session.commit()

            # Tự động tạo số lượng điểm theo số cột của cột điểm
            bang_diem = BangDiem.query.filter_by(
                MaMonHoc=idMonHoc
            ).all()

            for bd in bang_diem:
                hoc_sinh_list = HocSinh.query.join(HocSinhLop).filter_by(idLop=bd.MaLop).all()
                for hs in hoc_sinh_list:
                    for _ in range(cot_diem.soCot):  # Tạo số lượng điểm bằng số cột
                        diem_moi = Diem(
                            idChiTietCotDiem=chi_tiet_moi.idChiTietCotDiem,
                            idHocSinh=hs.id,
                            idBangDiem=bd.idBangDiem,
                            # tối ưu sau
                            soDiem=0
                        )
                        db.session.add(diem_moi)
            db.session.commit()

            return jsonify({"message": "Chi tiết cột điểm và điểm cho học sinh đã được tạo thành công."}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    cot_diem_list = CotDiem.query.all()
    nien_khoa_list = NienKhoa.query.all()
    mon_hoc_list = MonHoc.query.all()
    return render_template('tao_chi_tiet_cot_diem.html', cot_diem_list=cot_diem_list, nien_khoa_list=nien_khoa_list, mon_hoc_list=mon_hoc_list)


@app.route('/nhap_diem', methods=['GET', 'POST'])
def nhap_diem():
    khoi_list = Khoi.query.all()
    mon_hoc_list = MonHoc.query.all()
    lop_list = Lop.query.all()

    if request.method == 'POST':
        idKhoi = request.form.get('idKhoi')
        idMonHoc = request.form.get('idMonHoc')
        idLop = request.form.get('idLop')

        bang_diem = BangDiem.query.filter_by(MaLop=idLop, MaMonHoc=idMonHoc).first()

        if not bang_diem:
            return jsonify({"error": "Không tìm thấy bảng điểm cho lớp này."}), 400

        hoc_sinh_list = HocSinh.query.join(HocSinhLop).filter(HocSinhLop.idLop == idLop).all()
        chi_tiet_cot_diem = ChiTietCotDiem.query.filter_by(idMonHoc=idMonHoc).all()

        return render_template('nhap_diem.html',
                               hoc_sinh_list=hoc_sinh_list,
                               chi_tiet_cot_diem=chi_tiet_cot_diem,
                               bang_diem=bang_diem)

    return render_template('chon_nhap_diem.html', khoi_list=khoi_list, mon_hoc_list=mon_hoc_list, lop_list=lop_list)


@app.route('/luu_diem', methods=['POST'])
def luu_diem():
    for hs in HocSinh.query.all():
        for ct in ChiTietCotDiem.query.all():

            input_name = f"diem_{hs.id}_{ct.idChiTietCotDiem}"
            diem_moi = request.form.get(input_name)

            if diem_moi:
                diem = Diem.query.filter_by(idHocSinh=hs.id, idChiTietCotDiem=ct.idChiTietCotDiem).first()
                if diem:
                    diem.soDiem = float(diem_moi)  # Cập nhật điểm mới
                else:
                    diem = Diem(idHocSinh=hs.id, idChiTietCotDiem=ct.id, soDiem=float(diem_moi))
                    db.session.add(diem)  # Thêm điểm mới nếu chưa có

    db.session.commit()
    return redirect(url_for('nhap_diem'))


@app.route('/quan_ly_bang_diem', methods=['GET', 'POST'])
def quan_ly_bang_diem():
    # Handle the form submission for grade selection
    if request.method == 'POST':
        khoi_id = request.form['khoi']
        mon_hoc_id = request.form['mon_hoc']
        lop_id = request.form['lop']

        # Fetch grade tables based on selected subject and class
        danh_sach_bang_diem = BangDiem.query.filter_by(MaMonHoc=mon_hoc_id, MaLop=lop_id).all()

        # Flash the selected options (Optional)
        selected_khoi = Khoi.query.get(khoi_id)
        selected_mon_hoc = MonHoc.query.get(mon_hoc_id)
        selected_lop = Lop.query.get(lop_id)

        flash(f"Khối: {selected_khoi.tenKhoi}, Môn: {selected_mon_hoc.tenMonHoc}, Lớp: {selected_lop.tenLop}",
              'success')

        return render_template('quan_ly_bang_diem.html', khoi_list=Khoi.query.all(), mon_hoc_list=MonHoc.query.all(),
                               lop_list=Lop.query.all(), dsbd=danh_sach_bang_diem)

    # Fetch all data for the select options
    khoi_list = Khoi.query.all()
    mon_hoc_list = MonHoc.query.all()
    lop_list = Lop.query.all()

    return render_template('quan_ly_bang_diem.html', khoi_list=khoi_list, mon_hoc_list=mon_hoc_list, lop_list=lop_list,
                           dsbd=[])


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')


@app.route("/them_lop")
def them_lop():
    return render_template('addclasses.html')


@app.route("/them_lop_tu_dong", methods=['get', 'post'])
def them_lop_tu_dong():
    if request.method.__eq__('POST'):
        ten_mon_hoc = request.form.get('ten_mon_hoc')
        thuoc_khoi = request.form.get('thuoc_khoi')
        mo_ta = request.form.get('mo_ta')
        new_mon_hoc = MonHoc(
            tenMonHoc=ten_mon_hoc,
            moTa=mo_ta,
            TrangThai=True,
            thuocKhoi=LoaiKhoi[thuoc_khoi]
        )
        db.session.add(new_mon_hoc)
        db.session.commit()
        flash("Thêm môn học thành công", category='success')
    return render_template('subject_manager.html')


@login.user_loader
def load_user(id):
    return Account.query.get(int(id))

#
# @app.route('/tao_bang_diem', methods=['GET', 'POST'])
# def tao_bang_diem():
#     if request.method == 'POST':
#         # Get data from the form
#         ma_mon_hoc = request.form.get('ma_mon_hoc')
#         ma_lop = request.form.get('ma_lop')
#         hoc_ki = request.form.get('hoc_ki')
#         ma_giao_vien = request.form.get('ma_giao_vien')
#
#         # Validate data (you can add more validation as needed)
#         if not ma_mon_hoc or not ma_lop or not hoc_ki or not ma_giao_vien:
#             flash('Vui lòng điền đầy đủ thông tin!', 'danger')
#             return redirect(url_for('tao_bang_diem'))
#         existing_bang_diem = BangDiem.query.filter_by(
#             MaMonHoc=ma_mon_hoc,
#             MaLop=ma_lop,
#             HocKi=HocKi[hoc_ki]
#         ).first()
#         if existing_bang_diem:
#             flash('Bảng điểm này đã tồn tại!', 'danger')
#             return redirect(url_for('tao_bang_diem'))
#         # Create a new BangDiem record
#         bang_diem = BangDiem(
#             MaMonHoc=ma_mon_hoc,
#             MaLop=ma_lop,
#             HocKi=hoc_ki,  # Convert string to enum
#             MaGiaoVien=ma_giao_vien
#         )
#
#         # Add and commit the new record to the database
#         db.session.add(bang_diem)
#         db.session.commit()
#
#         flash('Bảng điểm đã được tạo thành công!', 'success')
#         return redirect(url_for('tao_bang_diem'))
#
#     # Get data for the form (classes, subjects, teachers)
#     mon_hocs = MonHoc.query.all()
#     lops = Lop.query.all()
#     giao_viens = GiaoVien.query.all()
#     hoc_ki_options = HocKi.__members__.items()  # List of enum options for HocKi
#
#     return render_template('tao_bang_diem.html', mon_hocs=mon_hocs, lops=lops, giao_viens=giao_viens,
#                            hoc_ki_options=hoc_ki_options)


@app.route('/tao_bang_diem', methods=['GET', 'POST'])
def tao_bang_diem():
    if request.method == 'POST':
        # Get form data
        khoi_id = request.form.get('khoi')
        mon_hoc_id = request.form.get('mon_hoc')
        lop_id = request.form.get('lop')
        giao_vien_id = request.form.get('giao_vien')
        hoc_ki = request.form.get('hoc_ki')

        # Validate the data
        if not khoi_id or not mon_hoc_id or not lop_id or not giao_vien_id or not hoc_ki:
            flash('Vui lòng điền đầy đủ thông tin!', 'danger')
            return redirect(url_for('tao_bang_diem'))
        existing_bang_diem = BangDiem.query.filter_by(
                        MaMonHoc=mon_hoc_id,
                        MaLop=lop_id,
                        HocKi=HocKi[hoc_ki]
                    ).first()
        if existing_bang_diem:
            flash('Bảng điểm này đã tồn tại!', 'danger')
            return redirect(url_for('tao_bang_diem'))
        bang_diem = BangDiem(
            MaMonHoc=mon_hoc_id,
            MaLop=lop_id,
            HocKi=HocKi[hoc_ki],  # Convert string to enum
            MaGiaoVien=giao_vien_id
        )

        # Add to the database and commit
        try:
            db.session.add(bang_diem)
            db.session.commit()
            flash('Bảng điểm đã được tạo thành công!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')

        return redirect(url_for('tao_bang_diem'))

    # Get data for the form (for GET request)
    khois = Khoi.query.all()  # Assuming Khoi is the grade level model
    giao_viens = GiaoVien.query.all()  # Get all teachers

    return render_template('tao_bang_diem.html', khois=khois, giao_viens=giao_viens)


@app.route('/get_mon_hoc_and_lop/<int:khoi_id>', methods=['GET'])
def get_mon_hoc_and_lop(khoi_id):
    # Fetch subjects and classes based on the selected grade (khối)
    mon_hocs = MonHoc.query.filter_by(thuocKhoi=khoi_id).all()
    lops = Lop.query.filter_by(thuocKhoi=khoi_id).all()

    # Prepare data for response
    mon_hoc_data = [{'idMonHoc': mon_hoc.idMonHoc, 'tenMonHoc': mon_hoc.tenMonHoc} for mon_hoc in mon_hocs]
    lop_data = [{'idLop': lop.idLop, 'tenLop': lop.tenLop} for lop in lops]

    return jsonify({'mon_hocs': mon_hoc_data, 'lops': lop_data})


@app.route('/nhap_1_diem', methods=['GET', 'POST'])
def nhap_diem_1():
    if request.method == 'POST':
        # Lấy thông tin từ form người dùng
        id_hoc_sinh = request.form.get('id_hoc_sinh')
        id_mon_hoc = request.form.get('id_mon_hoc')
        id_cot_diem = request.form.get('id_cot_diem')
        so_diem = float(request.form.get('so_diem'))
        id_bang_diem = request.form.get('id_bang_diem')  # Thêm tham số idBangDiem

        # Kiểm tra xem học sinh, môn học, và cột điểm có tồn tại không
        hoc_sinh = HocSinh.query.get(id_hoc_sinh)
        mon_hoc = MonHoc.query.get(id_mon_hoc)
        cot_diem = CotDiem.query.get(id_cot_diem)
        bang_diem = BangDiem.query.get(id_bang_diem)  # Kiểm tra bảng điểm

        if not hoc_sinh or not mon_hoc or not cot_diem or not bang_diem:
            flash('Thông tin không hợp lệ. Hãy kiểm tra lại dữ liệu nhập vào.', 'error')
            return redirect(url_for('nhap_diem'))

        # Kiểm tra lớp của học sinh thông qua bảng HocSinhLop
        hoc_sinh_lop = HocSinhLop.query.filter_by(idHocSinh=id_hoc_sinh).first()

        if not hoc_sinh_lop:
            flash('Học sinh không thuộc lớp nào.', 'error')
            return redirect(url_for('nhap_diem'))

        # Lấy lớp của học sinh từ bảng HocSinhLop
        id_lop_hoc_sinh = hoc_sinh_lop.idLop

        # Kiểm tra bảng điểm có môn học và lớp học này không
        if bang_diem.MaLop != id_lop_hoc_sinh or bang_diem.MaMonHoc != id_mon_hoc:
            flash('Lớp học hoặc môn học không hợp lệ với bảng điểm. Không thể nhập điểm.', 'error')
            return redirect(url_for('nhap_diem'))

        # Tạo mới bản ghi điểm
        chi_tiet_cot_diem = ChiTietCotDiem.query.filter_by(idCotDiem=id_cot_diem, idMonHoc=id_mon_hoc).first()

        if not chi_tiet_cot_diem:
            flash('Cột điểm cho môn học này không tồn tại.', 'error')
            return redirect(url_for('nhap_diem'))

        # Tạo và lưu bản ghi điểm mới
        diem_moi = Diem(soDiem=so_diem, idHocSinh=id_hoc_sinh, idChiTietCotDiem=chi_tiet_cot_diem.idChiTietCotDiem, idBangDiem=bang_diem.idBangDiem)
        db.session.add(diem_moi)
        db.session.commit()

        flash('Nhập điểm thành công!', 'success')
        return redirect(url_for('nhap_diem'))

    # Hiển thị form nhập điểm
    hoc_sinh_list = HocSinh.query.all()
    mon_hoc_list = MonHoc.query.all()
    cot_diem_list = CotDiem.query.all()
    bang_diem_list = BangDiem.query.all()  # Lấy danh sách bảng điểm

    return render_template('nhap_1_diem.html',
                           hoc_sinh_list=hoc_sinh_list,
                           mon_hoc_list=mon_hoc_list,
                           cot_diem_list=cot_diem_list,
                           bang_diem_list=bang_diem_list)  # Truyền bảng điểm vào form

if __name__ == '__main__':
    app.run(debug=True)
