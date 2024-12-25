import hashlib
from datetime import date
import random
from faker import Faker
from cloudinary.utils import unique
from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey, Boolean, UniqueConstraint, Float
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.testing.suite.test_reflection import users

from QuanLyHocSinh import app, db
from enum import Enum as RoleEnum
from flask_login import UserMixin


class UserRole(RoleEnum):
    QuanTriVien = 1
    NhanVien = 2
    GiaoVien = 3
    HocSinh = 4
    DEFAULT = 5


class LoaiKhoi(RoleEnum):
    Khoi10 = 1
    Khoi11 = 2
    Khoi12 = 3


class LoaiQuyDinh(RoleEnum):
    QDDoTuoi = 1
    QDSiSo = 2
    QDDiem = 3


class HocKi(RoleEnum):
    HocKi1 = 1
    HocKi2 = 2


class QuyDinh(db.Model):
    idQuyDinh = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(Integer, nullable=False)
    ToiThieu = Column(Integer, nullable=False)
    ToiDa = Column(Integer, nullable=False)
    loaiQuyDinh = Column(Enum(LoaiQuyDinh), nullable=False)

    def __str__(self):
        return self.name


class User(db.Model):
    idUser = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    DateBirth = Column(Date, nullable=False)
    PhoneNumber = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)

    account = relationship('Account', back_populates='user', cascade='all, delete-orphan', passive_deletes=True,
                           uselist=False, lazy=True)
    nhan_vien = relationship('NhanVien', back_populates='user', cascade='all, delete-orphan', passive_deletes=True,
                             lazy=True)
    qtv = relationship('QTV', back_populates='user', cascade='all, delete-orphan', passive_deletes=True, lazy=True)
    giao_vien = relationship('GiaoVien', back_populates='user', cascade='all, delete-orphan', passive_deletes=True,
                             lazy=True)
    hoc_sinh = relationship('HocSinh', back_populates='user', cascade='all, delete-orphan', passive_deletes=True,
                            lazy=True)
    type = Column(String(50))  # Cột dùng để phân biệt loại

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }


