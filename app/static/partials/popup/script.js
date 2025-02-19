// app/static/partials/popup.js
document.addEventListener('DOMContentLoaded', function() {
    var popupOverlay = document.getElementById('popupOverlay');
    var popupIcon = document.getElementById('popupIcon');
    var popupTitle = document.getElementById('popupTitle');
    var popupMessage = document.getElementById('popupMessage');
    var closePopupBtn = document.getElementById('closePopupBtn');

    closePopupBtn.addEventListener('click', function() {
        popupOverlay.style.display = 'none';
    });

    function showError(error) {
        popupIcon.classList.remove('popup-success');
        popupIcon.classList.add('popup-error');
        popupIcon.setAttribute('name', 'alert-circle');
        popupTitle.innerText = error.title;
        popupMessage.innerText = error.message;
        popupOverlay.style.display = 'flex';
    }

    function showSuccess(success) {
        popupIcon.classList.remove('popup-error');
        popupIcon.classList.add('popup-success');
        popupIcon.setAttribute('name', 'checkmark-circle');
        popupTitle.innerText = success.title;
        popupMessage.innerText = success.message;
        popupOverlay.style.display = 'flex';
    }

    $.ajax({
        url: '/api/v1/flash_messages',
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            if (data.error && data.error.title) {
                showError(data.error);
            } else if (data.success && data.success.title) {
                showSuccess(data.success);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error fetching messages:', error);
        }
    });

    window.showError = showError;
    window.showSuccess = showSuccess;
});
