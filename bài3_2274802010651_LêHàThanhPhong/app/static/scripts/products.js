// function loadCategories() {
//     fetch('/categories')  // Gọi API '/categories'
//         .then(response => response.json())
//         .then(categories => {
//             const list = document.getElementById('categories-list'); // Lấy phần tử <ul>
//             list.innerHTML = ''; // Xóa nội dung cũ

//             // Duyệt qua danh sách danh mục và thêm vào <ul>
//             categories.forEach(category => {
//                 const listItem = document.createElement('li'); // Tạo <li>
//                 listItem.textContent = category.name; // Thêm tên danh mục
//                 list.appendChild(listItem); // Gắn <li> vào <ul>
//             });
//         })
//         .catch(error => {
//             console.error('Failed to load categories:', error);
//         });
// }

// // Gọi hàm loadCategories khi trang được tải
// document.addEventListener('DOMContentLoaded', loadCategories);