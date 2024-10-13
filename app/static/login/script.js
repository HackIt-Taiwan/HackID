// app/static/login/script.js

document.addEventListener('DOMContentLoaded', () => {
    const registerContainer = document.getElementById('register-container');
    const loginContainer = document.getElementById('login-container');
    const registerEmailInput = document.getElementById('register-email');
    const registerUuidInput = document.getElementById('id-code');
    const loginEmailInput = document.getElementById('login-email');
    const googleButton = document.getElementById('google-button');
    const loginButton = document.getElementById('login-button');

    if (uuid && email) {
        registerContainer.classList.remove('hidden');
        loginContainer.classList.add('hidden');
        registerEmailInput.value = email;
        registerUuidInput.value = uuid;
    } else if (email && !uuid) {
        registerContainer.classList.add('hidden');
        loginContainer.classList.remove('hidden');
        loginEmailInput.value = email;
        googleButton.classList.add('fade-hidden');
        loginButton.classList.remove('fade-hidden');
    } else {
        registerContainer.classList.add('hidden');
        loginContainer.classList.remove('hidden');
    }
});

const registerButton = document.getElementById('register-button');
registerButton.addEventListener('click', () => {
    const uuidCode = document.getElementById('id-code').value;
    const email = document.getElementById('register-email').value;

    if (!uuidCode || !email) {
        showError({title: '錯誤', message: `請輸入您的識別碼和電子郵件`});
        return;
    }

    registerButton.disabled = true;
    registerButton.innerHTML = '處理中...<span class="spinner"></span>';

    fetch('/api/v1/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({uuid: uuidCode, email: email})
    })
    .then(response => response.json())
    .then(data => {
        registerButton.disabled = false;
        registerButton.innerHTML = '送出';

        if (data.error) {
            showError({title: '錯誤', message: "您所輸入的識別碼或電子郵件地址不正確"});
        } else {
            document.getElementById('register-container').classList.add('hidden');
            document.getElementById('register-code-container').classList.remove('hidden');
            document.getElementById('register-code-container').classList.add('fade-in');
            document.querySelectorAll('#register-code-container .code-input')[0].focus();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        registerButton.disabled = false;
        registerButton.innerHTML = '送出';
        showError({title: '錯誤', message: "意外錯誤，請稍後再試"});
    });
});

const loginButton = document.getElementById('login-button');
loginButton.addEventListener('click', () => {
    const email = document.getElementById('login-email').value;

    if (!email) {
        showError({title: '錯誤', message: "請輸入您的電子郵件地址"});
        return;
    }

    loginButton.disabled = true;
    loginButton.innerHTML = '處理中...<span class="spinner"></span>';

    fetch('/api/v1/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email: email})
    })
    .then(response => response.json())
    .then(data => {
        loginButton.disabled = false;
        loginButton.innerHTML = '登入';

        if (data.error) {
            showError({title: '錯誤', message: "您所輸入的電子郵件地址不正確"});
        } else {
            document.getElementById('login-container').classList.add('hidden');
            document.getElementById('login-code-container').classList.remove('hidden');
            document.getElementById('login-code-container').classList.add('fade-in');
            document.querySelectorAll('#login-code-container .code-input')[0].focus();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        loginButton.disabled = false;
        loginButton.innerHTML = '登入';
        showError({title: '錯誤', message: "意外錯誤，請稍後再試"});
    });
});

// Function to handle code submission
function handleCodeSubmission(code, email) {
    const container = document.querySelector('.code-container.processing') || document.querySelector('.code-container');
    if (code.length !== 8) {
        showError({title: '錯誤', message: "請輸入完整的驗證碼"});
        hideProcessingAnimation(container);
        return;
    }

    fetch('/api/v1/verify_code', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email: email, code: code})
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingAnimation(container);

        if (data.error) {
            showError({title: '錯誤', message: "您所輸入的驗證碼不正確或已過期"});
        } else {
            let countdown = 5;
            const countdownInterval = setInterval(() => {
                if (countdown <= 0) {
                    clearInterval(countdownInterval);
                    window.location.reload();
                } else {
                    showSuccess({
                        title: '登入成功',
                        message: `將於 ${countdown} 秒後自動跳轉...`
                    });
                }
                countdown -= 1;
            }, 1000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        hideProcessingAnimation(container);
        showError({title: '錯誤', message: "意外錯誤，請稍後再試"});
    });
}

function showProcessingAnimation(container) {
    container.classList.add('processing');
}

function hideProcessingAnimation(container) {
    container.classList.remove('processing');
}

