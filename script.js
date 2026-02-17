// 1. Função de Controle das Abas
function openTab(evt, tabName) {
    const contents = document.getElementsByClassName("tab-content");
    for (let c of contents) c.classList.remove("active");
    const btns = document.getElementsByClassName("tab-btn");
    for (let b of btns) b.classList.remove("active");
    document.getElementById(tabName).classList.add("active");
    evt.currentTarget.classList.add("active");
}

// 2. Toggle de Descrição dos Cards
function toggleDesc(card) {
    card.classList.toggle('active-card');
}

// 3. Sistema de Partículas
function initParticles() {
    const container = document.getElementById('particles-container');
    if (!container) return; // Evita erro se o container não existir
    for (let i = 0; i < 75; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const size = Math.random() * 3 + 1 + 'px';
        p.style.width = p.style.height = size;
        p.style.top = Math.random() * 100 + '%';
        p.style.left = Math.random() * 100 + '%';
        p.style.animation = `slowMove ${Math.random() * 15 + 20}s linear infinite`;
        container.appendChild(p);
    }
}

// Estilos das Partículas
const s = document.createElement('style');
s.innerHTML = `@keyframes slowMove { 
    0% { transform: translateY(100vh); opacity: 0; } 
    20% { opacity: 0.5; } 
    80% { opacity: 0.5; } 
    100% { transform: translateY(-10vh); opacity: 0; } 
}`;
document.head.appendChild(s);

// 4. Lógica de Abertura (Intro Overlay) e Inicialização
window.onload = function() {
    // Inicia suas partículas (mantendo seu código original)
    initParticles();

    // Faz a abertura preta sumir com opacidade
    const abertura = document.getElementById('abertura-simples');
    if (abertura) {
        // Um pequeno delay de 500ms antes de começar a transparência
        setTimeout(() => {
            abertura.classList.add('sumir');
        }, 500);
    }
};