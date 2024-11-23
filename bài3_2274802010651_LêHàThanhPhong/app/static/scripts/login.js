

function submitLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'  // Thêm header để xác định đây là yêu cầu AJAX
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        } else if (data.success) {
            Swal.fire({
                icon: 'success',
                title: 'Đăng nhập thành công!',
                text: data.message,
                showConfirmButton: false,
                timer: 2000
            }).then(() => {
                window.location.href = '/';
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Đăng nhập thất bại',
                text: data.message,
                confirmButtonText: 'Thử lại'
            });
        }
    })
    .catch(error => {
        Swal.fire({
            icon: 'error',
            title: 'Lỗi hệ thống',
            text: 'Không thể kết nối với server.',
            confirmButtonText: 'Thử lại'
        });
        console.error('Error:', error);
    });
}



// Đăng xuất
function logout() {
    fetch('/logout', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        // Hiển thị thông báo với SweetAlert2
        Swal.fire({
            icon: 'success',
            title: 'Đăng xuất thành công!',
            text: data.message,
            showConfirmButton: false,
            timer: 1500  // Tự động đóng thông báo sau 1.5 giây
        }).then(() => {
            // Điều hướng đến trang đăng nhập sau khi đóng thông báo
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            }
        });
    })
    .catch(error => {
        console.error("Error:", error);
        // Hiển thị thông báo lỗi nếu xảy ra lỗi khi gọi API
        Swal.fire({
            icon: 'error',
            title: 'Đã xảy ra lỗi',
            text: 'Không thể đăng xuất. Vui lòng thử lại!',
            confirmButtonText: 'OK'
        });
    });
}