const loginEmail = document.getElementById('login-email');
const googleButton = document.getElementById('google-button');

if (loginEmail) {
    loginEmail.addEventListener('input', () => {
        if (loginEmail.value.length > 0) {
            googleButton.classList.add('fade-hidden');
            loginButton.classList.remove('fade-hidden');
        } else {
            googleButton.classList.remove('fade-hidden');
            loginButton.classList.add('fade-hidden');
        }
    });
}

const resendLoginCodeButton = document.getElementById('resend-login-code-button');
const resendRegisterCodeButton = document.getElementById('resend-register-code-button');

if (resendLoginCodeButton) {
    resendLoginCodeButton.addEventListener('click', () => {
        const email = document.getElementById('login-email').value;

        if (!email) {
            showError({title: '錯誤', message: "請輸入您的電子郵件地址"});
            return;
        }

        resendLoginCodeButton.disabled = true;
        resendLoginCodeButton.innerHTML = '重發中...<span class="spinner"></span>';

        fetch('/api/v1/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email: email})
        })
        .then(response => response.json())
        .then(data => {
            resendLoginCodeButton.disabled = false;
            resendLoginCodeButton.innerHTML = '重發驗證碼';

            if (data.error) {
                showError({title: '錯誤', message: data.error});
            } else {
                alert('驗證碼已重發！');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resendLoginCodeButton.disabled = false;
            resendLoginCodeButton.innerHTML = '重發驗證碼';
            showError({title: '錯誤', message: "意外錯誤，請稍後再試"});
        });
    });
}

if (resendRegisterCodeButton) {
    resendRegisterCodeButton.addEventListener('click', () => {
        const email = document.getElementById('register-email').value;
        const uuid = document.getElementById('id-code').value;

        if (!email || !uuid) {
            showError({title: '錯誤', message: "請輸入您的識別碼和電子郵件"});
            return;
        }

        resendRegisterCodeButton.disabled = true;
        resendRegisterCodeButton.innerHTML = '重發中...<span class="spinner"></span>';

        fetch('/api/v1/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({uuid: uuid, email: email})
        })
        .then(response => response.json())
        .then(data => {
            resendRegisterCodeButton.disabled = false;
            resendRegisterCodeButton.innerHTML = '重發驗證碼';

            if (data.error) {
                showError({title: '錯誤', message: data.error});
            } else {
                alert('驗證碼已重發！');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resendRegisterCodeButton.disabled = false;
            resendRegisterCodeButton.innerHTML = '重發驗證碼';
            showError({title: '錯誤', message: "意外錯誤，請稍後再試"});
        });
    });
}

// Event listeners for code inputs
const codeContainers = document.querySelectorAll('.code-container');
codeContainers.forEach(container => {
    const inputs = container.querySelectorAll('.code-input');
    const containerType = container.closest('.container').getAttribute('id');
    let emailInput;

    if (containerType === 'login-code-container') {
        emailInput = document.getElementById('login-email');
    } else if (containerType === 'register-code-container') {
        emailInput = document.getElementById('register-email');
    }

    inputs.forEach((input, index) => {
        input.addEventListener('input', (e) => {
            const value = e.target.value;

            if (!/^\d$/.test(value)) {
                e.target.value = '';
                return;
            }

            e.target.value = value.slice(0, 1);
            if (index < inputs.length - 1) {
                inputs[index + 1].focus();
            }

            const code = Array.from(inputs).map(input => input.value).join('');
            if (code.length === 8) {
                showProcessingAnimation(container);
                handleCodeSubmission(code, emailInput.value);
            }
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && !e.target.value && index > 0) {
                inputs[index - 1].focus();
            } else if (e.key === 'ArrowLeft' && index > 0) {
                inputs[index - 1].focus();
            } else if (e.key === 'ArrowRight' && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }
        });
    });

    // Add paste event listener to the first input, only once per container
    inputs[0].addEventListener('paste', (e) => {
        e.preventDefault();
        const pasteData = e.clipboardData.getData('text');

        if (!/^\d+$/.test(pasteData)) {
            return;
        }

        const digits = pasteData.slice(0, inputs.length).split('');
        for (let i = 0; i < digits.length && i < inputs.length; i++) {
            inputs[i].value = digits[i];
        }

        // Focus next input or submit if all inputs are filled
        let nextIndex = digits.length;
        if (nextIndex < inputs.length) {
            inputs[nextIndex].focus();
        } else {
            const code = Array.from(inputs).map(input => input.value).join('');
            showProcessingAnimation(container);
            handleCodeSubmission(code, emailInput.value);
        }
    });
});
