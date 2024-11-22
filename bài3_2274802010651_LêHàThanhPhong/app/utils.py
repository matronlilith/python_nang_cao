from sqlalchemy import create_engine
from app.config import Config

from app.models import User

def check_user(name, password):
    # Kiểm tra người dùng có tồn tại trong cơ sở dữ liệu không
    user = User.query.filter_by(name=name).first()  # Tìm kiếm người dùng theo user_name
    if user and user.password == password:  # So sánh mật khẩu trực tiếp
        return user
    return None

def get_engine():
    # Tạo kết nối đến cơ sở dữ liệu
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    return engine

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



