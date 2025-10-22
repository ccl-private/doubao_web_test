import { translations, changeLanguage } from './i18n.js';
import { initMobileMenu, initUserMenu, initFaqToggles, initTabs } from './ui.js';
import { initModals, openLoginModal, closeLoginModal } from './modals.js';
import { initTextVideoGenerator, initImageVideoGenerator } from './video-generator.js';
import { verifyToken, loginUser, registerUser } from './api.js';

// 登录状态切换
export function showLoggedInState() {
    document.getElementById('login-link')?.classList.add('hidden');
    document.getElementById('register-link')?.classList.add('hidden');
    document.getElementById('user-logged-in')?.classList.remove('hidden');
}

export function hideLoggedInState() {
    document.getElementById('login-link')?.classList.remove('hidden');
    document.getElementById('register-link')?.classList.remove('hidden');
    document.getElementById('user-logged-in')?.classList.add('hidden');
}

// 页面加载时检查用户登录状态
function checkLoginStatus() {
    const token = localStorage.getItem('token');
    if (token) {
        verifyToken(token)
            .then(response => {
                // 令牌有效，显示登录状态
                showLoggedInState();
            })
            .catch(error => {
                // 令牌无效，清除本地存储
                console.error('令牌验证失败:', error);
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                hideLoggedInState();
            });
    }
}

// 初始化登录表单提交
function initLoginForm() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            try {
                // 调用登录API
                const response = await loginUser(email, password);

                // 保存令牌和用户信息
                localStorage.setItem('token', response.token);
                localStorage.setItem('user', JSON.stringify(response.user));

                // 显示成功消息
                alert('登录成功！');

                // 关闭模态框
                closeLoginModal();

                // 更新UI显示登录状态
                showLoggedInState();
            } catch (error) {
                alert(`登录失败: ${error.message}`);
            }
        });
    }
}

// 初始化注册表单提交
function initRegisterForm() {
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const name = document.getElementById('register-name').value;
            const email = document.getElementById('register-email').value;
            const password = document.getElementById('register-password').value;
            const confirmPassword = document.getElementById('register-confirm-password').value;

            // 验证密码是否一致
            if (password !== confirmPassword) {
                alert('两次输入的密码不一致，请重新输入');
                return;
            }

            try {
                // 调用注册API
                await registerUser(name, email, password);

                // 显示成功消息
                alert('注册成功！请登录');

                // 关闭注册模态框
                closeLoginModal();

                // 打开登录模态框
                setTimeout(() => {
                    openLoginModal();
                }, 500);
            } catch (error) {
                alert(`注册失败: ${error.message}`);
            }
        });
    }
}

// 初始化退出登录
function initLogout() {
    const logoutLink = document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();

            // 清除本地存储
            localStorage.removeItem('token');
            localStorage.removeItem('user');

            // 更新UI显示未登录状态
            hideLoggedInState();

            alert('已成功退出登录');
        });
    }
}

// 初始化语言切换事件
function initLanguageSwitch() {
    const langOptions = document.querySelectorAll('.lang-option');
    const currentLangElement = document.getElementById('current-lang');

    langOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            const lang = this.getAttribute('data-lang');
            changeLanguage(lang);

            // 更新当前语言显示
            currentLangElement.textContent = this.textContent;
        });
    });
}

// 总初始化函数
function init() {
    // 初始化UI组件
    initMobileMenu();
    initUserMenu();
    initFaqToggles();
    initTabs();
    initModals();

    // 初始化表单
    initLoginForm();
    initRegisterForm();

    // 初始化视频生成功能
    initTextVideoGenerator();
    initImageVideoGenerator();

    // 初始化语言切换
    initLanguageSwitch();

    // 初始化退出登录
    initLogout();

    // 检查登录状态
    checkLoginStatus();
}

// DOM加载完成后执行初始化
document.addEventListener('DOMContentLoaded', init);