class Account(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    user_role = Column(Enum(UserRole), default=UserRole.DEFAULT)
    idUser = Column(Integer, ForeignKey('user.idUser'), nullable=False, unique=True)
    user = relationship('User', back_populates='account', passive_deletes=True, uselist=False, lazy=True)

    def __str__(self):
        return self.name


class QTV(User):
    id = Column(Integer, ForeignKey('user.idUser'), primary_key=True)
    donViCongTac = Column(String(255), nullable=False)
    user = relationship('User', back_populates='qtv', passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'qtv',
        'inherit_condition': id == User.idUser
    }


class NhanVien(User):
    id = Column(Integer, ForeignKey('user.idUser'), primary_key=True)
    donViCongTac = Column(String(255), nullable=False)
    user = relationship('User', back_populates='nhan_vien', passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'nhanvien',
        'inherit_condition': id == User.idUser
    }


class GiaoVien(User):
    id = Column(Integer, ForeignKey('user.idUser'), primary_key=True)
    bangCap = Column(String(255), nullable=False)

    user = relationship('User', back_populates='giao_vien', passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'giaovien',
        'inherit_condition': id == User.idUser
    }


class HocSinh(User):
    id = Column(Integer, ForeignKey('user.idUser'), primary_key=True)
    thuocKhoi = Column(Enum(LoaiKhoi), nullable=False)
    user = relationship('User', back_populates='hoc_sinh', passive_deletes=True)
    diem = relationship('Diem', backref='hoc_sinh')
    hocsinh_lop = relationship('HocSinhLop', backref='hoc_sinh', lazy=True)
    __mapper_args__ = {
        'polymorphic_identity': 'hocsinh',
        'inherit_condition': id == User.idUser
    }


class NienKhoa(db.Model):
    idNienKhoa = Column(Integer, primary_key=True, autoincrement=True)
    tenNienKhoa = Column(String(255), nullable=False, unique=True)
    BatDau = Column(Date, nullable=False)
    KetThuc = Column(Date, nullable=False)
    khoi = relationship('Khoi', backref='nien_khoa', lazy=True)
    chi_tiet_cot_diem = relationship('ChiTietCotDiem', back_populates='nien_khoa', lazy=True)


class Khoi(db.Model):
    idKhoi = Column(Integer, primary_key=True, autoincrement=True)
    tenKhoi = Column(Integer, nullable=False)
    khoi = Column(Enum(LoaiKhoi), nullable=False, default=LoaiKhoi.Khoi10)
    idNienKhoa = Column(Integer, ForeignKey('nien_khoa.idNienKhoa'), nullable=False)
    lop = relationship('Lop', backref='khoi', lazy=True)
    monhoc_khoi = relationship('MonHocKhoi', backref='khoi', lazy=True)
    __table_args__ = (
        UniqueConstraint('idNienKhoa', 'khoi', name='unique_Khoi_NienKhoa'),
    )


class Lop(db.Model):
    idLop = Column(Integer, primary_key=True, autoincrement=True)
    tenLop = Column(String(255), nullable=False)
    siSo = Column(Integer, nullable=False)
    thuocKhoi = Column(Integer, ForeignKey('khoi.idKhoi'), nullable=False)
    bangDiem = relationship('BangDiem', backref='lop', lazy=True)
    hocsinh_lop = relationship('HocSinhLop', backref='lop', lazy=True)
    __table_args__ = (
        UniqueConstraint('tenLop', 'thuocKhoi', name='unique_lop_khoi'),
    )


class HocSinhLop(db.Model):
    idHocSinh = Column(Integer, ForeignKey('hoc_sinh.id'), primary_key=True)
    idLop = Column(Integer, ForeignKey('lop.idLop'), primary_key=True)


# học sinh có thể thuộc nhiều khối_niên khóa xử lý sao cho học sinh đó có thế thuộc nhiều 1 khối qua nhiều năm

class MonHoc(db.Model):
    idMonHoc = Column(Integer, primary_key=True, autoincrement=True)
    tenMonHoc = Column(String(255), nullable=False)
    moTa = Column(String(255), nullable=False)
    TrangThai = Column(Boolean, nullable=False)
    thuocKhoi = Column(Enum(LoaiKhoi), nullable=False)
    bangDiem = relationship('BangDiem', backref='mon_hoc', lazy=True)
    monhoc_khoi = relationship('MonHocKhoi', backref='mon_hoc', lazy=True)
    chi_tiet_cot_diem = relationship('ChiTietCotDiem', back_populates='mon_hoc', lazy=True)
    # def __str__(self):
    #     return self.name


class MonHocKhoi(db.Model):
    idMonHoc = Column(Integer, ForeignKey('mon_hoc.idMonHoc'), primary_key=True)
    idKhoi = Column(Integer, ForeignKey('khoi.idKhoi'), primary_key=True)


class BangDiem(db.Model):
    idBangDiem = Column(Integer, primary_key=True, autoincrement=True)
    MaMonHoc = Column(Integer, ForeignKey('mon_hoc.idMonHoc'), nullable=False)  # Liên kết với Môn Học
    MaLop = Column(Integer, ForeignKey('lop.idLop'), nullable=False)  # Liên kết với Lớp Học
    HocKi = Column(Enum(HocKi), nullable=False)
    MaGiaoVien = Column(Integer, ForeignKey('giao_vien.id'), nullable=False)
    __table_args__ = (
        UniqueConstraint('MaLop', 'MaMonHoc', 'HocKi', name='unique_Khoi_NienKhoa'),)
    diem = relationship('Diem', backref='bang_diem')


class CotDiem(db.Model):
    idCot = Column(Integer, primary_key=True, autoincrement=True)
    tenCot = Column(String(20), nullable=False)
    heSo = Column(Integer, nullable=False)
    soCot = Column(Integer, nullable=False)
    chi_tiet_cot_diem = relationship('ChiTietCotDiem', back_populates='cot_diem', lazy=True)


class ChiTietCotDiem(db.Model):
    idChiTietCotDiem = Column(Integer, primary_key=True, autoincrement=True)
    idCotDiem = Column(Integer, ForeignKey('cot_diem.idCot'), nullable=False)
    idMonHoc = Column(Integer, ForeignKey('mon_hoc.idMonHoc'), nullable=False)
    idNienKhoa = Column(Integer, ForeignKey('nien_khoa.idNienKhoa'), nullable=False)
    cot_diem = relationship('CotDiem', back_populates='chi_tiet_cot_diem', lazy=True)
    mon_hoc = relationship('MonHoc', back_populates='chi_tiet_cot_diem', lazy=True)
    nien_khoa = relationship('NienKhoa', back_populates='chi_tiet_cot_diem', lazy=True)

    diem = relationship('Diem', backref='chi_tiet_cot_diem', lazy=True)


class Diem(db.Model):
    idDiem = Column(Integer, primary_key=True, autoincrement=True)
    soDiem = Column(Float, nullable=False)
    idHocSinh = Column(Integer, ForeignKey('hoc_sinh.id'), nullable=False)
    idChiTietCotDiem = Column(Integer, ForeignKey('chi_tiet_cot_diem.idChiTietCotDiem'), nullable=False)
    idBangDiem = Column(Integer, ForeignKey('bang_diem.idBangDiem'), nullable=False)


faker = Faker('vi_VN')

# Danh sách họ, tên đệm, tên phổ biến ở Việt Nam
ho_list = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ"]
ten_dem_list = ["Văn", "Thị", "Minh", "Hữu", "Ngọc", "Anh", "Quang", "Thanh", "Thế", "Thảo"]
ten_list = ["Hùng", "Hoa", "Linh", "Tùng", "Lan", "Hương", "Nam", "Phương", "Kiên", "Hiếu", "Dũng", "Trang"]


# Hàm tạo tên giáo viên
def tao_ten_nguoi_dung(check):
    if check:
        return random.choice(ho_list)
    else:
        return f"{random.choice(ten_dem_list)} {random.choice(ten_list)}"


from math import ceil


def tao_lop_cho_khoi(khoi):
    try:
        # Bước 1: Lấy tất cả học sinh thuộc khối
        hoc_sinh_list = HocSinh.query.filter_by(thuocKhoi=khoi.khoi).all()

        # Bước 2: Tính số lớp cần tạo
        so_luong_hoc_sinh = len(hoc_sinh_list)
        so_lop = ceil(so_luong_hoc_sinh / 30)  # Ví dụ mỗi lớp chứa tối đa 30 học sinh

        # Bước 3: Tạo các lớp
        lop_list = []
        for i in range(so_lop):
            ten_lop = f"Lớp {khoi.idKhoi} - {i + 1}"
            lop = Lop(
                tenLop=ten_lop,
                siSo=0,  # Chưa có học sinh, số lượng sẽ cập nhật sau khi thêm học sinh
                thuocKhoi=khoi.idKhoi,
            )
            lop_list.append(lop)

        # Thêm các lớp vào cơ sở dữ liệu
        db.session.add_all(lop_list)
        db.session.commit()

        # Bước 4: Gán học sinh vào các lớp
        hoc_sinh_idx = 0
        for lop in lop_list:
            so_hoc_sinh_cua_lop = min(30,
                                      so_luong_hoc_sinh - hoc_sinh_idx)  # Đảm bảo không vượt quá số học sinh còn lại
            for _ in range(so_hoc_sinh_cua_lop):
                hoc_sinh = hoc_sinh_list[hoc_sinh_idx]
                hoc_sinh_lop = HocSinhLop(
                    idHocSinh=hoc_sinh.id,
                    idLop=lop.idLop
                )
                db.session.add(hoc_sinh_lop)
                hoc_sinh_idx += 1
                lop.siSo += 1  # Tăng số lượng học sinh trong lớp

        # Cập nhật số học sinh cho mỗi lớp
        db.session.commit()

        return f"Đã tạo {so_lop} lớp cho khối {khoi.idKhoi} và phân phối học sinh vào các lớp."

    except Exception as e:
        db.session.rollback()
        return f"Lỗi khi tạo lớp và phân phối học sinh: {str(e)}"


def tao_20_giao_vien_va_tai_khoan(so_luong=20):
    giao_vien_list = []
    tai_khoan_list = []
    created_emails = set()  # Bộ lưu trữ email để tránh trùng lặp
    created_usernames = set()  # Bộ lưu trữ username để tránh trùng lặp
    created_phone_numbers = set()  # Bộ lưu trữ số điện thoại để tránh trùng lặp

    try:
        for _ in range(so_luong):
            # Tạo thông tin cá nhân
            first_name = tao_ten_nguoi_dung(check=True)
            last_name = tao_ten_nguoi_dung(check=False)
            bang_cap = random.choice(["Cử nhân Sư phạm", "Thạc sĩ Giáo dục", "Tiến sĩ Giáo dục"])

            # Tạo email duy nhất
            email = faker.email()
            while email in created_emails or User.query.filter_by(email=email).first():
                email = faker.email()
            created_emails.add(email)

            # Tạo số điện thoại duy nhất
            phone = faker.phone_number()
            while phone in created_phone_numbers or User.query.filter_by(PhoneNumber=phone).first():
                phone = faker.phone_number()
            created_phone_numbers.add(phone)

            # Tạo giáo viên
            giao_vien = GiaoVien(
                first_name=first_name,
                last_name=last_name,
                DateBirth=faker.date_of_birth(minimum_age=25, maximum_age=60),
                PhoneNumber=phone,
                email=email,
                bangCap=bang_cap,
            )
            giao_vien_list.append(giao_vien)

            # Tạo username duy nhất
            base_username = f"{first_name.lower()}.{last_name.split()[-1].lower()}"
            username = f"{base_username}{random.randint(100, 999)}"
            while username in created_usernames or Account.query.filter_by(username=username).first():
                username = f"{base_username}{random.randint(100, 999)}"
            created_usernames.add(username)

            # Hash mật khẩu
            password = hashlib.md5("123".encode('utf-8')).hexdigest()

            # Tạo tài khoản
            tai_khoan = Account(
                name=f"{first_name} {last_name}",
                username=username,
                password=password,
                status=True,
                user_role=UserRole.GiaoVien,  # Vai trò giáo viên
                user=giao_vien,  # Liên kết tài khoản với giáo viên
            )
            tai_khoan_list.append(tai_khoan)

        # Lưu vào cơ sở dữ liệu
        db.session.add_all(giao_vien_list)
        db.session.add_all(tai_khoan_list)
        db.session.commit()

        return f"Đã tạo thành công {so_luong} giáo viên kèm tài khoản."

    except Exception as e:
        db.session.rollback()
        return f"Lỗi khi tạo giáo viên và tài khoản: {str(e)}"


def tao_ngau_nhien_hoc_sinh_va_tai_khoan(so_luong):
    hoc_sinh_list = []
    tai_khoan_list_2 = []
    created_emails = set()  # Bộ lưu trữ email để tránh trùng lặp
    created_phones = set()
    created_usernames = set()

    for _ in range(so_luong):
        # Tạo thông tin cá nhân
        first_name = tao_ten_nguoi_dung(check=True)
        last_name = tao_ten_nguoi_dung(check=False)
        email = faker.unique.email()
        phone = faker.unique.phone_number()
        khoi = random.choice(["Khoi10", "Khoi11", "Khoi12"])

        while email in created_emails or User.query.filter_by(email=email).first():
            email = faker.unique.email()
        created_emails.add(email)

        phone = faker.phone_number()
        while phone in created_phones or User.query.filter_by(PhoneNumber=phone).first():
            phone = faker.phone_number()
        created_phones.add(phone)

        base_username = f"{first_name.lower()}.{last_name.split()[-1].lower()}"
        username = f"{base_username}{random.randint(100, 9999)}"
        while username in created_usernames or Account.query.filter_by(username=username).first():
            username = f"{base_username}{random.randint(100, 9999)}"
        created_usernames.add(username)
        # Tạo học sinh
        hoc_sinh = HocSinh(
            first_name=first_name,
            last_name=last_name,
            DateBirth=faker.date_of_birth(minimum_age=15, maximum_age=18),  # Độ tuổi học sinh cấp 3
            PhoneNumber=phone,
            email=email,
            thuocKhoi=LoaiKhoi[khoi]
        )
        hoc_sinh_list.append(hoc_sinh)
        password = str(hashlib.md5("123".encode('utf-8')).hexdigest()),
        tai_khoan = Account(
            name=f"{first_name} {last_name}",
            username=username,
            password=password,
            status=True,
            user_role=UserRole.HocSinh,  # Vai trò giáo viên
            user=hoc_sinh,  # Liên kết tài khoản với giáo viên
        )
        tai_khoan_list_2.append(tai_khoan)

        # Lưu vào cơ sở dữ liệu
    try:
        db.session.add_all(hoc_sinh_list)
        db.session.add_all(tai_khoan_list_2)
        db.session.commit()
        return f"Đã tạo thành công {so_luong} học sinh ngẫu nhiên."
    except Exception as e:
        db.session.rollback()
        return f"Lỗi khi tạo học sinh: {str(e)}"


def tao_mon_hoc_theo_khoi(ten_mon_hoc, mo_ta, trang_thai, loai_khoi, id_khoi):
    # Tạo môn học mới
    mon_hoc_moi = MonHoc(
        tenMonHoc=ten_mon_hoc,
        moTa=mo_ta,
        TrangThai=trang_thai,
        thuocKhoi=loai_khoi
    )
    db.session.add(mon_hoc_moi)
    db.session.flush()  # Đảm bảo idMonHoc được tạo ra ngay

    # Tạo mối quan hệ môn học và khối
    mon_hoc_khoi_moi = MonHocKhoi(
        idMonHoc=mon_hoc_moi.idMonHoc,
        idKhoi=id_khoi
    )
    db.session.add(mon_hoc_khoi_moi)

    try:
        db.session.commit()
        print(f"Tạo môn học '{ten_mon_hoc}' cho khối {loai_khoi.name} thành công!")
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi tạo môn học: {e}")
        raise


def tao_chi_tiet_cot_diem(id_cot_diem, id_mon_hoc, id_nien_khoa):
    # Kiểm tra sự tồn tại của CotDiem
    cot_diem = CotDiem.query.filter_by(idCot=id_cot_diem).first()
    mon_hoc = MonHoc.query.filter_by(idMonHoc=id_mon_hoc).first()
    nien_khoa = NienKhoa.query.filter_by(idNienKhoa=id_nien_khoa).first()
    if not cot_diem:
        return {"message": "Không tìm thấy Cột Điểm."}

    # Tạo instance mới của ChiTietCotDiem
    chi_tiet_moi = ChiTietCotDiem(
        idCotDiem=cot_diem.idCot,
        idMonHoc=mon_hoc.idMonHoc,
        idNienKhoa=nien_khoa.idNienKhoa,
    )

    try:
        # Chỉ thêm chiTietCotDiem, không cần thêm CotDiem vào session
        db.session.add(chi_tiet_moi)
        db.session.commit()
        return {"message": "Thêm Chi Tiết Cột Điểm thành công.", "idChiTietCotDiem": chi_tiet_moi.idChiTietCotDiem}
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}


