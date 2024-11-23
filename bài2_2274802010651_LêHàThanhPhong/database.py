import psycopg2
from psycopg2 import sql
from tkinter import messagebox

class Database:
    def __init__(self):
        self.connection = None

    # Kết nối đến cơ sở dữ liệu
    def connect(self, host, database, user, password, port):
        try:
            self.connection = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port,
                options='-c client_encoding=UTF8'  # Cài đặt mã hóa UTF-8 cho kết nối
            )
            self.create_table()  # Tạo bảng sau khi kết nối thành công
            return self.connection
        except (Exception, psycopg2.Error) as error:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối: {error}")
            return None

    # Tạo bảng nếu chưa tồn tại
    def create_table(self):
        try:
            cur = self.connection.cursor()
            cur.execute(''' 
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    user_name VARCHAR(255),
                    user_password VARCHAR(255),
                    user_role VARCHAR(50)
                )
            ''')
            self.check_existed_data()
        except (Exception, psycopg2.Error) as error:
            messagebox.showerror(f"Lỗi tạo bảng: {error}")
        finally:
            cur.close()

    # Kiểm tra và thêm dữ liệu người dùng mặc định nếu chưa tồn tại
    def check_existed_data(self):
        cur = self.connection.cursor()
        cur.execute('SELECT * FROM users')
        existing_users = cur.fetchall()

        # Nếu người dùng chưa tồn tại, thêm mới
        if len(existing_users) < 1:
            cur.execute('''
                INSERT INTO users (user_name, user_password, user_role) 
                VALUES 
                    ('admin', '1', '1'),
                    ('nva', '1', '0')
            ''')
            self.connection.commit()  # Xác nhận thay đổi
        cur.close()
