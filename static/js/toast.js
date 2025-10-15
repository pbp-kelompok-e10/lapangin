let toastTimeout;

function showToast(title, message, type = 'normal', duration = 4000) {
    const toastComponent = document.querySelector('#toast-component');
    const toastTitle = document.querySelector('#toast-title');
    const toastMessage = document.querySelector('#toast-message');
    const toastIcon = document.querySelector('#toast-icon')
    if (!toastComponent) return;

    clearTimeout(toastTimeout);

    toastComponent.classList.remove(
        'bg-[#FB2C36]', 'border-red-500',
        'bg-[#00C950]', 'border-green-500',
        'bg-white', 'border-gray-300',
    );

    if (type === 'success') {
        toastComponent.classList.add('bg-[#00C950]', 'border-green-500',);
        toastComponent.style.border = '1px solid #22c55e';
        toastIcon.innerHTML =
        `<svg width="34" height="34" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M17 0.333313C7.79504 0.333313 0.333374 7.79497 0.333374 17C0.333374 26.2049 7.79504 33.6666 17 33.6666C26.205 33.6666 33.6667 26.2049 33.6667 17C33.6667 7.79497 26.205 0.333313 17 0.333313ZM23.6667 12C24.0934 12 24.5384 12.1433 24.865 12.4683C25.515 13.12 25.515 14.2133 24.865 14.8649L18.615 21.0633C16.6967 22.9799 13.7651 22.6933 12.2601 20.4366L10.5934 17.9366C10.0834 17.1716 10.2967 16.105 11.0634 15.5933C11.8284 15.0833 12.895 15.2966 13.4067 16.0633L15.0734 18.5633C15.41 19.0683 15.8417 19.1483 16.2701 18.7183L22.4684 12.4683C22.7951 12.1433 23.24 12 23.6667 12Z" fill="white"/>
        </svg>
        `
    } else if (type === 'error') {
        toastComponent.classList.add('bg-[#FB2C36]', 'border-red-500');
        toastComponent.style.border = '1px solid #ef4444';
        toastIcon.innerHTML =
        `<svg width="34" height="34" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M17 0.333313C7.79537 0.333313 0.333374 7.79498 0.333374 17C0.333374 26.205 7.79537 33.6666 17 33.6666C26.205 33.6666 33.6667 26.205 33.6667 17C33.6667 7.79498 26.205 0.333313 17 0.333313ZM12 10.3333C12.4264 10.3333 12.8725 10.4767 13.198 10.8017L17 14.6033L20.8017 10.8017C21.1284 10.4767 21.5734 10.3333 22 10.3333C22.4267 10.3333 22.8717 10.4767 23.1984 10.8017C23.8484 11.4533 23.8484 12.5466 23.1984 13.1983L19.3967 17L23.1984 20.8017C23.8484 21.4533 23.8484 22.5466 23.1984 23.1983C22.5467 23.8483 21.4534 23.8483 20.8017 23.1983L17 19.3967L13.198 23.1983C12.5472 23.8483 11.453 23.8483 10.802 23.1983C10.1512 22.5466 10.1512 21.4533 10.802 20.8017L14.6034 17L10.802 13.1983C10.1512 12.5466 10.1512 11.4533 10.802 10.8017C11.1277 10.4767 11.5735 10.3333 12 10.3333Z" fill="white"/>
        </svg>`

    } else {
        toastComponent.classList.add('bg-white', 'border-gray-300');
        toastComponent.style.border = '1px solid #d1d5db';
    }

    toastTitle.textContent = title;
    toastMessage.textContent = message;

    toastComponent.classList.remove("opacity-0", "-translate-y-64");
    toastComponent.classList.add("opacity-100", "translate-y-0");

    toastTimeout = setTimeout(() => {
        toastComponent.classList.remove("opacity-100", "translate-y-0");
        toastComponent.classList.add("opacity-0", "-translate-y-64");
    }, duration);

}