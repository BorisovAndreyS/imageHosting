//Глобальные переменные
let imagesData = [] //Все изображения

// Функция для создания карточки изображения
function createImageCard(fileData) {
    const col = document.createElement('div');
    col.className = 'col';

    const card = document.createElement('div');
    card.className = 'card shadow-sm image-item';

    const link = document.createElement('a');
    link.href = `/images/${fileData.filename}.${fileData.file_type}`;
    link.target = '_blank';

    const img = document.createElement('img');
    img.src = `/images/${fileData.filename}.${fileData.file_type}`;
    img.alt = fileData.filename;
    img.className = 'bd-placeholder-img card-img-top';
    img.style.objectFit = 'cover';
    img.style.height = '200px';

    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';

    const text = document.createElement('p');
    text.className = 'card-text text-center';
    text.textContent = fileData.filename;

    const downloadBtnWrapper = document.createElement('div');
    downloadBtnWrapper.className = 'd-flex justify-content-center align-items-center';

    const downloadBtn = document.createElement('a');
    downloadBtn.className = 'btn btn-sm btn-outline-secondary';
    downloadBtn.href = `/images/${fileData.filename}.${fileData.file_type}`;
    downloadBtn.download = fileData.filename;
    downloadBtn.textContent = 'Скачать';

    // Сборка структуры
    link.appendChild(img);
    downloadBtnWrapper.appendChild(downloadBtn);
    cardBody.append(text, downloadBtnWrapper);
    card.append(link, cardBody);
    col.appendChild(card);

    return col;
}

//async function fetchImages(){
//    try{
//        const response = await fetch('/api/images-list/');
//        console.log(response);
//        if (!response.ok) throw new error('Ошибка загрузки изображений');
//        imagesData = await response.json();
//
//        createImageCard();
//        }
//    catch (error) {
//        console.error()
//                  }
//    }
//}


// Использование
document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/all_images/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('imageContainer');
            const fragment = document.createDocumentFragment();

            data.forEach(fileData => {
                fragment.appendChild(createImageCard(fileData));
            });

            container.replaceChildren(fragment);
        })
        .catch(error => console.error('Ошибка загрузки изображений:', error));
});