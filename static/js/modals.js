// 登录模态框控制
export function openLoginModal() {
    const loginModal = document.getElementById('login-modal');
    const loginModalContent = document.getElementById('login-modal-content');
    const registerModal = document.getElementById('register-modal');

    if (loginModal && loginModalContent && registerModal) {
        // 先关闭注册模态框
        registerModal.classList.add('hidden');
        registerModal.classList.remove('flex');

        // 显示登录模态框
        loginModal.classList.remove('hidden');
        loginModal.classList.add('flex');

        // 动画效果
        setTimeout(() => {
            loginModalContent.classList.remove('scale-95', 'opacity-0');
            loginModalContent.classList.add('scale-100', 'opacity-100');
        }, 10);
    }
}

export function closeLoginModal() {
    const loginModal = document.getElementById('login-modal');
    const loginModalContent = document.getElementById('login-modal-content');

    if (loginModal && loginModalContent) {
        // 动画效果
        loginModalContent.classList.remove('scale-100', 'opacity-100');
        loginModalContent.classList.add('scale-95', 'opacity-0');

        // 隐藏模态框
        setTimeout(() => {
            loginModal.classList.remove('flex');
            loginModal.classList.add('hidden');
        }, 300);
    }
}

// 注册模态框控制
export function openRegisterModal() {
    const registerModal = document.getElementById('register-modal');
    const registerModalContent = document.getElementById('register-modal-content');
    const loginModal = document.getElementById('login-modal');

    if (registerModal && registerModalContent && loginModal) {
        // 先关闭登录模态框
        loginModal.classList.add('hidden');
        loginModal.classList.remove('flex');

        // 显示注册模态框
        registerModal.classList.remove('hidden');
        registerModal.classList.add('flex');

        // 动画效果
        setTimeout(() => {
            registerModalContent.classList.remove('scale-95', 'opacity-0');
            registerModalContent.classList.add('scale-100', 'opacity-100');
        }, 10);
    }
}

export function closeRegisterModal() {
    const registerModal = document.getElementById('register-modal');
    const registerModalContent = document.getElementById('register-modal-content');

    if (registerModal && registerModalContent) {
        // 动画效果
        registerModalContent.classList.remove('scale-100', 'opacity-100');
        registerModalContent.classList.add('scale-95', 'opacity-0');

        // 隐藏模态框
        setTimeout(() => {
            registerModal.classList.remove('flex');
            registerModal.classList.add('hidden');
        }, 300);
    }
}

// 初始化模态框事件监听
export function initModals() {
    // 登录链接点击事件
    const loginLink = document.getElementById('login-link');
    if (loginLink) {
        loginLink.addEventListener('click', function(e) {
            e.preventDefault();
            openLoginModal();
        });
    }

    // 注册链接点击事件
    const registerLink = document.getElementById('register-link');
    if (registerLink) {
        registerLink.addEventListener('click', function(e) {
            e.preventDefault();
            openRegisterModal();
        });
    }

    // CTA注册按钮点击事件
    const ctaRegister = document.getElementById('cta-register');
    if (ctaRegister) {
        ctaRegister.addEventListener('click', function(e) {
            e.preventDefault();
            openRegisterModal();
        });
    }

    // 模态框内的注册链接点击事件
    const modalRegisterLink = document.getElementById('modal-register-link');
    if (modalRegisterLink) {
        modalRegisterLink.addEventListener('click', function(e) {
            e.preventDefault();
            openRegisterModal();
        });
    }

    // 模态框内的登录链接点击事件
    const modalLoginLink = document.getElementById('modal-login-link');
    if (modalLoginLink) {
        modalLoginLink.addEventListener('click', function(e) {
            e.preventDefault();
            openLoginModal();
        });
    }

    // 关闭登录模态框按钮点击事件
    const closeLoginModalBtn = document.getElementById('close-login-modal');
    if (closeLoginModalBtn) {
        closeLoginModalBtn.addEventListener('click', closeLoginModal);
    }

    // 关闭注册模态框按钮点击事件
    const closeRegisterModalBtn = document.getElementById('close-register-modal');
    if (closeRegisterModalBtn) {
        closeRegisterModalBtn.addEventListener('click', closeRegisterModal);
    }

    // 点击登录模态框外部关闭
    const loginModal = document.getElementById('login-modal');
    if (loginModal) {
        loginModal.addEventListener('click', function(e) {
            if (e.target === loginModal) {
                closeLoginModal();
            }
        });
    }

    // 点击注册模态框外部关闭
    const registerModal = document.getElementById('register-modal');
    if (registerModal) {
        registerModal.addEventListener('click', function(e) {
            if (e.target === registerModal) {
                closeRegisterModal();
            }
        });
    }
}