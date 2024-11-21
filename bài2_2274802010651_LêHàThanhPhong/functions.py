from tkinter import messagebox, ttk
import psycopg2

def check_existed_data(connection):
    cur = connection.cursor()
    
    cur.execute('SELECT * FROM users')
    existing_users = cur.fetchall()

    if len(existing_users) < 1:
        cur.execute('''
            INSERT INTO users (user_name, user_password, user_role) 
            VALUES 
                ('admin', '123456789', '1'),
                ('user', '1', '0')
        ''')
        connection.commit()  # Xác nhận thay đổi

def create_table(connection):
    try:
        cur = connection.cursor()
        
        # Tạo bảng nếu chưa tồn tại
        cur.execute(''' 
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                user_name VARCHAR(255),
                user_password VARCHAR(255),
                user_role VARCHAR(50)
            )
        ''')
        check_existed_data(connection)  # Chèn dữ liệu nếu chưa tồn tại
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        messagebox.showerror(f"Error: {error}")
    
    finally:
        cur.close()

def get_tables(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';""")
            return cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        messagebox.showerror("Lỗi", f"Không thể lấy danh sách bảng: {error}")
        return []

def get_column_names(connection, table_name):
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND table_schema = 'public';
            """
            cursor.execute(query, (table_name,))
            return [col[0] for col in cursor.fetchall()]
    except (Exception, psycopg2.Error) as error:
        messagebox.showerror("Lỗi", f"Không thể lấy tên cột: {error}")
        return []

def reload_table(connection, table_name, list_widget):
    if connection:
        with connection.cursor() as cur:
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()

            # Xóa dữ liệu cũ trên TreeView
            for row in list_widget.get_children():
                list_widget.delete(row)

            # Hiển thị dữ liệu mới
            for row in rows:
                list_widget.insert('', 'end', values=row)

def add_user(connection, username, password, role, list_widget):
    if username and password and role:
        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO users (user_name, user_password, user_role) VALUES (%s, %s, %s)"
                cursor.execute(query, (username, password, role))
                connection.commit()
                messagebox.showinfo("Thành công", "Thêm người dùng thành công!")
                reload_table(connection, 'users', list_widget)
        except (Exception, psycopg2.Error) as error:
            connection.rollback()
            messagebox.showerror("Lỗi", f"Không thể thêm người dùng: {error}")
    else:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin.")

def delete_user(connection, user_id, list_widget):
    try:
        with connection.cursor() as cursor:
            query = "DELETE FROM users WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            connection.commit()
            messagebox.showinfo("Thành công", "Xóa người dùng thành công!")
            reload_table(connection, 'users', list_widget)
    except (Exception, psycopg2.Error) as error:
        connection.rollback()
        messagebox.showerror("Lỗi", f"Không thể xóa người dùng: {error}")

def update_user(connection, user_id, new_username, new_password, new_role, list_widget):
    try:
        with connection.cursor() as cursor:
            query = "UPDATE users SET user_name = %s, user_password = %s, user_role = %s WHERE user_id = %s"
            cursor.execute(query, (new_username, new_password, new_role, user_id))
            connection.commit()
            messagebox.showinfo("Thành công", "Cập nhật người dùng thành công!")
            reload_table(connection, 'users', list_widget)
    except (Exception, psycopg2.Error) as error:
        connection.rollback()
        messagebox.showerror("Lỗi", f"Không thể cập nhật người dùng: {error}")
