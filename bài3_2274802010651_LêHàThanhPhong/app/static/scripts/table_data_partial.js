function highlight(e) {
    if (selected[0]) selected[0].className = '';
    e.target.parentNode.className = 'selected';
    
}

var table = document.getElementById('dataTable'),
    selected = table.getElementsByClassName('selected');
table.onclick = highlight;

function fnselect(){
var $row=$(this).parent().find('td');
    var clickeedID=$row.eq(0).text();
    // alert(clickeedID);
}

$("#tst").click(function(){
    var value =$(".selected td:first").html();
    value = value || "No row Selected";
    alert(value);
});

function deleteRow() {
    var columnData = [];

    // Lấy tên của cột đầu tiên của bảng
    var firstColumnName = $("#dataTable thead th:first").text(); 

    // Lấy dữ liệu của cột đầu tiên của dòng được chọn
    var firstRowValue = $(".selected td:first").text(); 

    // Thêm tên cột và giá trị vào mảng columnData dưới dạng đối tượng
    columnData.push({
        columnName: firstColumnName,
        value: firstRowValue
    });

    // Hiển thị cảnh báo xác nhận với SweetAlert2
    Swal.fire({
        title: 'Bạn có chắc chắn muốn xóa không?',
        text: "Thao tác này không thể hoàn tác!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Xóa',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (result.isConfirmed) {
            // Nếu người dùng xác nhận, thực hiện AJAX để xóa
            $.ajax({
                type: "POST",
                url: '/database/' + databaseName + '/table/' + tableName + '/delete',  // Địa chỉ route của Flask
                contentType: "application/json",  // Thiết lập Content-Type là JSON
                data: JSON.stringify(columnData),  // Chuyển đổi columnData thành JSON
                success: function(response) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Đã xóa thành công!',
                        text: response.message,
                        showConfirmButton: false,
                        timer: 1500  // Đóng sau 1.5 giây
                    });
                    // Xóa dòng khỏi bảng hoặc cập nhật giao diện theo nhu cầu của bạn
                    $(".selected").remove();  // Xóa dòng đã chọn khỏi bảng
                },
                error: function(xhr, status, error) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Có lỗi xảy ra!',
                        text: 'Không thể xóa dòng. Vui lòng thử lại!',
                        confirmButtonText: 'OK'
                    });
                    console.error("Có lỗi xảy ra: " + error);
                }
            });
        }
    });
}