def tao_bang_diem(ma_mon_hoc, ma_lop, hoc_ki, ma_giao_vien):
    # Tạo đối tượng BangDiem
    if hoc_ki == 1:
        hoc_ki_enum = HocKi.HocKi1
    elif hoc_ki == 2:
        hoc_ki_enum = HocKi.HocKi2
    else:
        raise ValueError("Học kỳ không hợp lệ. Chỉ chấp nhận 1 hoặc 2.")

    bang_diem = BangDiem(
        MaMonHoc=ma_mon_hoc,
        MaLop=ma_lop,
        HocKi=hoc_ki_enum,
        MaGiaoVien=ma_giao_vien
    )

    # Thêm vào session và commit
    db.session.add(bang_diem)
    db.session.commit()


def tao_bang_diem_cho_lop_theo_mon(id_lop, id_giao_vien, danh_sach_mon_hoc, hoc_ki):
    """
    Tạo bảng điểm cho một lớp theo từng môn học và phân công giáo viên quản lý.

    :param id_lop: ID của lớp
    :param id_giao_vien: ID của giáo viên quản lý bảng điểm
    :param danh_sach_mon_hoc: Danh sách các môn học cần tạo bảng điểm
    :param hoc_ki: Học kỳ cho bảng điểm
    """
    if hoc_ki == 1:
        hoc_ki_enum = HocKi.HocKi1
    elif hoc_ki == 2:
        hoc_ki_enum = HocKi.HocKi2
    else:
        raise ValueError("Học kỳ không hợp lệ. Chỉ chấp nhận 1 hoặc 2.")

    try:
        # Tạo bảng điểm cho từng môn học
        for mon_hoc in danh_sach_mon_hoc:
            # Kiểm tra bảng điểm đã tồn tại chưa
            bang_diem_ton_tai = db.session.query(BangDiem).filter_by(
                MaLop=id_lop,
                MaMonHoc=mon_hoc['idMonHoc'],
                HocKi=hoc_ki
            ).first()

            if bang_diem_ton_tai:
                print(f"Bảng điểm đã tồn tại cho môn học {mon_hoc['idMonHoc']} - Không tạo lại.")
                continue

            bang_diem_moi = BangDiem(
                MaLop=id_lop,
                MaMonHoc=mon_hoc['idMonHoc'],
                HocKi=hoc_ki,
                MaGiaoVien=id_giao_vien
            )
            db.session.add(bang_diem_moi)

        db.session.commit()
        print("Tạo bảng điểm thành công cho lớp!")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Lỗi khi tạo bảng điểm: {str(e)}")


