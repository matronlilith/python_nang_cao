

document.getElementById('cart').addEventListener('click', function () {
    fetch('/check_auth')
        .then(response => response.json())
        .then(authData => {
            const cartModal = document.getElementById('cartModal');
            const cartFooter = document.getElementById('cart-footer');
            const cartContainer = document.getElementById('cart-container');

            // Kiểm tra trạng thái đăng nhập
            if (authData.authenticated) {
                // Người dùng đã đăng nhập, hiển thị giỏ hàng
                fetch('/get_cart')
                    .then(response => {
                        if (response.ok) return response.json();
                        throw new Error("Không thể tải dữ liệu giỏ hàng");
                    })
                    .then(data => {
                        if (data.cart_items.length === 0) {
                            cartContainer.innerHTML = '<p>Giỏ hàng trống.</p>';
                            cartFooter.style.display = 'none'; // Ẩn footer nếu giỏ hàng trống
                        } else {
                            cartFooter.style.display = 'flex'; // Hiển thị footer
                            cartContainer.innerHTML = `
                                <div class="cart-row">
                                    <span class="cart-item cart-header cart-column">Sản Phẩm</span>
                                    <span class="cart-price cart-header cart-column">Giá</span>
                                    <span class="cart-quantity cart-header cart-column">Số Lượng</span>
                                </div>`;
                            data.cart_items.forEach(item => {
                                cartContainer.innerHTML += `
                                    <div class="cart-items">
                                        <div class="cart-row cart-product-data">
                                            <div class="cart-item cart-column">
                                                <img class="cart-item-image" src="${item.prod_img}" width="100" height="100">
                                                <span class="cart-item-title">${item.prod_name}</span>
                                            </div>
                                            <span class="cart-price cart-column">${item.prod_price} VND</span>
                                            <div class="cart-quantity cart-column prod_data">
                                                <input type="hidden" value="${item.prod_id}" class="prodId">
                                                <button class="input-group-text increase-btn updateQty">+</button>
                                                <input class="cart-quantity-input text-center input-qty form-control" type="text" value="${item.prod_qty}" disabled>
                                                <button class="input-group-text decrease-btn updateQty">-</button>
                                            </div>
                                            <button class="btn btn-danger deleteItem" value="${item.cart_id}" type="button">Xóa</button>
                                        </div>
                                    </div>`;
                            });
                        }
                    })
                    .catch(error => {
                        console.error(error);
                        alert("Có lỗi xảy ra khi tải giỏ hàng.");
                    });
            } else {
                // Người dùng chưa đăng nhập
                cartContainer.innerHTML = '<p>Bạn cần đăng nhập để sử dụng chức năng giỏ hàng.</p><a href="/login"><button type="button" class="btn btn-warning shadow-sm">Đăng nhập</button></a>';
                cartFooter.style.display = 'none'; // Ẩn footer khi chưa đăng nhập
            }

            // Hiển thị modal giỏ hàng
            cartModal.style.display = 'block';

            // Đóng modal
            cartModal.querySelector('.close').onclick = () => {
                cartModal.style.display = 'none';
            };
            cartFooter.querySelector('.close').onclick = () => {
                cartModal.style.display = 'none';
            };
        })
        .catch(error => {
            console.error("Có lỗi xảy ra khi kiểm tra trạng thái đăng nhập:", error);
        });
});



