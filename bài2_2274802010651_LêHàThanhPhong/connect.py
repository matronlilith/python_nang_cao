import psycopg2
from tkinter import messagebox

# Hàm kết nối cơ sở dữ liệu
def connect_to_db(host, database, user, password, port):
    try:
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port,
            options='-c client_encoding=UTF8'  # Set UTF-8 encoding for the connection
        )
        return connection
    except (Exception, psycopg2.Error) as error:
        messagebox.showerror("Lỗi kết nối", f"Không thể kết nối!: {error}")
        return None
