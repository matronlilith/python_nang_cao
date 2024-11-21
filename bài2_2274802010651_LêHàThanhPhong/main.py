import tkinter as tk
from tkinter import messagebox, ttk
from connect import connect_to_db
from functions import create_table, add_user, update_user, delete_user, get_tables, reload_table, get_column_names

def create_login_page():
    global entry_host, entry_database, entry_user, entry_password, entry_port
    login_frame = tk.Frame(win, padx=10, pady=10)
    login_frame.pack(padx=10, pady=10)

    # Host
    host_label = tk.Label(login_frame, text="Host:")
    host_label.grid(row=0, column=0, padx=5, pady=5)
    entry_host = tk.Entry(login_frame)
    entry_host.grid(row=0, column=1, padx=5, pady=5)
    entry_host.insert(0, "localhost")

    # Database
    database_label = tk.Label(login_frame, text="Database:")
    database_label.grid(row=1, column=0, padx=5, pady=5)
    entry_database = tk.Entry(login_frame)
    entry_database.grid(row=1, column=1, padx=5, pady=5)

    # Username
    user_name_label = tk.Label(login_frame, text="Username:")
    user_name_label.grid(row=2, column=0, padx=5, pady=5)
    entry_user = tk.Entry(login_frame)
    entry_user.grid(row=2, column=1, padx=5, pady=5)
    entry_user.insert(0, "postgres")

    # Password
    password_label = tk.Label(login_frame, text="Password:")
    password_label.grid(row=3, column=0, padx=5, pady=5)
    entry_password = tk.Entry(login_frame, show="*")
    entry_password.grid(row=3, column=1, padx=5, pady=5)

    # Port
    port_label = tk.Label(login_frame, text="Port:")
    port_label.grid(row=4, column=0, padx=5, pady=5)
    entry_port = tk.Entry(login_frame)
    entry_port.grid(row=4, column=1, padx=5, pady=5)
    entry_port.insert(0, "5432")

    # Login Button
    login_button = tk.Button(login_frame, text="Đăng nhập", command=login_and_open_admin_page)
    login_button.grid(row=5, column=0, columnspan=2, pady=10)

def login_and_open_admin_page():
    host = entry_host.get()
    database = entry_database.get()
    user = entry_user.get()
    password = entry_password.get()
    port = entry_port.get()

    connection = connect_to_db(host, database, user, password, port)
    if connection:
        create_table(connection)
        show_admin_page(connection)

def show_admin_page(connection):
    global current_connection
    current_connection = connection
    
    
    admin_frame = tk.Frame(win, padx=10, pady=10)
    admin_frame.pack()

    # Admin UI elements here
    tables = get_tables(connection)
    for table in tables:
        table_name = table[0]
        frame_tree = tk.Frame(admin_frame)
        frame_tree.pack(pady=5, fill="both", expand=True)
        show_table(frame_tree, table_name, connection)

    logout_button = tk.Button(admin_frame, text="Đăng xuất", command=lambda: logout(admin_frame))
    logout_button.pack(pady=10)

def show_table(frame, table_name, connection):
    columns = get_column_names(connection, table_name)
    tree = ttk.Treeview(frame, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    
    tree.pack()
    reload_table(connection, table_name, tree)

def logout(admin_frame):
    admin_frame.pack_forget()
    create_login_page()

# Khởi tạo cửa sổ chính
win = tk.Tk()
win.title("Quản lý CSDL")
create_login_page()
win.mainloop()