$(document).ready(function () {

    $(document).on('click', '.increase-btn', function() 
    {

        var $qty = $(this).closest('.prod_data').find('.input-qty');
        // var productId = $(this).closest('.prod_data').find('.prodId');
        var currentValue = parseInt($qty.val());

        if(!isNaN(currentValue))
        {
            currentValue++;
            var qtyVal = currentValue;
            $qty.val(qtyVal);
            // $('#total-price').load(location.href + " #total-price");
            
        }
    });

    $(document).on('click', '.decrease-btn', function() 
    {

        var $qty = $(this).closest('.prod_data').find('.input-qty');
        // var productId = $(this).closest('.prod_data').find('.prodId');
        var currentValue = parseInt($qty.val());

        if(!isNaN(currentValue) && currentValue > 1)
        {
            var qtyVal = currentValue - 1;
            $qty.val(qtyVal);
            // $('#total-price').load(location.href + " #total-price");
        }
    });

    $('.addToCart').click(function (e) {
        e.preventDefault();
    
        // Lấy giá trị số lượng và ID sản phẩm
        var $qty = $(this).closest('.prod_data').find('.input-qty').val();
        var prod_id = $(this).val();
    
        // Tạo đối tượng dữ liệu để gửi đi
        var formData = {
            prod_qty: $qty,
            prod_id: prod_id
        };
    
        // Gửi AJAX request
        $.ajax({
            method: "POST",
            url: "/add-to-cart",
            contentType: "application/json", // Định dạng dữ liệu gửi
            data: JSON.stringify(formData), // Chuyển dữ liệu sang JSON
            success: function (response) {
                if (response.status === 201) {
                    alert("Đã thêm vào giỏ hàng.");
                    window.location.reload();
                } else if (response.status === 300) {
                    alert("Sản phẩm đã được thêm vào giỏ từ trước!");
                } else if (response.status === 401) {
                    alert("Bạn phải đăng nhập để sử dụng chức năng này");
                } else if (response.status === 500) {
                    alert("Đã xảy ra lỗi. Vui lòng thử lại sau.");
                }
            },
            error: function (xhr) {
                if (xhr.status === 401) {
                    alert("Bạn cần đăng nhập để thêm sản phẩm vào giỏ hàng");
                } else if (xhr.status === 400) {
                    alert("Dữ liệu không hợp lệ");
                } else {
                    alert("Đã xảy ra lỗi không mong muốn");
                }
            }
        });
    });

    $(document).on('click','.updateQty', function () {

        var $qty = $(this).closest('.cart-product-data').find('.input-qty').val();
        var prod_id = $(this).closest('.cart-product-data').find('.prodId').val();

        var formData = {
            prod_qty: $qty,
            prod_id: prod_id
        };

        $.ajax ({
            method: "POST",
            url: "/update-cart",
            contentType: "application/json",
            data: JSON.stringify(formData),
            success: function (response)
            {
                if (response == 500)
                {
                    alert("Lỗi! Không thể thay đổi số lượng sản phẩm");
                }
                else if(response != 200)
                {
                    // alert(response);
                }
            }
        });
    });

    $(document).on('click', '.deleteItem', function () {
        var cart_id = $(this).val();  // Lấy cart_id từ thuộc tính value của nút bấm
    
        // Hiển thị hộp thoại xác nhận trước khi xóa
        Swal.fire({
            title: 'Bạn chắc chắn muốn xóa sản phẩm này?',
            text: "Hành động này không thể hoàn tác!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Xóa',
            cancelButtonText: 'Hủy'
        }).then((result) => {
            if (result.isConfirmed) {
                // Nếu người dùng xác nhận, gửi yêu cầu xóa
                $.ajax({
                    method: "POST",
                    url: "/delete-cart-items",
                    contentType: "application/json",
                    data: JSON.stringify({ cart_id: cart_id }),  // Đóng gói cart_id vào đối tượng JSON
                    success: function (response) {
                        if (response.status === 200) {
                            // Hiển thị SweetAlert2 thông báo thành công
                            Swal.fire(
                                'Đã xóa!',
                                'Sản phẩm đã được xóa khỏi giỏ hàng.',
                                'success'
                            );
                            window.location.reload();  // Tải lại trang sau khi xóa thành công
                        } else {
                            Swal.fire(
                                'Lỗi!',
                                response.message,
                                'error'
                            );
                        }
                    },
                    error: function (xhr, status, error) {
                        Swal.fire(
                            'Lỗi!',
                            'Có lỗi xảy ra khi xóa sản phẩm.',
                            'error'
                        );
                    }
                });
            }
        });
    });

});