def tao_diem(so_diem, id_hoc_sinh, id_chi_tiet_cot_diem, id_bang_diem):
    # Tạo đối tượng Diem mới
    diem_moi = Diem(
        soDiem=so_diem,
        idHocSinh=id_hoc_sinh,
        idChiTietCotDiem=id_chi_tiet_cot_diem,
        idBangDiem=id_bang_diem
    )

    # Thêm đối tượng vào phiên
    db.session.add(diem_moi)

    # Thực hiện commit để lưu vào cơ sở dữ liệu
    db.session.commit()

    # Refresh đối tượng để đảm bảo dữ liệu mới nhất được load
    db.session.refresh(diem_moi)

    return diem_moi


def tao_chi_tiet_cot_diem(id_mon_hoc, id_nien_khoa, danh_sach_id_cot_diem):
    try:
        # Kiểm tra sự tồn tại của MonHoc và NienKhoa
        mon_hoc = db.session.query(MonHoc).filter_by(idMonHoc=id_mon_hoc).first()
        nien_khoa = db.session.query(NienKhoa).filter_by(idNienKhoa=id_nien_khoa).first()

        if not mon_hoc:
            raise ValueError("Môn học không tồn tại")

        if not nien_khoa:
            raise ValueError("Niên khóa không tồn tại")

        # Tạo danh sách chi tiết cột điểm
        chi_tiet_cot_diem_list = []
        for id_cot_diem in danh_sach_id_cot_diem:
            chi_tiet = ChiTietCotDiem(
                idCotDiem=id_cot_diem,
                idMonHoc=id_mon_hoc,
                idNienKhoa=id_nien_khoa
            )
            chi_tiet_cot_diem_list.append(chi_tiet)

        # Thêm vào session và commit
        db.session.add_all(chi_tiet_cot_diem_list)
        db.session.commit()
        print("Tạo chi tiết cột điểm thành công!")
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi: {e}")
    finally:
        db.session.close()


