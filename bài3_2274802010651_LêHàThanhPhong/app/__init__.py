from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Khởi tạo ứng dụng Flask và cơ sở dữ liệu SQLAlchemy
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Cấu hình thư mục uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

# Cấu hình cơ sở dữ liệu
pg_username = 'postgres'
pg_password = '01229168198le.'
pg_host = 'localhost'
pg_port = '5432'
database_name = 'engine'

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{pg_username}:{pg_password}@{pg_host}:{pg_port}/{database_name}'
db = SQLAlchemy(app)

# Nhập các routes
from app import routes