function updateRow() {
    // Tạo một đối tượng để lưu trữ dữ liệu của tất cả các input
    var formData = {};

    // Lặp qua tất cả các trường input trong form và lấy giá trị
    $("#input_form input").each(function() {
        var columnName = $(this).attr('name');  // Lấy tên của input (name)
        var columnValue = $(this).val();  // Lấy giá trị của input
        formData[columnName] = columnValue;  // Thêm vào đối tượng formData
    });

    var columnData = [];
    var firstColumnName = $("#dataTable thead th:first").text(); 
    var firstRowValue = $(".selected td:first").text(); 
    columnData.push({
        columnName: firstColumnName,
        value: firstRowValue
    });

    // Tạo đối tượng dữ liệu tổng hợp
    var dataToSend = {
        formData: formData,
        columnData: columnData
    };

    // Hiển thị cảnh báo xác nhận với SweetAlert2
    Swal.fire({
        title: 'Bạn có chắc chắn muốn cập nhật không?',
        text: "Thao tác này sẽ cập nhật dữ liệu!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Cập nhật',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (result.isConfirmed) {
            // Nếu người dùng xác nhận, thực hiện AJAX để cập nhật
            $.ajax({
                type: "POST",
                url: '/database/' + databaseName + '/table/' + tableName + '/update',  // Địa chỉ route của Flask
                contentType: "application/json",  // Thiết lập Content-Type là JSON
                data: JSON.stringify(dataToSend),  // Chuyển đổi dataToSend thành JSON
                success: function(response) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Cập nhật thành công!',
                        text: response.message,
                        showConfirmButton: false,
                        timer: 1500  // Đóng sau 1.5 giây
                    });
                    // Cập nhật giao diện nếu cần thiết, ví dụ: cập nhật dòng trong bảng
                    $(".selected td").each(function(index) {
                        var inputName = $("#dataTable thead th").eq(index).text();
                        if (formData[inputName]) {
                            $(this).text(formData[inputName]);
                        }
                    });
                },
                error: function(xhr, status, error) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Có lỗi xảy ra!',
                        text: 'Không thể cập nhật. Vui lòng thử lại!',
                        confirmButtonText: 'OK'
                    });
                    console.error("Có lỗi xảy ra: " + error);
                }
            });
        }
    });
}
function addRow() {
    // Tạo một đối tượng FormData để lưu trữ dữ liệu của tất cả các input
    var formData = new FormData();

    // Lặp qua tất cả các trường input trong form và lấy giá trị
    $("#input_form input").each(function() {
        var columnName = $(this).attr('name');  // Lấy tên của input (name)
        var columnValue = $(this).val();  // Lấy giá trị của input
        formData.append(columnName, columnValue);  // Thêm vào FormData
    });

    
    // Kiểm tra sự tồn tại của phần tử file input trước khi lấy file ảnh
    var fileInput = $("#product_img")[0];
    if (fileInput && fileInput.files.length > 0) {
        var imageFile = fileInput.files[0];
        formData.append("product_img", imageFile);
    } else {
    }

    
    Swal.fire({
        title: 'Xác nhận thêm hàng?',
        text: "Bạn có chắc chắn muốn thêm dữ liệu này không?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Thêm',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (result.isConfirmed) {
            // Nếu người dùng xác nhận, thực hiện AJAX để thêm dữ liệu
            $.ajax({
                type: "POST",
                url: '/database/' + databaseName + '/table/' + tableName + '/submit',  
                enctype: 'multipart/form-data',
                data: formData,
                processData: false,  // Ngăn jQuery xử lý dữ liệu
                contentType: false,  // Ngăn jQuery thiết lập Content-Type
                success: function(response) {
                    
                    Swal.fire({
                        icon: 'success',
                        title: 'Thêm thành công!',
                        text: response.message,
                        showConfirmButton: false,
                        timer: 1500  // Đóng sau 1.5 giây
                    });

                    // Cập nhật giao diện nếu cần thiết, ví dụ: thêm hàng mới vào bảng
                    var newRow = $("<tr>");
                    for (var columnName in response.data) {
                        newRow.append($("<td>").text(response.data[columnName]));
                    }
                    $("#dataTable tbody").append(newRow);
                },
                error: function(xhr, status, error) {
                    // Hiển thị thông báo lỗi với SweetAlert2
                    Swal.fire({
                        icon: 'error',
                        title: 'Có lỗi xảy ra!',
                        text: 'Không thể thêm dữ liệu. Vui lòng thử lại!',
                        confirmButtonText: 'OK'
                    });
                    console.error("Có lỗi xảy ra: " + error);
                }
            });
        }
    });
}

function reLoadTable() {
    // Lấy dữ liệu bảng cho database và table
    $.ajax({
        url: '/database/' + databaseName + '/table/' + tableName,
        method: 'GET',
        success: function(response) {
            $('#database-content').html(response);  // Hiển thị dữ liệu bảng trong <div id="database-content">
        },
        error: function(error) {
            console.log("Lỗi khi lấy dữ liệu bảng:", error);
        }
    });
}

function executeQuery() {
    const sqlQuery = document.getElementById("sql-query").value;

    $.ajax({
        url: '/database/' + databaseName + '/execute_query',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({query: sqlQuery}),
        success: function(response) {
            if (response.success) {
                if (response.result) {
                    document.getElementById("query-result").innerHTML = response.result;
                } else {
                    // Hiển thị thông báo thành công bằng SweetAlert2 nếu không có dòng trả về
                    Swal.fire({
                        icon: 'success',
                        title: 'Thực thi thành công!',
                        text: response.message,
                        showConfirmButton: false,
                        timer: 1500  // Đóng sau 1.5 giây
                    });
                }
            } else {
                // Hiển thị thông báo lỗi bằng SweetAlert2
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi truy vấn!',
                    text: response.error,
                    confirmButtonText: 'OK'
                });
            }
        },
        error: function(error) {
            console.error("Error:", error);
            // Hiển thị thông báo lỗi chung khi xảy ra lỗi AJAX
            Swal.fire({
                icon: 'error',
                title: 'Lỗi kết nối!',
                text: 'Không thể thực hiện truy vấn. Vui lòng thử lại!',
                confirmButtonText: 'OK'
            });
        }
    });
}

function uploadImage(columnName) {
    let fileInput = document.getElementById(columnName);
    let formData = new FormData();
    formData.append('file', fileInput.files[0]);  // Lấy file từ input

    fetch('/upload-image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            console.log("Image uploaded successfully. Path:", data.filepath);
            // Sử dụng đường dẫn filepath nếu cần, ví dụ lưu vào database
        } else {
            console.error("Image upload failed.");
        }
    })
    .catch(error => console.error("Error:", error));
}