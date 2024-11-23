from tkinter import messagebox, ttk
from database import Database
import psycopg2
from psycopg2 import extras, sql

class UserManagement:
    def __init__(self, db: Database):
        self.db = db

    # Tải lại bảng dữ liệu
    def reload_table(self, table_name, list_widget):
        if self.db.connection:
            with self.db.connection.cursor() as cur:
                cur.execute(f"SELECT * FROM {table_name}")
                rows = cur.fetchall()

                # Xóa dữ liệu cũ trên TreeView
                for row in list_widget.get_children():
                    list_widget.delete(row)

                # Hiển thị dữ liệu mới
                for row in rows:
                    list_widget.insert('', 'end', values=row)

    # Thêm người dùng mới
    def add_user(self, username, password, role, list_widget):
        if username and password and role:
            try:
                with self.db.connection.cursor() as cursor:
                    query = "INSERT INTO users (user_name, user_password, user_role) VALUES (%s, %s, %s)"
                    cursor.execute(query, (username, password, role))
                    self.db.connection.commit()  # Commit if successful
                    messagebox.showinfo("Thành công", "Thêm người dùng thành công!")
                    self.reload_table('users', list_widget)
            except (Exception, psycopg2.Error) as error:
                self.db.connection.rollback()  # Rollback on error
                messagebox.showerror("Lỗi", f"Không thể thêm người dùng: {error}")
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin.")

    # Xóa người dùng
    def delete_user(self, username, list_widget):
        if username:
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa người dùng '{username}' không?"):
                try:
                    with self.db.connection.cursor() as cursor:
                        query = "DELETE FROM users WHERE user_name = %s"
                        cursor.execute(query, (username,))
                        self.db.connection.commit()  # Commit if successful
                        messagebox.showinfo("Thành công", "Xóa người dùng thành công!")
                        self.reload_table('users', list_widget)
                except (Exception, psycopg2.Error) as error:
                    self.db.connection.rollback()  # Rollback on error
                    messagebox.showerror("Lỗi", f"Không thể xóa người dùng: {error}")
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn người dùng để xóa.")

    # Cập nhật thông tin người dùng
    def update_user(self, user_id, new_username, new_password, new_role, list_widget):
        if user_id:
            try:
                with self.db.connection.cursor() as cursor:
                    query = "UPDATE users SET user_name = %s, user_password = %s, user_role = %s WHERE user_id = %s"
                    cursor.execute(query, (new_username, new_password, new_role, user_id))
                    self.db.connection.commit()  # Commit if successful
                    messagebox.showinfo("Thành công", "Cập nhật thông tin người dùng thành công!")
                    self.reload_table('users', list_widget)
            except (Exception, psycopg2.Error) as error:
                self.db.connection.rollback()  # Rollback on error
                messagebox.showerror("Lỗi", f"Không thể cập nhật người dùng: {error}")
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn người dùng để cập nhật.")
