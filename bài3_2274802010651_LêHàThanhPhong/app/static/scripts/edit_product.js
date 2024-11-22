
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

$(document).ready(function () {
    // Lấy dữ liệu sản phẩm từ backend
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id');

    if (productId) {
        $.ajax({
            url: `/get-single-product?id=${productId}`, // Tạo route mới để lấy thông tin sản phẩm
            type: 'GET',
            success: function (product) {
                $('select[name="category_id"]').val(product.cat_id);
                $('input[name="id"]').val(product.id);
                $('input[name="name"]').val(product.name);
                $('textarea[name="description"]').val(product.description);
                $('input[name="price"]').val(product.price);
                $('input[name="quantity"]').val(product.quantity);
                $('input[name="status"]').prop('checked', product.status === 0); // 0: Hoạt động
                $('img').attr('src', `/static/uploads/${product.image}`); // Hiển thị ảnh hiện tại
            },
            error: function (xhr) {
                alert('Không thể tải dữ liệu sản phẩm: ' + xhr.responseText);
            }
        });
    }
});

$(document).ready(function () {
    $('#update-product-btn').click(function () {
        let formData = new FormData($('#edit-product-form')[0]); // Lấy toàn bộ dữ liệu trong form

        $.ajax({
            url: '/update-product',
            type: 'POST',
            data: formData,
            processData: false,  // Không xử lý dữ liệu, vì có file
            contentType: false,  // Không đặt header mặc định
            success: function (response) {
                alert(response.message); // Hiển thị thông báo thành công
            },
            error: function (xhr, status, error) {
                alert('Có lỗi xảy ra: ' + xhr.responseText);
            }
        });
    });
});


$(document).ready(function () {
    // Bắt sự kiện click vào nút chỉnh sửa
    $(document).on('click', '.update-product-btn', function () {
        window.location.href = `/admin-board`; // Điều hướng đến trang chỉnh sửa
    });
});