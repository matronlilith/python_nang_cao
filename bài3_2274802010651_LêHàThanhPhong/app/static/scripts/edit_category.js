$(document).ready(function () {
    // Bắt sự kiện click vào nút chỉnh sửa
    $(document).on('click', '.update-category-btn', function () {
        window.location.href = `/admin-board`; // Điều hướng đến trang chỉnh sửa
    });
});

$(document).ready(function () {
    // Lấy dữ liệu sản phẩm từ backend
    const urlParams = new URLSearchParams(window.location.search);
    const categoryId = urlParams.get('id');

    if (categoryId) {
        $.ajax({
            url: `/get-single-category?id=${categoryId}`, // Tạo route mới để lấy thông tin sản phẩm
            type: 'GET',
            success: function (category) {
                $('input[name="id"]').val(category.id);
                $('input[name="name"]').val(category.name);
                $('input[name="status"]').prop('checked', category.status === 0); // 0: Hoạt động
            },
            error: function (xhr) {
                alert('Không thể tải dữ liệu sản phẩm: ' + xhr.responseText);
            }
        });
    }
});

$(document).ready(function () {
    $('#update-category-btn').click(function () {
        let formData = new FormData($('#edit-category-form')[0]); // Lấy toàn bộ dữ liệu trong form

        $.ajax({
            url: '/update-category',
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