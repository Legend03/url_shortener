// Функция для изменения цвета header
function updateHeaderStyle() {
    const header = document.querySelector('header');
    const featuresSection = document.querySelector('.features');

    if (!featuresSection) return;

    const featuresTop = featuresSection.offsetTop;
    const scrollPosition = window.scrollY + 100;

    if (scrollPosition >= featuresTop) {
        header.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';

    } else {
        header.style.background = 'rgba(255, 255, 255, 0.1)';
        header.style.backdropFilter = 'blur(10px)';
    }
}

document.addEventListener('DOMContentLoaded', updateHeaderStyle);
window.addEventListener('scroll', updateHeaderStyle);
window.addEventListener('resize', updateHeaderStyle);