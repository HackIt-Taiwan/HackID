<!-- static/register/script.js -->
document.addEventListener('DOMContentLoaded', () => {
    const staff = staffData || {};

    const formSteps = document.querySelectorAll('.form-step');
    let currentStep = 0;

    const nextToStep2 = document.getElementById('next-to-step-2');
    const nextToStep3 = document.getElementById('next-to-step-3');
    const backToStep1 = document.getElementById('back-to-step-1');
    const backToStep2 = document.getElementById('back-to-step-2');
    const submitButton = document.getElementById('submit-button');
    const loading = document.getElementById('loading');

    initializeForms();

    nextToStep2.addEventListener('click', () => {
        if (validateStep(0)) {
            saveStepData(0);
            showStep(1);
        }
    });

    backToStep1.addEventListener('click', () => {
        showStep(0);
    });

    nextToStep3.addEventListener('click', () => {
        if (validateStep(1)) {
            saveStepData(1);
            showStep(2);
        }
    });

    backToStep2.addEventListener('click', () => {
        showStep(1);
    });

    submitButton.addEventListener('click', () => {
        if (validateStep(2)) {
            showLoading();
            saveStepData(2, true);
        }
    });

    function showStep(stepIndex) {
        formSteps[currentStep].classList.remove('active');
        formSteps[stepIndex].classList.add('active');
        currentStep = stepIndex;
    }

    function validateStep(stepIndex) {
        const inputs = formSteps[stepIndex].querySelectorAll('input[required], textarea[required]');
        let valid = true;
        let errorShown = false;
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('input-error');
                valid = false;
            } else {
                input.classList.remove('input-error');
            }

            if (input.id === 'phone_number') {
                let phoneNumber = input.value.trim();

                if (phoneNumber.startsWith('8869')) {
                    phoneNumber = '0' + phoneNumber.substring(3);
                    input.value = phoneNumber;
                }

                if (phoneNumber.startsWith('+8869')) {
                    phoneNumber = '0' + phoneNumber.substring(4);
                    input.value = phoneNumber;
                }

                if (phoneNumber.length !== 10 || !/^\d{10}$/.test(phoneNumber)) {
                    input.classList.add('input-error');
                    showError({title: '錯誤', message: '請輸入有效的 10 位數電話號碼'});
                    errorShown = true;
                    valid = false;
                } else {
                    input.value = phoneNumber;
                }
            }
        });
        if (!valid && !errorShown) {
            showError({title: '錯誤', message: '請填寫所有必填欄位'});
        }
        return valid;
    }

    function initializeForms() {
        // Stage 1
        document.getElementById('name').value = staff.name || '';
        document.getElementById('email').value = staff.email || '';
        document.getElementById('phone_number').value = staff.phone_number || '';
        document.getElementById('city').value = staff.city || '';
        document.getElementById('school').value = staff.school || '';

        // Stage 2
        if (staff.emergency_contact) {
            document.getElementById('emergency_name').value = staff.emergency_contact.name || '';
            document.getElementById('emergency_relationship').value = staff.emergency_contact.relationship || '';
            document.getElementById('emergency_phone').value = staff.emergency_contact.phone_number || '';
        }

        // Stage 3
        if (staff.avatar_base64) {
            document.getElementById('avatar-image').src = staff.avatar_base64;
            document.querySelector('.avatar-preview').classList.remove('hidden');
            document.getElementById('drop-zone').classList.add('hidden');

            document.getElementById('avatar').required = false;
        }
        document.getElementById('nickname').value = staff.nickname || '';
        document.getElementById('line_id').value = staff.line_id || '';
        document.getElementById('ig_id').value = staff.ig_id || '';
        document.getElementById('introduction').value = staff.introduction || '';

        initializeDropZone();
    }

    function saveStepData(stepIndex, isFinal = false) {
        const formData = new FormData();

        if (stepIndex >= 0) {
            formData.append('phone_number', document.getElementById('phone_number').value);
            formData.append('city', document.getElementById('city').value);
            formData.append('school', document.getElementById('school').value);
        }

        if (stepIndex >= 1) {
            const emergencyContact = {
                name: document.getElementById('emergency_name').value,
                relationship: document.getElementById('emergency_relationship').value,
                phone_number: document.getElementById('emergency_phone').value,
            };
            formData.append('emergency_contact', JSON.stringify(emergencyContact));
        }

        if (stepIndex >= 2) {
            formData.append('nickname', document.getElementById('nickname').value);
            formData.append('line_id', document.getElementById('line_id').value);
            formData.append('ig_id', document.getElementById('ig_id').value);
            formData.append('introduction', document.getElementById('introduction').value);

            const avatarFile = document.getElementById('avatar').files[0];
            if (avatarFile) {
                formData.append('avatar', avatarFile);
            }
        }

        fetch('/api/v1/register/save', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.error) {
                showError({title: '錯誤', message: data.error});
            } else {
                if (isFinal) {
                    completeRegistration();
                }
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Error:', error);
            showError({title: '錯誤', message: "意外錯誤，請稍後再試"});
        });
    }

    function completeRegistration() {
        fetch('/api/v1/register/complete', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.error) {
                showError({title: '錯誤', message: data.error});
            } else {
                let countdown = 5;
                const countdownInterval = setInterval(() => {
                    if (countdown <= 0) {
                        clearInterval(countdownInterval);
                        window.location.href = '/';
                    } else {
                        showSuccess({
                            title: '填寫成功',
                            message: `將於 ${countdown} 秒後自動跳轉...`
                        });
                    }
                    countdown -= 1;
                }, 1000);
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Error:', error);
            showError({title: '錯誤', message: "意外錯誤，請稍後再試"});
        });
    }

    function initializeDropZone() {
        const dropZone = document.getElementById('drop-zone');
        const avatarInput = document.getElementById('avatar');
        const avatarPreview = document.getElementById('avatar-image');
        const avatarPreviewContainer = document.querySelector('.avatar-preview');
        const editAvatarButton = document.getElementById('edit-avatar');

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('hover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('hover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('hover');
            const file = e.dataTransfer.files[0];
            if (file) {
                handleFile(file);
            }
        });

        avatarInput.addEventListener('change', () => {
            const file = avatarInput.files[0];
            if (file) {
                handleFile(file);
            }
        });

        function handleFile(file) {
            if (file.size > 3 * 1024 * 1024) {
                showError({title: '提示', message: "當前的文件大小超過 3MB，將自動進行壓縮"});
                compressImage(file, 3 * 1024 * 1024, (compressedFile) => {
                    previewAvatar(compressedFile);
                });
            } else {
                previewAvatar(file);
            }
        }

        function previewAvatar(file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                avatarPreview.src = e.target.result;
                avatarPreviewContainer.classList.remove('hidden');
                dropZone.classList.add('hidden');

                document.getElementById('avatar').required = true;
            };
            reader.readAsDataURL(file);
        }

        function compressImage(file, maxSize, callback) {
            const reader = new FileReader();
            reader.onload = function(event) {
                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    const scale = Math.sqrt(maxSize / file.size);
                    canvas.width = img.width * scale;
                    canvas.height = img.height * scale;
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    canvas.toBlob(function(blob) {
                        callback(blob);
                        const compressedFile = new File([blob], file.name, { type: 'image/jpeg' });
                        avatarInput.files = createFileList(compressedFile);
                    }, 'image/jpeg', 0.8);
                };
                img.src = event.target.result;
            };
            reader.readAsDataURL(file);
        }

        function createFileList(file) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            return dataTransfer.files;
        }

        if (editAvatarButton) {
            editAvatarButton.addEventListener('click', () => {
                avatarInput.click();
            });
        }
    }

    function showLoading() {
        loading.classList.remove('hidden');
    }

    function hideLoading() {
        loading.classList.add('hidden');
    }
});
