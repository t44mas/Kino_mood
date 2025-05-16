let cardContainer = '.card';
let moreCards = true;
if (document.querySelectorAll('.card').length === 0) {
    cardContainer = '.rating-block';
    moreCards = false;
}
document.querySelectorAll(cardContainer).forEach(card => {
  const openBtn = card.querySelector('.open-rating-btn');
  const closeBtn = card.querySelector('.close-btn');
  const overlay = card.querySelector('.overlay');
  const popup = card.querySelector('.rating-popup');
  const stars = card.querySelectorAll('.star');
  const ratingText = card.querySelector('.selected-rating-text');
  const submitBtn = card.querySelector('.submit-rating');
  let selectedRating = 0;

  let closeTimeout = null;

    // Открытие попапа
    openBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        clearTimeout(closeTimeout);
        overlay.style.display = 'block';
        popup.style.display = 'block';
        popup.classList.remove('hiding');
        selectedRating = 0;
        updateStars();
        ratingText.textContent = 'Выберите количество звёзд';
    });

    // Закрытие попапа
    closeBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        overlay.style.display = 'none';
        popup.style.display = 'none';
        closePopup();
    });

    overlay.addEventListener('click', function(e) {
        if (e.target === overlay) {
            closePopup();
        }
    });

    // Предотвращаем закрытие при клике внутри попапа
    popup.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Обработка выбора звёзд
    stars.forEach(star => {
        star.addEventListener('click', function() {
            selectedRating = parseInt(star.getAttribute('data-rating'));
            ratingText.textContent = `Вы выбрали ${selectedRating} звёзд(ы)`;
            updateStars();
        });
    });

    // Отправка оценки
    submitBtn.addEventListener('click', function() {
        if (selectedRating === 0) {
            alert('Пожалуйста, выберите оценку');
            return;
        }

       // Получаем ID книги
    const bookId = submitBtn.getAttribute('data-book-id');
    const genre = submitBtn.getAttribute('data-genre');
    // Отправляем данные на сервер
    fetch('/rate_book', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            book_ID: bookId,
            rating: selectedRating
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Спасибо за вашу оценку!');
            let new_rating;
            if (moreCards){
                new_rating = card.querySelector('.card-rating');
            }
            else {
                new_rating = document.querySelector('.card-rating');
            }
            new_rating.innerHTML  = '<p class="card-rating"><i class="fa-solid fa-star"></i>' + data.new_rating + '</p>';
            closePopup();
        } else {
            alert('Ошибка при сохранении оценки: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при отправке оценки');
    });
        closePopup();
    });

    function updateStars() {
        stars.forEach(star => {
            const rating = parseInt(star.getAttribute('data-rating'));
            if (rating <= selectedRating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    function closePopup() {
        // Добавляем класс для анимации закрытия
        popup.classList.add('hiding');

        // Устанавливаем таймер для полного скрытия после анимации
        closeTimeout = setTimeout(() => {
            overlay.style.display = 'none';
            popup.style.display = 'none';
            popup.classList.remove('hiding');
        }, 300); // Должно совпадать с длительностью анимации
    }

    // Закрытие при нажатии ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closePopup();
        }
    });
});
