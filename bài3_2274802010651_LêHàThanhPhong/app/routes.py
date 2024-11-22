from flask import Flask, render_template, request, jsonify, render_template_string, session, redirect, url_for, flash

from sqlalchemy import create_engine, inspect, MetaData, Table, text, insert, update, delete, select, func,  Column
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Row

from werkzeug.utils import secure_filename

from app import app, db
from app.models import User
from app.utils import check_user, get_engine, allowed_file

from datetime import datetime
from math import ceil
import os
# Trang chính

@app.route('/')
def index():
    engine = get_engine()  # Sử dụng get_engine từ utils.py
    metadata = MetaData()
    categories_table = Table('category', metadata, autoload_with=engine)
    products_table = Table('product', metadata, autoload_with=engine)

    with engine.connect() as connection:
        query = select(categories_table).where(categories_table.c.status == '0')
        categories_result = connection.execute(query).mappings()
        categories = [dict(row) for row in categories_result]

        per_page = 6
        page = request.args.get('page', 1, type=int)
        offset = (page - 1) * per_page
        query = select(products_table).limit(per_page).offset(offset)
        result = connection.execute(query)
        products = result.fetchall()

        total_products_query = select(func.count(products_table.c.id))
        total_products_result = connection.execute(total_products_query).scalar()
        total_pages = ceil(total_products_result / per_page)

    return render_template('index.html', products=products, categories=categories, page=page, total_pages=total_pages)

# Đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_name = request.form['user_name']
        user_phone = request.form['user_phone']
        user_email = request.form['user_email']
        user_password = request.form['user_password']
        confirm_password = request.form['confirm_password']

        if user_password != confirm_password:
            flash('Mật khẩu và xác nhận mật khẩu không khớp!', 'error')
            return redirect(url_for('register'))

        engine = get_engine()  # Sử dụng get_engine từ utils.py
        metadata = MetaData()
        users_table = Table('users', metadata, autoload_with=engine)

        try:
            with engine.connect() as connection:
                insert_query = users_table.insert().values(
                    name=user_name,
                    phone_number=user_phone,
                    email=user_email,
                    password=user_password,
                    role=0,  # Mặc định là người dùng
                    address=None
                )
                connection.execute(insert_query)
                connection.commit()

            flash('Đăng ký thành công, vui lòng đăng nhập!', 'success')
            return redirect(url_for('login'))

        except IntegrityError:
            flash('Email hoặc số điện thoại đã được đăng ký!', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')


"""LOGIN/ LOGOUT"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user_name = data['username']
        user_password = data['password']

        try:
            # Kiểm tra người dùng trong cơ sở dữ liệu
            user = check_user(user_name, user_password)

            if user:
                # Lưu thông tin đăng nhập vào session
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['auth'] = True
                session['user_role'] = user.role  # Lưu user_role vào session
                print(session['user_role'])

                # Kiểm tra user_role và chuyển hướng
                if user.role == 1:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({"redirect_url": url_for('admin_board')})
                    return redirect(url_for('admin_board'))  # Chuyển hướng đến trang admin

                elif user.role == 0:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({"redirect_url": url_for('index')})
                    return redirect(url_for('index'))  # Chuyển hướng đến trang sản phẩm

                else:
                    return jsonify({"message": "User role không hợp lệ"}), 400
            else:
                return jsonify({"message": "Tên đăng nhập hoặc mật khẩu không đúng"}), 401

        except SQLAlchemyError as e:
            return jsonify({"message": "Lỗi kết nối cơ sở dữ liệu: " + str(e)}), 500
    else:
        return render_template('login.html')

@app.route('/check_auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({"authenticated": True})
    return jsonify({"authenticated": False})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Xóa toàn bộ dữ liệu trong session
    return jsonify({"message": "Đã đăng xuất thành công", "redirect_url": url_for('login')})

"""GIỎ HÀNG"""

@app.route('/get_cart', methods=['GET'])
def get_cart():
    if 'user_id' not in session:
        return jsonify({"error": "Bạn chưa đăng nhập"}), 401

    user_id = session['user_id']
    engine = get_engine()
    metadata = MetaData()
    carts_table = Table('carts', metadata, autoload_with=engine)
    products_table = Table('product', metadata, autoload_with=engine)

    try:
        with engine.connect() as connection:
            query = select(
                carts_table.c.id,
                carts_table.c.part_id,
                carts_table.c.numberpart,
                products_table.c.part,
                products_table.c.price,
                products_table.c.img
            ).where(
                (carts_table.c.user_id == user_id) &
                (carts_table.c.part_id == products_table.c.id)
            )
            result = connection.execute(query)
            cart_items = [
                {
                    "cart_id": row.id,
                    "prod_id": row.part_id,
                    "prod_qty": row.numberpart,
                    "prod_name": row.part,
                    "prod_price": row.price,
                    "prod_img": url_for('static', filename=f"uploads/{row.img}")
                } for row in result
            ]

        return jsonify({"cart_items": cart_items}), 200

    except SQLAlchemyError as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    # Kiểm tra nếu người dùng đã đăng nhập
    if 'user_id' not in session:
        return jsonify({"message": "Bạn cần đăng nhập để sử dụng chức năng này"}), 401  # Mã 401: Unauthorized

    # Lấy dữ liệu từ request
    data = request.json
    # print(data)
    user_id = session['user_id']
    prod_id = data.get('prod_id')
    prod_qty = data.get('prod_qty', 1)

    # Chuyển prod_qty sang kiểu số nguyên và kiểm tra
    try:
        prod_qty = int(prod_qty)
    except ValueError:
        return jsonify({"message": "Số lượng phải là một số hợp lệ"}), 400

    if not prod_id or prod_qty <= 0:
        return jsonify({"message": "Dữ liệu không hợp lệ"}), 400

    engine = get_engine()
    metadata = MetaData()
    carts_table = Table('carts', metadata, autoload_with=engine)

    try:
        with engine.connect() as connection:
            # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
            query = select(carts_table).where(
                (carts_table.c.user_id == user_id) &
                (carts_table.c.part_id == prod_id)
            )
            existing_cart_item = connection.execute(query).fetchone()

            if existing_cart_item:
                # Nếu sản phẩm đã tồn tại, cập nhật số lượng
                update_query = carts_table.update().where(
                    carts_table.c.id == existing_cart_item.id
                ).values(numberpart=carts_table.c.numberpart + prod_qty) 
                connection.execute(update_query)
                connection.commit()
                return jsonify({"message": "Sản phẩm đã được cập nhật trong giỏ hàng", "status": 200}), 200
            else:
                # Nếu sản phẩm chưa tồn tại, thêm mới vào giỏ hàng
                insert_query = carts_table.insert().values(
                    user_id=user_id,
                    part_id=prod_id,
                    numberpart=prod_qty
                )
                connection.execute(insert_query)
                connection.commit()
                return jsonify({"message": "Sản phẩm đã được thêm vào giỏ hàng", "status": 201}), 201

    except SQLAlchemyError as e:
        print(e)
        return jsonify({"message": "Lỗi cơ sở dữ liệu: " + str(e)}), 500
    
@app.route('/update-cart', methods=['POST'])
def update_cart():
    # Lấy dữ liệu từ request
    data = request.json
    print(data)
    user_id = session['user_id']
    prod_id = data.get('prod_id')
    prod_qty = data.get('prod_qty', 1)

    # Chuyển prod_qty sang kiểu số nguyên và kiểm tra
    try:
        prod_qty = int(prod_qty)
    except ValueError:
        return jsonify({"message": "Số lượng phải là một số hợp lệ"}), 400

    if not prod_id or prod_qty <= 0:
        return jsonify({"message": "Dữ liệu không hợp lệ"}), 400

    engine = get_engine()
    metadata = MetaData()
    carts_table = Table('carts', metadata, autoload_with=engine)

    try:
        with engine.connect() as connection:

            # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
            query = select(carts_table).where(
                (carts_table.c.user_id == user_id) & 
                (carts_table.c.part_id == prod_id)
            )
            existing_cart_item = connection.execute(query).fetchone()

            if existing_cart_item:
                # Nếu sản phẩm đã tồn tại trong giỏ hàng, cập nhật số lượng
                update_query = carts_table.update().where(
                    carts_table.c.id == existing_cart_item.id
                ).values(numberpart=prod_qty)  # Cập nhật số lượng mới
                connection.execute(update_query)
                connection.commit()  # Commit sau khi cập nhật
                return jsonify({"message": "Sản phẩm đã được cập nhật trong giỏ hàng", "status": 200}), 200
            else:
                return jsonify({"message": "Sản phẩm không tồn tại", "status": 201}), 201

    except SQLAlchemyError as e:
        print(e)
        return jsonify({"message": "Lỗi cơ sở dữ liệu: " + str(e)}), 500
    
@app.route('/delete-cart-items', methods=['POST'])
def delete_cart_items():
    # Lấy dữ liệu từ request
    data = request.get_json()  # Thử lấy dữ liệu JSON từ request
    if not data or not isinstance(data, dict):
        return jsonify({"message": "Dữ liệu không hợp lệ"}), 400

    user_id = session['user_id']
    cart_id = data.get('cart_id')
    cart_id = int(cart_id)

    if not cart_id or not isinstance(cart_id, int):
        return jsonify({"message": "ID giỏ hàng không hợp lệ"}), 400

    # Kiểm tra cart_id có tồn tại không và có phải là số không
    if not cart_id or not isinstance(cart_id, int):
        return jsonify({"message": "ID giỏ hàng không hợp lệ"}), 400

    engine = get_engine()
    metadata = MetaData()
    carts_table = Table('carts', metadata, autoload_with=engine)

    try:
        with engine.connect() as connection:
            # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
            query = select(carts_table).where(
                (carts_table.c.user_id == user_id) & 
                (carts_table.c.id == cart_id)
            )
            existing_cart_item = connection.execute(query).fetchone()

            if existing_cart_item:
                # Nếu sản phẩm đã tồn tại trong giỏ hàng, xóa
                delete_query = carts_table.delete().where(
                    carts_table.c.id == cart_id
                )
                connection.execute(delete_query)
                connection.commit()  # Commit sau khi xóa
                return jsonify({"message": "Sản phẩm đã được xóa khỏi giỏ hàng", "status": 200}), 200
            else:
                return jsonify({"message": "Sản phẩm không tồn tại", "status": 404}), 404

    except SQLAlchemyError as e:
        print(e)
        return jsonify({"message": "Lỗi cơ sở dữ liệu: " + str(e)}), 500



"""USER VIEW"""

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_input', '').strip()
    engine = get_engine()
    metadata = MetaData()
    connection = engine.connect()
    products_table = Table('product', metadata, autoload_with=engine)

    # Truy vấn database để tìm sản phẩm có tên giống với truy vấn tìm kiếm
    query = products_table.select().where(products_table.c.part.ilike(f'%{search_query}%'))
    result = connection.execute(query).mappings()  # Thêm .mappings() để lấy kết quả dưới dạng dictionary

    # Chuyển đổi kết quả thành danh sách dictionary
    products = [dict(row) for row in result]

    connection.close()
    
    # Render lại trang kết quả tìm kiếm với các sản phẩm tìm được
    return render_template('search_results.html', products=products, search_query=search_query)

@app.route('/product/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    # Tạo kết nối tới cơ sở dữ liệu
    engine = get_engine()
    metadata = MetaData()
    products_table = Table('product', metadata, autoload_with=engine)

    # Truy vấn sản phẩm theo product_id
    with engine.connect() as connection:
        # Truy vấn bảng products và tìm sản phẩm với product_id
        query = select(products_table).where(products_table.c.id == product_id)
        result = connection.execute(query)

        # Lấy thông tin sản phẩm (nếu có)
        product = result.fetchone()  # Lấy một dòng đầu tiên của kết quả

    # Nếu tìm thấy sản phẩm, render template với dữ liệu sản phẩm
    if product:
        return render_template('product_detail.html', product=product)
    else:
        return "Sản phẩm không tồn tại", 404


@app.route('/product/<int:id>_<category_name>')
def show_category(id, category_name):
    # Truy vấn sản phẩm thuộc danh mục từ bảng products
    engine = get_engine()
    metadata = MetaData()
    categories_table = Table('category', metadata, autoload_with=engine)
    products_table = Table('product', metadata, autoload_with=engine)

    with engine.connect() as connection:
        # Truy vấn sản phẩm theo id danh mục và tên danh mục
        query = select(categories_table).where(categories_table.c.status == '0')
        categories_result = connection.execute(query).mappings()
        categories = [dict(row) for row in categories_result]

        # Lấy danh sách sản phẩm
        per_page = 6
        page = request.args.get('page', 1, type=int)
        offset = (page - 1) * per_page
        query = select(products_table).where(
            products_table.c.category_id == id,
        ).limit(per_page).offset(offset)
        result = connection.execute(query).mappings()
        products = [dict(row) for row in result]

        # Tính tổng số trang
        total_products_query = select(func.count(products_table.c.id)).where(products_table.c.category_id == id)
        total_products_result = connection.execute(total_products_query).scalar()
        total_pages = ceil(total_products_result / per_page)

    return render_template(
        'category_products.html',
        products=products,
        categories=categories,
        category_name=category_name,  # Truyền danh mục vào template
        id=id,
        page=page,
        total_pages=total_pages
    )


"""ADMIN PAGE ACTION"""

@app.route('/admin-board')
def admin_board():
    # Nếu không, trả về HTML bình thường
    engine = create_engine(f'postgresql+psycopg2://postgres:01229168198le.@localhost:5432')
    try:
        with engine.connect() as connection:
            databases = ["engine"]
    except SQLAlchemyError as e:
        return jsonify({"message": "Lỗi khi truy xuất cơ sở dữ liệu: " + str(e)}), 500
    
    return render_template('admin.html', databases=databases)

@app.route('/add-product', methods=['POST'])
def add_product():
    try:
        # Nhận dữ liệu từ AJAX
        category_id = request.form.get('category_id')
        name = request.form.get('name')
        description = request.form.get('description')
        description = request.form.get('description', '').strip()

        price = request.form.get('price')
        quantity = request.form.get('quantity')
        quantity = int(request.form.get('quantity', 0))

        status = bool(request.form.get('status'))  # True nếu được chọn
        status = 0 if request.form.get('status') == 'on' else 1  # 1: Không hoạt động, 0: Hoạt động

        # Xử lý file tải lên
        image_file = request.files.get('image')
        image_filename = None
        if image_file and allowed_file(image_file.filename):
            # Đổi tên file
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = secure_filename(image_file.filename)
            image_filename = f"{timestamp}_{filename}"

            # Lưu file
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # Lưu dữ liệu vào cơ sở dữ liệu
        engine = get_engine()
        metadata = MetaData()
        products_table = Table('product', metadata, autoload_with=engine)

        with engine.connect() as connection:
            insert_query = products_table.insert().values(
                category_id=category_id,
                part=name,
                describe=description,
                price=price,
                img=image_filename,
                numberpart=quantity,
                status=status
            )
            connection.execute(insert_query)
            connection.commit()

        return jsonify({'message': 'Thêm sản phẩm thành công!'}), 200

    except Exception as e:
        print(e)
        return jsonify({'message': 'Lỗi: ' + str(e)}), 500

@app.route('/add-category', methods=['POST'])
def add_category():
    try:
        # Nhận dữ liệu từ AJAX
        name = request.form.get('name')

        status = bool(request.form.get('status'))  # True nếu được chọn
        status = 0 if request.form.get('status') == 'on' else 1  # 0: Không hoạt động, 1: Hoạt động


        # Lưu dữ liệu vào cơ sở dữ liệu
        engine = get_engine()
        metadata = MetaData()
        categories_table = Table('category', metadata, autoload_with=engine)

        with engine.connect() as connection:
            insert_query = categories_table.insert().values(
                name=name,
                status=status
            )
            connection.execute(insert_query)
            connection.commit()

        return jsonify({'message': 'Thêm danh mục thành công!'}), 200

    except Exception as e:
        print(e)
        return jsonify({'message': 'Lỗi: ' + str(e)}), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    try:
        # Kết nối đến cơ sở dữ liệu
        engine = engine = get_engine()
        metadata = MetaData()
        categories_table = Table('category', metadata,autoload_with=engine)

        # Truy vấn dữ liệu
        with engine.connect() as connection:
            query = categories_table.select()
            result = connection.execute(query).fetchall()

        # Chuyển đổi kết quả thành dictionary
        categories = []
        for row in result:
            categories.append({
                        'id': row[0],
                        'name': row[1],
                        'status': row[2],
                        'create_at': row[3]
                    })
        return jsonify({'categories': categories}), 200

    except Exception as e:
        print(e)
        return jsonify({'message': 'Lỗi: ' + str(e)}), 500
    
@app.route('/get-products', methods=['GET'])
def get_products():
    try:
        # Kết nối đến cơ sở dữ liệu
        engine = get_engine()
        metadata = MetaData()
        products_table = Table('product', metadata, autoload_with=engine)

        # Thực hiện truy vấn để lấy tất cả sản phẩm
        with engine.connect() as connection:
            query = products_table.select()
            result = connection.execute(query).fetchall()
            
            # Chuyển kết quả thành danh sách các dictionary
            products = []
            for row in result:
                # Đảm bảo bạn sử dụng tên cột thay vì chỉ số
                products.append({
                    'id': row[0],
                    'name': row[1],
                    'price': row[2],
                    'image': row[3],
                    'description': row[4],
                    'cat_id': row[5],
                    'status': row[6],  # Trạng thái
                    'quantity': row[7],
                    'create_at': row[8]
                })
        # Trả về kết quả dưới dạng JSON
        return jsonify({'products': products}), 200

    except Exception as e:
        print(e)
        return jsonify({'message': 'Lỗi: ' + str(e)}), 500

@app.route('/get-users', methods=['GET'])
def get_users():
    try:
        # Kết nối đến cơ sở dữ liệu
        engine = get_engine()
        metadata = MetaData()
        users_table = Table('users', metadata, autoload_with=engine)

        # Thực hiện truy vấn để lấy tất cả sản phẩm
        with engine.connect() as connection:
            query = users_table.select()
            result = connection.execute(query).fetchall()
            
            # Chuyển kết quả thành danh sách các dictionary
            users = []
            for row in result:
                # Đảm bảo bạn sử dụng tên cột thay vì chỉ số
                users.append({
                    'id': row[0],
                    'name': row[1],
                    'password': row[2],
                    'role': row[3],
                    'address': row[4],
                    'email': row[5],
                    'phone': row[6],
                    'create_at': row[7]
                })
        # Trả về kết quả dưới dạng JSON
        return jsonify({'users': users}), 200

    except Exception as e:
        print(e)
        return jsonify({'message': 'Lỗi: ' + str(e)}), 500
    
@app.route('/get-carts', methods=['GET'])
def get_carts():
    try:
        # Kết nối đến cơ sở dữ liệu
        engine = get_engine()
        metadata = MetaData()
        carts_table = Table('carts', metadata, autoload_with=engine)

        # Thực hiện truy vấn để lấy tất cả sản phẩm
        with engine.connect() as connection:
            query = carts_table.select()
            result = connection.execute(query).fetchall()
            
            # Chuyển kết quả thành danh sách các dictionary
            carts = []
            for row in result:
                # Đảm bảo bạn sử dụng tên cột thay vì chỉ số
                carts.append({
                    'id': row[0],
                    'user_id': row[1],
                    'prod_id': row[2],
                    'prod_qty': row[3]
                })
        # Trả về kết quả dưới dạng JSON
        return jsonify({'carts': carts}), 200

    except Exception as e:
        print(e)
        return jsonify({'message': 'Lỗi: ' + str(e)}), 500
    
@app.route('/get-single-product', methods=['GET'])
def get_product():
    try:
        product_id = request.args.get('id')  # Lấy ID sản phẩm
        if not product_id:
            return jsonify({'message': 'Product ID is required.'}), 400

        # Kết nối đến cơ sở dữ liệu
        engine = get_engine()
        metadata = MetaData()
        products_table = Table('product', metadata, autoload_with=engine)

        with engine.connect() as connection:
            query = products_table.select().where(products_table.c.id == product_id)
            result = connection.execute(query).fetchone()

        if not result:
            return jsonify({'message': 'Product not found.'}), 404

        # Trả về thông tin sản phẩm dưới dạng JSON
        product = {
            'id': result[0],
            'name': result[1],
            'price': result[2],
            'image': result[3],
            'description': result[4],
            'cat_id': result[5],
            'status': result[6],
            'quantity': result[7]
        }
        return jsonify(product), 200

    except Exception as e:
        print('0',e)
        return jsonify({'message': 'Error: ' + str(e)}), 500
    
@app.route('/edit-product', methods=['GET'])
def edit_product_page():
    try:
        product_id = request.args.get('id')  # Lấy ID sản phẩm từ URL
        if not product_id:
            return "Product ID is required.", 400

        # Kết nối đến cơ sở dữ liệu và lấy thông tin sản phẩm
        engine = get_engine()
        metadata = MetaData()
        products_table = Table('product', metadata, autoload_with=engine)

        with engine.connect() as connection:
            query = products_table.select().where(products_table.c.id == product_id)
            result = connection.execute(query).fetchone()

        if not result:
            return "Product not found.", 404

        # Chuyển đổi kết quả thành dictionary
        product = {
            'id': result[0],
            'name': result[1],
            'price': result[2],
            'image': result[3],
            'description': result[4],
            'cat_id': result[5],
            'status': result[6],
            'quantity': result[7]
        }

        return render_template('edit-product.html', product=product)

    except Exception as e:
        print('1',e)
        return str(e), 500

@app.route('/update-product', methods=['POST'])
def update_product():
    try:
        data = request.form
        product_id = data.get('id')
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        quantity = data.get('quantity')
        status = 0 if data.get('status') == 'on' else 1
        category_id = data.get('category_id')
        print(data)

        # Xử lý file tải lên nếu có
        image_file = request.files.get('image')
        image_filename = None
        if image_file and allowed_file(image_file.filename):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = secure_filename(image_file.filename)
            image_filename = f"{timestamp}_{filename}"
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # Kết nối đến cơ sở dữ liệu và cập nhật sản phẩm
        engine = get_engine()
        metadata = MetaData()
        products_table = Table('product', metadata, autoload_with=engine)

        with engine.connect() as connection:
            update_query = products_table.update().where(products_table.c.id == product_id).values(
                part=name,
                describe=description,
                price=price,
                numberpart=quantity,
                status=status,
                category_id=category_id,
                img=image_filename if image_filename else products_table.c.img
            )
            connection.execute(update_query)
            connection.commit()

        return jsonify({'message': 'Cập nhật sản phẩm thành công!'}), 200

    except Exception as e:
        print('2',e)
        return jsonify({'message': 'Error: ' + str(e)}), 500
    
@app.route('/delete-product', methods=['POST'])
def delete_product():
    try:
        # Lấy `id` sản phẩm từ yêu cầu
        data = request.get_json()
        product_id = data.get('id')

        if not product_id:
            return jsonify({'message': 'ID sản phẩm không được để trống!'}), 400

        # Kết nối cơ sở dữ liệu
        engine = get_engine()
        metadata = MetaData()
        products_table = Table('product', metadata, autoload_with=engine)

        with engine.connect() as connection:
            # Lấy thông tin sản phẩm để kiểm tra file ảnh
            query = select(products_table.c.img).where(products_table.c.id == product_id)
            result = connection.execute(query).fetchone()

            if result and result[0]:  # Nếu sản phẩm có ảnh
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], result[0])
                if os.path.exists(image_path):
                    os.remove(image_path)  # Xóa file ảnh

            # Xóa sản phẩm trong cơ sở dữ liệu
            delete_query = products_table.delete().where(products_table.c.id == product_id)
            connection.execute(delete_query)
            connection.commit()

        return jsonify({'message': 'Xóa sản phẩm và hình ảnh thành công!'}), 200

    except Exception as e:
        print('Lỗi:', e)
        return jsonify({'message': 'Error: ' + str(e)}), 500

@app.route('/delete-user', methods=['POST'])
def delete_user():
    try:
        # Lấy `id` sản phẩm từ yêu cầu
        data = request.get_json()
        user_id = data.get('id')

        if not user_id:
            return jsonify({'message': ' trống!'}), 400

        # Kết nối cơ sở dữ liệu
        engine = get_engine()
        metadata = MetaData()
        users_table = Table('users', metadata, autoload_with=engine)

        with engine.connect() as connection:
            # Xóa sản phẩm trong cơ sở dữ liệu
            delete_query = users_table.delete().where(users_table.c.id == user_id)
            connection.execute(delete_query)
            connection.commit()

        return jsonify({'message': 'Xóa sản phẩm và hình ảnh thành công!'}), 200

    except Exception as e:
        print('Lỗi:', e)
        return jsonify({'message': 'Error: ' + str(e)}), 500

@app.route('/get-single-category', methods=['GET'])
def get_category():
    try:
        category_id = request.args.get('id')  # Lấy ID sản phẩm
        if not category_id:
            return jsonify({'message': 'category ID is required.'}), 400

        # Kết nối đến cơ sở dữ liệu
        engine = get_engine()
        metadata = MetaData()
        categories_table = Table('category', metadata, autoload_with=engine)

        with engine.connect() as connection:
            query = categories_table.select().where(categories_table.c.id == category_id)
            result = connection.execute(query).fetchone()

        if not result:
            return jsonify({'message': 'category not found.'}), 404

        # Trả về thông tin sản phẩm dưới dạng JSON
        category = {
            'id': result[0],
            'name': result[1],
            'status': result[2],
        }
        return jsonify(category), 200

    except Exception as e:
        print('0',e)
        return jsonify({'message': 'Error: ' + str(e)}), 500
    
@app.route('/edit-category', methods=['GET'])
def edit_category_page():
    try:
        category_id = request.args.get('id')  # Lấy ID sản phẩm từ URL
        if not category_id:
            return "category ID is required.", 400

        # Kết nối đến cơ sở dữ liệu và lấy thông tin sản phẩm
        engine = get_engine()
        metadata = MetaData()
        categories_table = Table('category', metadata, autoload_with=engine)

        with engine.connect() as connection:
            query = categories_table.select().where(categories_table.c.id == category_id)
            result = connection.execute(query).fetchone()

        if not result:
            return "category not found.", 404

        # Chuyển đổi kết quả thành dictionary
        category = {
            'id': result[0],
            'name': result[1],
            'status': result[2],
        }

        return render_template('edit-category.html', category=category)

    except Exception as e:
        print('1',e)
        return str(e), 500

@app.route('/update-category', methods=['POST'])
def update_category():
    try:
        data = request.form
        category_id = data.get('id')
        name = data.get('name')
        status = 0 if data.get('status') == 'on' else 1
        print(data)


        # Kết nối đến cơ sở dữ liệu và cập nhật sản phẩm
        engine = get_engine()
        metadata = MetaData()
        categories_table = Table('category', metadata, autoload_with=engine)

        with engine.connect() as connection:
            update_query = categories_table.update().where(categories_table.c.id == category_id).values(
                name=name,
                status=status,
            )
            connection.execute(update_query)
            connection.commit()

        return jsonify({'message': 'Cập nhật sản phẩm thành công!'}), 200

    except Exception as e:
        print('2',e)
        return jsonify({'message': 'Error: ' + str(e)}), 500

@app.route('/delete-category', methods=['POST'])
def delete_category():
    try:
        # Lấy `id` sản phẩm từ yêu cầu
        data = request.get_json()
        category_id = data.get('id')

        if not category_id:
            return jsonify({'message': 'trống!'}), 400

        # Kết nối cơ sở dữ liệu
        engine = get_engine()
        metadata = MetaData()
        categories_table = Table('category', metadata, autoload_with=engine)

        with engine.connect() as connection:
            # Xóa sản phẩm trong cơ sở dữ liệu
            delete_query = categories_table.delete().where(categories_table.c.id == category_id)
            connection.execute(delete_query)
            connection.commit()

        return jsonify({'message': 'Xóa danh mục thành công!'}), 200

    except Exception as e:
        print('Lỗi:', e)
        return jsonify({'message': 'Error: ' + str(e)}), 500