def tao_nhieu_diem_1(id_hoc_sinh, id_bang_diem, id_cot_diem, diem_list):
    """
    Tạo nhiều điểm cho một cột điểm và bảng điểm cụ thể.

    :param session: phiên làm việc SQLAlchemy
    :param id_bang_diem: ID của bảng điểm
    :param id_cot_diem: ID của cột điểm
    :param diem_list: Danh sách điểm dạng [{'id_hoc_sinh': 1, 'so_diem': 9.5}, {'id_hoc_sinh': 2, 'so_diem': 8.0}, ...]
    """
    try:
        # Lấy thông tin lớp của học sinh
        hoc_sinh_lop = db.session.query(HocSinhLop).filter_by(idHocSinh=id_hoc_sinh).first()
        if not hoc_sinh_lop:
            raise ValueError("Học sinh không tồn tại trong lớp nào!")

        # Lấy thông tin lớp từ bảng điểm
        bang_diem = db.session.query(BangDiem).filter_by(idBangDiem=id_bang_diem).first()
        if not bang_diem:
            raise ValueError("Bảng điểm không tồn tại!")

        # Kiểm tra sự khớp lớp giữa học sinh và bảng điểm
        if hoc_sinh_lop.idLop != bang_diem.MaLop:
            raise ValueError("Học sinh không thuộc lớp của bảng điểm này!")
        # Lấy id chi tiết cột điểm tương ứng
        chi_tiet_cot_diem = db.session.query(ChiTietCotDiem).filter_by(
            idCotDiem=id_cot_diem
        ).first()

        if not chi_tiet_cot_diem:
            raise ValueError("Chi tiết cột điểm không tồn tại!")

        id_chi_tiet_cot_diem = chi_tiet_cot_diem.idChiTietCotDiem

        # Tạo danh sách các đối tượng Diem
        for i, so_diem in enumerate(diem_list):
            diem_moi = tao_diem(
                so_diem=so_diem,
                id_hoc_sinh=id_hoc_sinh,
                id_chi_tiet_cot_diem=id_chi_tiet_cot_diem,
                id_bang_diem=id_bang_diem
            )
            db.session.add(diem_moi)
        # Thêm vào phiên làm việc
        db.session.commit()
        print("Tạo điểm thành công!")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Lỗi khi tạo điểm: {str(e)}")
    except ValueError as e:
        print(str(e))


def tao_nhieu_diem(id_hoc_sinh, id_bang_diem, id_cot_diem, so_diem):
    """
    Tạo một điểm cho một cột điểm và bảng điểm cụ thể.

    :param session: phiên làm việc SQLAlchemy
    :param id_bang_diem: ID của bảng điểm
    :param id_cot_diem: ID của cột điểm
    :param so_diem: Điểm cần thêm cho học sinh
    """
    try:
        # Lấy thông tin lớp của học sinh
        hoc_sinh_lop = db.session.query(HocSinhLop).filter_by(idHocSinh=id_hoc_sinh).first()
        if not hoc_sinh_lop:
            raise ValueError("Học sinh không tồn tại trong lớp nào!")

        # Lấy thông tin lớp từ bảng điểm
        bang_diem = db.session.query(BangDiem).filter_by(idBangDiem=id_bang_diem).first()
        if not bang_diem:
            raise ValueError("Bảng điểm không tồn tại!")

        # Kiểm tra sự khớp lớp giữa học sinh và bảng điểm
        if hoc_sinh_lop.idLop != bang_diem.MaLop:
            raise ValueError("Học sinh không thuộc lớp của bảng điểm này!")

        # Lấy chi tiết cột điểm từ cột điểm
        cot_diem = db.session.query(CotDiem).filter_by(idCot=id_cot_diem).first()
        if not cot_diem:
            raise ValueError("Cột điểm không tồn tại!")

        # Lấy chi tiết cột điểm đầu tiên từ cột điểm
        chi_tiet_cot_diem = db.session.query(ChiTietCotDiem).filter_by(idCotDiem=cot_diem.idCot).first()
        if not chi_tiet_cot_diem:
            raise ValueError("Không tìm thấy chi tiết cột điểm!")

        # Kiểm tra số lượng điểm hiện tại của học sinh
        so_diem_da_co = db.session.query(Diem).filter_by(
            idHocSinh=id_hoc_sinh,
            idChiTietCotDiem=chi_tiet_cot_diem.idChiTietCotDiem,
            idBangDiem=id_bang_diem
        ).count()

        # Nếu học sinh đã có đủ số điểm, không cho nhập thêm
        if so_diem_da_co >= cot_diem.soCot:
            raise ValueError("Học sinh đã có đủ điểm trong cột điểm này!")

        # Tạo đối tượng Diem mới
        diem_moi = tao_diem(
            so_diem=so_diem,
            id_hoc_sinh=id_hoc_sinh,
            id_chi_tiet_cot_diem=chi_tiet_cot_diem.idChiTietCotDiem,
            id_bang_diem=id_bang_diem
        )
        db.session.add(diem_moi)

        # Thêm vào phiên làm việc
        db.session.commit()
        print("Tạo điểm thành công!")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Lỗi khi tạo điểm: {str(e)}")
    except ValueError as e:
        print(str(e))


