// 移动端菜单切换
export function initMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
}

// 用户菜单切换
export function initUserMenu() {
    const userMenuButton = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');
    if (userMenuButton && userMenu) {
        userMenuButton.addEventListener('click', function() {
            userMenu.classList.toggle('opacity-0');
            userMenu.classList.toggle('invisible');
        });

        // 点击其他地方关闭用户菜单
        document.addEventListener('click', function(event) {
            if (!userMenuButton.contains(event.target) && !userMenu.contains(event.target)) {
                userMenu.classList.add('opacity-0', 'invisible');
            }
        });
    }
}

// FAQ 折叠功能
export function initFaqToggles() {
    const faqToggles = document.querySelectorAll('.faq-toggle');
    faqToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const icon = this.querySelector('i');

            content.classList.toggle('hidden');
            icon.classList.toggle('rotate-180');
        });
    });
}

// Tab切换逻辑（文本/图片生视频）
export function initTabs() {
    const textTab = document.getElementById('text-to-video-tab');
    const imageTab = document.getElementById('image-to-video-tab');
    const textContent = document.getElementById('text-to-video-content');
    const imageContent = document.getElementById('image-to-video-content');

    if (textTab && imageTab && textContent && imageContent) {
        textTab.addEventListener('click', function() {
            textTab.classList.add('bg-primary/30', 'border-b-2', 'border-primary', 'text-white');
            textTab.classList.remove('text-white/80', 'hover:bg-white/5');
            imageTab.classList.remove('bg-primary/30', 'border-b-2', 'border-primary', 'text-white');
            imageTab.classList.add('text-white/80', 'hover:bg-white/5');
            textContent.classList.remove('hidden');
            imageContent.classList.add('hidden');
        });

        imageTab.addEventListener('click', function() {
            imageTab.classList.add('bg-primary/30', 'border-b-2', 'border-primary', 'text-white');
            imageTab.classList.remove('text-white/80', 'hover:bg-white/5');
            textTab.classList.remove('bg-primary/30', 'border-b-2', 'border-primary', 'text-white');
            textTab.classList.add('text-white/80', 'hover:bg-white/5');
            imageContent.classList.remove('hidden');
            textContent.classList.add('hidden');
        });
    }
}