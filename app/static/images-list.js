//Глобальные переменные
let imagesData = [] //Все изображения
let currentPage = [1] //Текущая страница
const itemsPerPage = 5 //Колво изображений на странице

//Получение данных с сервера
async function fetchImages(){
    try{
        const response = await fetch('/api/images-list/');
        console.log(response);
        if (!response.ok) throw new error('Ошибка загрузки изображений');
        imagesData = await response.json();

        renderTable();
        }
    catch (error) {
        console.error()
                  }
}

// Функция для отображения таблицы
function renderTable(){
//    console.log(imagesData);
    const tableBody = document.getElementById('imagesTableBody');
    tableBody.innerHTML = ''; // clear table

    //Вычисляем диапазон эдементов для текущей страницы
    const start = (currentPage - 1) * itemsPerPage;
//    console.log('start ' ,start)
//    console.log('currentPage ', currentPage)
    const end = currentPage * itemsPerPage;
//    console.log('end', end)
    const currentItems = imagesData.slice(start, end);
//    console.log('currentItems', currentItems)

    //Создание строк таблицы
    currentItems.forEach(image => {
        const row = document.createElement('tr');
        const imageUrl = `/images/${image.filename}.${image.file_type}`

        //Prev
        const previewCell = document.createElement('td');
        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = 'Preview';
        img.style.width = '50px';
        previewCell.appendChild(img);
        row.appendChild(previewCell);

        //URL
        const urlCell = document.createElement('td');
        const link = document.createElement('a');
        link.href = imageUrl;
        link.textContent = image.filename;
        link.target = '_blank';
        urlCell.appendChild(link);
        row.appendChild(urlCell);

        //Orig name
        const origName = document.createElement('td');
        origName.textContent = image.original_name;
        row.appendChild(origName);

        //Size
        const sizeCell = document.createElement('td');
        sizeCell.textContent = image.size;
        row.appendChild(sizeCell);

        //Date
        const dateCell = document.createElement('td');
        dateCell.textContent = image.upload_time;
        row.appendChild(dateCell);

        //TypeFile
        const TypeFileCell = document.createElement('td');
        TypeFileCell.textContent = image.file_type;
        row.appendChild(TypeFileCell);

        //Delete
        const deleteCell = document.createElement('td');
        const deleteButton = document.createElement('button');
        deleteButton.textContext = 'Удалить';
        deleteButton.className = 'btn btn-danger btn-sm';
        deleteButton.onclick = () => deleteImage(image.id);
        deleteCell.appendChild(deleteButton);
        row.appendChild(deleteCell);

        tableBody.appendChild(row);


        });

        updatePaginationControls();

}

function updatePaginationControls(){
    const totalPages = Math.ceil(imagesData.length / itemsPerPage);
    document.getElementById('prevPage').disabled = currentPage === 1;
    document.getElementById('nextPage').disabled = currentPage === totalPages;
    document.getElementById('currentPage').textContent = currentPage;
}

document.getElementById('prevPage').addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage --;
        renderTable();
        }
});

document.getElementById('nextPage').addEventListener('click', () => {
    const totalPages = Math.ceil(imagesData.length / itemsPerPage);
    if (currentPage < totalPages) {
    currentPage++;
    renderTable();
        }
});

//тут происходит удаление из Fronta, но не происходит удаление из базы данных и файлов
function deleteImage(id) {
    imagesData = imagesData.filter(image => image.id !== id);
    fetch(`/api/delete/${id}`, { method: 'DELETE' })
        .then(response => {
        if (response.ok) {
            console.log(`${id} успешно удален`);
        } else {
            console.error(`Ошибка при удалении ${id}`);
        }
    })
    .catch(error => console.error('Ошибка:', error));
    renderTable();
}


// Использование - получение списка файлов и формирование таблицы

document.addEventListener('DOMContentLoaded', () => {
    fetchImages();
});