def create_bang_diem_for_class(class_id, hoc_ki, nien_khoa_id):
    # Lấy lớp học từ database
    lop = Lop.query.filter(Lop.idLop == class_id).first()
    if not lop:
        print("Lớp không tồn tại!")
        return

    # Lấy khối của lớp
    khoi_lop = lop.khoi  # Lớp thuộc khối nào (idKhoi trong Lop)

    # Lấy danh sách môn học của lớp theo khối
    mon_hocs = db.session.query(MonHoc).join(MonHocKhoi).filter(
        MonHocKhoi.idKhoi == lop.thuocKhoi).all()

    # Duyệt qua các môn học và tạo bảng điểm cho mỗi môn
    for mon_hoc in mon_hocs:
        # Kiểm tra nếu môn học không thuộc khối của lớp thì bỏ qua
        mon_hoc_khoi = MonHocKhoi.query.filter(
            MonHocKhoi.idMonHoc == mon_hoc.idMonHoc,
            MonHocKhoi.idKhoi == lop.thuocKhoi
        ).first()

        if not mon_hoc_khoi:
            print(f"Môn học {mon_hoc.tenMonHoc} không thuộc khối {lop.khoi}.")
            continue

        # Kiểm tra nếu bảng điểm cho môn học, lớp và học kỳ đó đã tồn tại
        existing_bang_diem = BangDiem.query.filter(
            BangDiem.MaLop == lop.idLop,
            BangDiem.MaMonHoc == mon_hoc.idMonHoc,
            BangDiem.HocKi == hoc_ki
        ).first()

        if existing_bang_diem:
            print(f"Bảng điểm cho lớp {lop.tenLop} môn {mon_hoc.tenMonHoc} học kỳ {hoc_ki} đã tồn tại.")
            continue

        # Lấy giáo viên để phân công quản lý bảng điểm (ví dụ chọn giáo viên đầu tiên)
        giao_vien = db.session.query(GiaoVien).first()  # Lấy giáo viên đầu tiên (hoặc tùy chọn theo logic khác)
        if not giao_vien:
            print(f"Không có giáo viên nào để phân công cho bảng điểm môn {mon_hoc.tenMonHoc}.")
            continue

        # Tạo bản ghi bảng điểm
        bang_diem = BangDiem(
            MaMonHoc=mon_hoc.idMonHoc,
            MaLop=lop.idLop,
            HocKi=hoc_ki,
            MaGiaoVien=giao_vien.id
        )

        # Lưu bảng điểm vào database
        db.session.add(bang_diem)
        db.session.commit()
        print(f"Tạo bảng điểm cho lớp {lop.tenLop} môn {mon_hoc.tenMonHoc} thành công.")


# Ví dụ gọi hàm để tạo bảng điểm cho lớp có id = 1, học kỳ = 1, niên khóa id = 2024

def tao_nhieu_chi_tiet_cot_diem(id_mon_hoc, id_nien_khoa, danh_sach_id_cot_diem):
    # Kiểm tra sự tồn tại của MonHoc và NienKhoa
    mon_hoc = MonHoc.query.filter_by(idMonHoc=id_mon_hoc).first()
    nien_khoa = NienKhoa.query.filter_by(idNienKhoa=id_nien_khoa).first()

    if not mon_hoc:
        return {"message": "Không tìm thấy Môn Học."}

    if not nien_khoa:
        return {"message": "Không tìm thấy Niên Khóa."}

    # Tạo danh sách chi tiết cột điểm
    chi_tiet_moi_list = []
    for id_cot_diem in danh_sach_id_cot_diem:
        cot_diem = CotDiem.query.filter_by(idCot=id_cot_diem).first()
        if not cot_diem:
            return {"message": f"Không tìm thấy Cột Điểm với id {id_cot_diem}."}

        # Tạo instance mới của ChiTietCotDiem
        chi_tiet_moi = ChiTietCotDiem(
            idCotDiem=cot_diem.idCot,
            idMonHoc=mon_hoc.idMonHoc,
            idNienKhoa=nien_khoa.idNienKhoa,
        )
        chi_tiet_moi_list.append(chi_tiet_moi)

    try:
        # Thêm tất cả chiTietCotDiem vào session và commit
        db.session.add_all(chi_tiet_moi_list)
        db.session.commit()
        return {"message": "Thêm nhiều Chi Tiết Cột Điểm thành công."}
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}


def tao_nhieu_chi_tiet_cot_diem123(list_id_cot_diem, id_khoi, id_nien_khoa):
    # Kiểm tra sự tồn tại của Niên Khóa
    nien_khoa = NienKhoa.query.filter_by(idNienKhoa=id_nien_khoa).first()
    if not nien_khoa:
        return {"message": "Không tìm thấy Niên Khóa."}

    # Lấy danh sách môn học thuộc khối
    mon_hoc_list = MonHoc.query.filter_by(thuocKhoi=id_khoi).all()
    if not mon_hoc_list:
        return {"message": "Không có môn học nào thuộc khối này."}

    chi_tiet_list = []

    try:
        for id_cot_diem in list_id_cot_diem:
            cot_diem = CotDiem.query.filter_by(idCot=id_cot_diem).first()
            if not cot_diem:
                continue

            for mon_hoc in mon_hoc_list:
                # Kiểm tra nếu chi tiết cột điểm đã tồn tại
                chi_tiet_ton_tai = ChiTietCotDiem.query.filter_by(
                    idCotDiem=cot_diem.idCot,
                    idMonHoc=mon_hoc.idMonHoc,
                    idNienKhoa=nien_khoa.idNienKhoa
                ).first()

                if chi_tiet_ton_tai:
                    continue

                chi_tiet_moi = ChiTietCotDiem(
                    idCotDiem=cot_diem.idCot,
                    idMonHoc=mon_hoc.idMonHoc,
                    idNienKhoa=nien_khoa.idNienKhoa,
                )
                db.session.add(chi_tiet_moi)
                chi_tiet_list.append(chi_tiet_moi)

        db.session.commit()
        return {
            "message": "Thêm Chi Tiết Cột Điểm cho các môn học thành công.",
            "chiTietCotDiemList": [ct.idChiTietCotDiem for ct in chi_tiet_list]
        }
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}


