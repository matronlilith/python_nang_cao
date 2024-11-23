function showTab(id) {
    // Ẩn tất cả các tab
    const tabs = document.querySelectorAll('.tab-pane');
    tabs.forEach(tab => tab.classList.remove('active', 'show'));

    // Hiển thị tab tương ứng
    const activeTab = document.getElementById(id);
    if (activeTab) {
        activeTab.classList.add('active', 'show');
    }
}

$(document).ready(function () {
    $('#submit-product-btn').click(function () {
        let formData = new FormData($('#add-product-form')[0]); // Lấy toàn bộ dữ liệu trong form

        $.ajax({
            url: '/add-product',
            type: 'POST',
            data: formData,
            processData: false,  // Không xử lý dữ liệu, vì có file
            contentType: false,  // Không đặt header mặc định
            success: function (response) {
                alert(response.message); // Hiển thị thông báo thành công
                $('#add-product-form')[0].reset(); // Reset lại form
            },
            error: function (xhr, status, error) {
                alert('Có lỗi xảy ra: ' + xhr.responseText);
            }
        });
    });
});

$(document).ready(function () {
    $('#submit-category-btn').click(function () {
        let formData = new FormData($('#add-category-form')[0]); // Lấy toàn bộ dữ liệu trong form

        $.ajax({
            url: '/add-category',
            type: 'POST',
            data: formData,
            processData: false,  // Không xử lý dữ liệu, vì có file
            contentType: false,  // Không đặt header mặc định
            success: function (response) {
                alert(response.message); // Hiển thị thông báo thành công
                $('#add-category-form')[0].reset(); // Reset lại form
            },
            error: function (xhr, status, error) {
                alert('Có lỗi xảy ra: ' + xhr.responseText);
            }
        });
    });
});

$(document).ready(function () {
    function loadCategories() {
        $.ajax({
            url: '/categories', // URL của route Flask
            type: 'GET',
            success: function (response) {
                // Kiểm tra xem response.categories có tồn tại không
                if (response && response.categories) {
                    let select = $('select[name="category_id"]');
                    select.empty(); // Xóa các tùy chọn hiện tại
                    select.append('<option selected>Chọn Danh mục</option>'); // Thêm tùy chọn mặc định

                    // Lặp qua các danh mục và thêm vào select
                    response.categories.forEach(function (category) {
                        select.append(`<option value="${category.id}">${category.name}</option>`);
                    });
                } else {
                    alert('Dữ liệu danh mục không hợp lệ.');
                }
            },
            error: function (xhr, status, error) {
                alert('Không thể tải danh mục: ' + xhr.responseText);
            }
        });
    }

    loadCategories(); // Gọi hàm khi trang được tải
});

$(document).ready(function() {
    // Gửi AJAX để lấy dữ liệu sản phẩm
    $.ajax({
        url: '/get-products',
        method: 'GET',
        success: function(response) {
            let products = response.products;
            let tableBody = $('.all-prods tbody');
            tableBody.empty();  // Xóa các hàng cũ trước khi thêm mới
            
            // Lặp qua danh sách sản phẩm và thêm vào bảng
            products.forEach(function(product) {
                let productRow = `
                    <tr>
                        <th>${product.id}</th>
                        <th>${product.name}</th>
                        <th>${product.cat_id}</th>
                        <th><img src="/static/uploads/${product.image}" alt="image" width="50"></th>
                        <th>${product.price}</th>
                        <th>${product.description}</th>
                        <th>${product.status === 1 ? 'Không hoạt động' : 'Hoạt động'}</th>
                        <th>${product.quantity}</th>
                        <th>${product.create_at}</th>
                        <th style="display: flex; justify-content:space-between;">
                            <button type="button" class="btn btn-primary edit_product_btn" data-id="${product.id}">Chỉnh sửa</button>
                            <button type="button" class="btn btn-primary delete_product_btn btn-danger" data-id="${product.id}">Xóa</button>
                        </th>
                    </tr>
                `;
                tableBody.append(productRow);
            });
        },
        error: function(error) {
            console.log("Lỗi khi lấy dữ liệu sản phẩm:", error);
        }
    });
});

$(document).ready(function() {
    // Gửi AJAX để lấy dữ liệu sản phẩm
    $.ajax({
        url: '/categories',
        method: 'GET',
        success: function(response) {
            let categories = response.categories;
            let tableBody = $('.all-categories tbody');
            tableBody.empty();  // Xóa các hàng cũ trước khi thêm mới
            
            // Lặp qua danh sách sản phẩm và thêm vào bảng
            categories.forEach(function(category) {
                let categoryRow = `
                    <tr>
                        <th>${category.id}</th>
                        <th>${category.name}</th>
                        <th>${category.status === 1 ? 'Không hoạt động' : 'Hoạt động'}</th>
                        <th>${category.create_at}</th>
                        <th style="display: flex; justify-content:space-between;">
                            <button type="button" class="btn btn-primary edit_categories_btn" data-id="${category.id}">Chỉnh sửa</button>
                            <button type="button" class="btn btn-primary delete_categories_btn btn-danger" data-id="${category.id}">Xóa</button>
                        </th>
                    </tr>
                `;
                tableBody.append(categoryRow);
            });
        },
        error: function(error) {
            console.log("Lỗi khi lấy dữ liệu sản phẩm:", error);
        }
    });
});

