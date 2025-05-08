// Функция для создания карточки изображения
function createImageCard(filename) {
    const col = document.createElement('div');
    col.className = 'col';

    const card = document.createElement('div');
    card.className = 'card shadow-sm image-item';

    const link = document.createElement('a');
    link.href = `/images/${filename}`;
    link.target = '_blank';

    const img = document.createElement('img');
    img.src = `/images/${filename}`;
    img.alt = filename;
    img.className = 'bd-placeholder-img card-img-top';
    img.style.objectFit = 'cover';
    img.style.height = '200px';

    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';

    const text = document.createElement('p');
    text.className = 'card-text text-center';
    text.textContent = filename;

    const downloadBtnWrapper = document.createElement('div');
    downloadBtnWrapper.className = 'd-flex justify-content-center align-items-center';

    const downloadBtn = document.createElement('a');
    downloadBtn.className = 'btn btn-sm btn-outline-secondary';
    downloadBtn.href = `/images/${filename}`;
    downloadBtn.download = filename;
    downloadBtn.textContent = 'Скачать';

    // Сборка структуры
    link.appendChild(img);
    downloadBtnWrapper.appendChild(downloadBtn);
    cardBody.append(text, downloadBtnWrapper);
    card.append(link, cardBody);
    col.appendChild(card);

    return col;
}

// Использование
document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/all_images/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('imageContainer');
            const fragment = document.createDocumentFragment();

            data.images.forEach(filename => {
                fragment.appendChild(createImageCard(filename));
            });

            container.replaceChildren(fragment);
        })
        .catch(error => console.error('Ошибка загрузки изображений:', error));
});