if __name__ == '__main__':
    with app.app_context():
        # user= User.query.filter_by(idUser = 9).first()
        # db.session.delete(user)  # Xóa bản ghi
        # db.session.commit()
        # db.drop_all()
        # db.create_all()

        # lop = Lop.query.filter_by(idLop=1).first()
        # print(lop.khoi.nien_khoa.tenNienKhoa)

        # admin_user = QTV(
        #     first_name="Nguyen",
        #     last_name="Admin",
        #     DateBirth=date(1990, 1, 1),
        #     PhoneNumber="0123456789",
        #     email="hehee",
        #     donViCongTac="Phòng CNTT"
        # )
        #
        # admin_account = Account(
        #     name="Nguyen Admin he",
        #     username="admin",
        #     password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),  # Hash mật khẩu để bảo mật
        #     user_role=UserRole.QuanTriVien,  # Vai trò quản trị viên
        #     status=True,
        #     user= admin_user # Liên kết với đối tượng QTV
        # )
        # db.session.add(admin_user)
        # db.session.add(admin_account)
        # db.session.commit()

        # result = tao_ngau_nhien_hoc_sinh_va_tai_khoan(so_luong=200)
        # print(result)
        # result = tao_20_giao_vien_va_tai_khoan(20)
        # print(result)

        # print(tao_lop_cho_khoi(Khoi.query.filter_by(idKhoi=3).first()))
        # so_luong_hoc_sinh = HocSinh.query.filter_by(thuocKhoi = "Khoi10").count()
        # print(so_luong_hoc_sinh)
        # new_nien_khoa = NienKhoa(
        #     tenNienKhoa="Niên Khóa 2022-2023",
        #     BatDau=date(2021, 8, 21),
        #     KetThuc=date(2022, 6, 15)
        # )
        # print(tao_lop_cho_khoi(Khoi.query.filter_by(idKhoi=3).first()))
        #
        # # Thêm vào database
        # db.session.add(new_nien_khoa)
        # db.session.commit()
        # khoi_10 = Khoi(tenKhoi=10, khoi=LoaiKhoi.Khoi10, idNienKhoa=1)
        # khoi_11 = Khoi(tenKhoi=11, khoi=LoaiKhoi.Khoi11, idNienKhoa=1)
        # khoi_12 = Khoi(tenKhoi=12, khoi=LoaiKhoi.Khoi12, idNienKhoa=1)
        # db.session.add_all([khoi_10, khoi_11, khoi_12])
        # db.session.commit()
        # khoi = Khoi.query.filter_by(idKhoi=1).first()
        # print(khoi.ni)
        # nv = NhanVien(
        #     first_name="Nguyen",
        #     last_name="Admin",
        #     DateBirth=date(1990, 1, 1),
        #     PhoneNumber="23123123",
        #     email="123@domain.com",
        #     donViCongTac="Phòng CNTT"
        # )
        # employee_account= Account(
        #     name="Nguyen Admin he",
        #     username="employee",
        #     password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),  # Hash mật khẩu để bảo mật
        #     user_role=UserRole.NhanVien,  # Vai trò quản trị viên
        #     status=True,
        #     user=nv  # Liên kết với đối tượng QTV
        # )
        # db.session.add(nv)
        # db.session.add(employee_account)
        # db.session.commit()

        # danh_sach_mon_hoc = [
        #     # Khối 10
        #     {"ten_mon_hoc": "Toán", "mo_ta": "Toán học cơ bản", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi10,
        #      "id_khoi": 1},
        #     {"ten_mon_hoc": "Văn", "mo_ta": "Ngữ văn", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi10, "id_khoi": 1},
        #     {"ten_mon_hoc": "Anh", "mo_ta": "Tiếng Anh cơ bản", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi10,
        #      "id_khoi": 1},
        #     {"ten_mon_hoc": "Lý", "mo_ta": "Vật lý đại cương", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi10,
        #      "id_khoi": 1},
        #     {"ten_mon_hoc": "Hóa", "mo_ta": "Hóa học cơ bản", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi10,
        #      "id_khoi": 1},
        #     {"ten_mon_hoc": "Sinh", "mo_ta": "Sinh học tổng quát", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi10,
        #      "id_khoi": 1},
        #     {"ten_mon_hoc": "Sử", "mo_ta": "Lịch sử Việt Nam", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi10,
        #      "id_khoi": 1},
        #     {"ten_mon_hoc": "Địa", "mo_ta": "Địa lý tự nhiên", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi10,
        #      "id_khoi": 1},
        #     {"ten_mon_hoc": "GDCD", "mo_ta": "Giáo dục công dân", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi10,
        #      "id_khoi": 1},
        #     {"ten_mon_hoc": "Tin", "mo_ta": "Tin học cơ bản", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi10,
        #      "id_khoi": 1},
        #     {"ten_mon_hoc": "Thể dục", "mo_ta": "Giáo dục thể chất", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi10,
        #      "id_khoi": 1},
        #     {"ten_mon_hoc": "Công nghệ", "mo_ta": "Kỹ thuật công nghiệp", "trang_thai": True,
        #      "loai_khoi": LoaiKhoi.Khoi10, "id_khoi": 1},
        #
        #     # Khối 11
        #     {"ten_mon_hoc": "Toán", "mo_ta": "Toán học nâng cao", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi11,
        #      "id_khoi": 2},
        #     {"ten_mon_hoc": "Văn", "mo_ta": "Ngữ văn sáng tác", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi11,
        #      "id_khoi": 2},
        #     {"ten_mon_hoc": "Anh", "mo_ta": "Tiếng Anh giao tiếp", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi11,
        #      "id_khoi": 2},
        #     {"ten_mon_hoc": "Lý", "mo_ta": "Cơ học", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi11, "id_khoi": 2},
        #     {"ten_mon_hoc": "Hóa", "mo_ta": "Hóa vô cơ", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi11,
        #      "id_khoi": 2},
        #     {"ten_mon_hoc": "Sinh", "mo_ta": "Di truyền học", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi11,
        #      "id_khoi": 2},
        #     {"ten_mon_hoc": "Sử", "mo_ta": "Lịch sử thế giới", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi11,
        #      "id_khoi": 2},
        #     {"ten_mon_hoc": "Địa", "mo_ta": "Địa lý kinh tế", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi11,
        #      "id_khoi": 2},
        #     {"ten_mon_hoc": "GDCD", "mo_ta": "Luật và xã hội", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi11,
        #      "id_khoi": 2},
        #     {"ten_mon_hoc": "Tin", "mo_ta": "Lập trình cơ bản", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi11,
        #      "id_khoi": 2},
        #     {"ten_mon_hoc": "Thể dục", "mo_ta": "Giáo dục thể chất", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi11,
        #      "id_khoi": 2},
        #     {"ten_mon_hoc": "Công nghệ", "mo_ta": "Kỹ thuật điện tử", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi11,
        #      "id_khoi": 2},
        #
        #     # Khối 12
        #     {"ten_mon_hoc": "Toán", "mo_ta": "Giải tích", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi12,
        #      "id_khoi": 3},
        #     {"ten_mon_hoc": "Văn", "mo_ta": "Ngữ văn nghị luận", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi12,
        #      "id_khoi": 3},
        #     {"ten_mon_hoc": "Anh", "mo_ta": "Tiếng Anh nâng cao", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi12,
        #      "id_khoi": 3},
        #     {"ten_mon_hoc": "Lý", "mo_ta": "Điện từ", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi12, "id_khoi": 3},
        #     {"ten_mon_hoc": "Hóa", "mo_ta": "Hóa hữu cơ", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi12,
        #      "id_khoi": 3},
        #     {"ten_mon_hoc": "Sinh", "mo_ta": "Sinh học phân tử", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi12,
        #      "id_khoi": 3},
        #     {"ten_mon_hoc": "Sử", "mo_ta": "Lịch sử hiện đại", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi12,
        #      "id_khoi": 3},
        #     {"ten_mon_hoc": "Địa", "mo_ta": "Địa lý chính trị", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi12,
        #      "id_khoi": 3},
        #     {"ten_mon_hoc": "GDCD", "mo_ta": "Kinh tế và pháp luật", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi12,
        #      "id_khoi": 3},
        #     {"ten_mon_hoc": "Tin", "mo_ta": "Khoa học máy tính", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi12,
        #      "id_khoi": 3},
        #     {"ten_mon_hoc": "Thể dục", "mo_ta": "Thể thao nâng cao", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi12,
        #      "id_khoi": 3},
        #     {"ten_mon_hoc": "Công nghệ", "mo_ta": "Kỹ thuật cơ khí", "trang_thai": True, "loai_khoi": LoaiKhoi.Khoi12,
        #      "id_khoi": 3}
        # ]
        # for mon in danh_sach_mon_hoc:
        #     tao_mon_hoc_theo_khoi(
        #         mon["ten_mon_hoc"],
        #         mon["mo_ta"],
        #         mon["trang_thai"],
        #         mon["loai_khoi"],
        #         mon["id_khoi"]
        #     )
        # example_data = [
        #     {"tenCot": "1 tiết", "heSo": 2, "soCot": 5},
        #     {"tenCot": "Cuối kì", "heSo": 3, "soCot": 4},
        #     {"tenCot": "15 phút", "heSo": 1, "soCot": 6},
        # ]
        # cot_diem_1 = CotDiem(tenCot="Điểm giữa kỳ", heSo=2, soCot=1)
        # cot_diem_2 = CotDiem(tenCot="Điểm cuối kỳ", heSo=3, soCot=2)
        # cot_diem_3 = CotDiem(tenCot="Điểm bài tập", heSo=1, soCot=3)
        #
        # # Thêm các cột điểm vào cơ sở dữ liệu
        # db.session.add(cot_diem_1)
        # db.session.add(cot_diem_2)
        # db.session.add(cot_diem_3)
        # db.session.commit()

        # tao_chi_tiet_cot_diem()

        # print(tao_chi_tiet_cot_diem(id_cot_diem=1, id_mon_hoc=1, id_nien_khoa=1))

        # print(tao_bang_diem(ma_mon_hoc=2, ma_lop=1, hoc_ki=1, ma_giao_vien=202))

        # print(tao_diem(so_diem=5,id_hoc_sinh=1,id_chi_tiet_cot_diem=1,id_bang_diem=5))

        # tạo nhiều chi tiết cột điểm
        # danh_sach_id_cot_diem1=[1,2,3]
        # print(tao_chi_tiet_cot_diem(id_mon_hoc=1, id_nien_khoa=1, danh_sach_id_cot_diem=danh_sach_id_cot_diem1))

        # tạo nhiều điểm cho cột điểm và bảng điểm
        # diem_list1=[4]
        # print(tao_nhieu_diem(id_hoc_sinh=9,id_bang_diem=5, id_cot_diem=1, so_diem = 10))
        # print(HocSinhLop.query.count())

        # print(create_bang_diem_for_class(class_id=1, hoc_ki=HocKi.HocKi1, nien_khoa_id=1))
        # danh_sach_id_cot_diem1 = [1, 2, 3]
        # print(tao_nhieu_chi_tiet_cot_diem(id_mon_hoc=1, id_nien_khoa=1, danh_sach_id_cot_diem=danh_sach_id_cot_diem1))

        # hoc_sinh = HocSinh.query.filter_by(id = 2).first()
        # print(hoc_sinh.diem[1].idDiem)
        # cotDiem = CotDiem(
        #     tenCot="thuyết trình",
        #     heSo=1,
        #     soCot=3
        # )
        # # Thêm đối tượng CotDiem vào cơ sở dữ liệu
        # db.session.add(cotDiem)
        #
        # # Tạo đối tượng ChiTietCotDiem, sử dụng đối tượng MonHoc, NienKhoa, và CotDiem
        # chiTietCotDiem = ChiTietCotDiem(
        #     mon_hoc=MonHoc.query.filter_by(idMonHoc=1).first(),  # Truy vấn đối tượng MonHoc
        #     nien_khoa=NienKhoa.query.filter_by(idNienKhoa=3).first(),  # Truy vấn đối tượng NienKhoa
        #     idCotDiem=cotDiem.idCot  # Truyền đối tượng CotDiem vào
        # )
        #
        # # Thêm đối tượng ChiTietCotDiem vào cơ sở dữ liệu
        # db.session.add(chiTietCotDiem)
        #
        # # Commit các thay đổi vào cơ sở dữ liệu
        # db.session.commit()
        # bang_diem = BangDiem.query.filter_by(idBangDiem = 15).first()
        # print(bang_diem.mon_hoc.idMonHoc)
        # cot_diem = CotDiem.query.all()
        # for _ in cot_diem:
        #     print(_.idCot)

        db.session.query(ChiTietCotDiem).delete()
        db.session.commit()
        # print(tao_nhieu_chi_tiet_cot_diem123(list_id_cot_diem=[1,2,3],id_khoi=2,id_nien_khoa=1))