$(document).ready(function() {
    // Gửi AJAX để lấy dữ liệu sản phẩm
    $.ajax({
        url: '/get-users',
        method: 'GET',
        success: function(response) {
            let users = response.users;
            let tableBody = $('.all-users tbody');
            tableBody.empty();  // Xóa các hàng cũ trước khi thêm mới
            
            // Lặp qua danh sách sản phẩm và thêm vào bảng
            users.forEach(function(user) {
                let userRow = `
                    <tr>
                        <th>${user.id}</th>
                        <th>${user.name}</th>
                        <th>${user.email}</th>
                        <th>${user.password}</th>
                        <th>${user.phone}</th>
                        <th>${user.role === 1 ? 'Quản trị viên' : 'Người dùng'}</th>
                        <th>
                            ${user.role === 1 ?
                                '<button type="button" class="btn btn-primary delete_admin_role_btn" value="user.id">Tước quyền</button>'
                            :
                                '<button type="button" class="btn btn-primary update_role_btn" value="user.id">Cấp quyền</button>'
                            }
                        </th>
                        <th>${user.address}</th>
                        <th>${user.create_at}</th>
                        <th style="display: flex; justify-content:space-between;">
                            <button type="button" class="btn btn-primary delete_user_btn btn-danger" data-id="${user.id}">Xóa</button>
                        </th>
                    </tr>
                `;
                tableBody.append(userRow);
            });
        },
        error: function(error) {
            console.log("Lỗi khi lấy dữ liệu sản phẩm:", error);
        }
    });
});

$(document).ready(function() {
    // Gửi AJAX để lấy dữ liệu sản phẩm
    $.ajax({
        url: '/get-carts',
        method: 'GET',
        success: function(response) {
            let carts = response.carts;
            let tableBody = $('.all-carts tbody');
            tableBody.empty();  // Xóa các hàng cũ trước khi thêm mới
            
            // Lặp qua danh sách sản phẩm và thêm vào bảng
            carts.forEach(function(cart) {
                let cartRow = `
                    <tr>
                        <th>${cart.id}</th>
                        <th>${cart.user_id}</th>
                        <th>${cart.prod_id}</th>
                        <th>${cart.prod_qty}</th>
                    </tr>
                `;
                tableBody.append(cartRow);
            });
        },
        error: function(error) {
            console.log("Lỗi khi lấy dữ liệu sản phẩm:", error);
        }
    });
});

$(document).ready(function () {
    // Lắng nghe sự kiện khi nhấn nút xóa
    $(document).on('click', '.delete_product_btn', function () {
        let productId = $(this).data('id'); // Lấy ID sản phẩm từ thuộc tính data-id

        if (confirm('Bạn có chắc chắn muốn xóa sản phẩm này không?')) {
            // Gửi AJAX đến backend để xóa sản phẩm
            $.ajax({
                url: '/delete-product',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ id: productId }),
                success: function (response) {
                    alert(response.message); // Hiển thị thông báo thành công
                    location.reload(); // Reload lại danh sách sản phẩm
                },
                error: function (xhr, status, error) {
                    alert('Không thể xóa sản phẩm: ' + xhr.responseText);
                }
            });
        }
    });
});

$(document).ready(function () {
    $(document).on('click', '.delete_categories_btn', function () {
        let cat_Id = $(this).data('id');

        if (confirm('Bạn có chắc chắn muốn xóa danh mục này không?')) {
            $.ajax({
                url: '/delete-category',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ id: cat_Id }),
                success: function (response) {
                    alert(response.message);
                    location.reload();
                },
                error: function (xhr, status, error) {
                    alert('Không thể xóa danh mục: ' + xhr.responseText);
                }
            });
        }
    });
});

$(document).ready(function () {
    $(document).on('click', '.delete_user_btn', function () {
        let userId = $(this).data('id');

        if (confirm('Bạn có chắc chắn muốn xóa người dùng này không?')) {
            $.ajax({
                url: '/delete-user',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ id: userId }),
                success: function (response) {
                    alert(response.message);
                    location.reload();
                },
                error: function (xhr, status, error) {
                    alert('Không thể xóa người dùng: ' + xhr.responseText);
                }
            });
        }
    });
});

$(document).ready(function () {
    // Bắt sự kiện click vào nút chỉnh sửa
    $(document).on('click', '.edit_product_btn', function () {
        const productId = $(this).data('id'); // Lấy ID của sản phẩm từ nút
        window.location.href = `/edit-product?id=${productId}`; // Điều hướng đến trang chỉnh sửa
    });
});

$(document).ready(function () {
    // Bắt sự kiện click vào nút chỉnh sửa
    $(document).on('click', '.edit_categories_btn', function () {
        const categoryId = $(this).data('id'); // Lấy ID của sản phẩm từ nút
        window.location.href = `/edit-category?id=${categoryId}`; // Điều hướng đến trang chỉnh sửa
    });
});

