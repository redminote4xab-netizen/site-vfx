// ==========================================
// PAINEL DE CONTROLE DO LOTEAMENTO (ARLISSON)
// INTEGRADO COM PYTHON + GITHUB
// ==========================================
let CONFIG_LOTEAMENTO = {
    ajustes: {
        anguloTexto: 45,
        exibirMedidas: true
    },
    statusLotes: {} 
};

// FUNÇÃO PARA LIGAR O SITE AO ARQUIVO DO PYTHON
async function carregarDadosLoteamento(nomePasta) {
    try {
        // O "?t=" força o navegador a baixar o arquivo novo do GitHub sem usar o cache antigo
        const resposta = await fetch(`./${nomePasta}/LOTES.geojson?t=${new Date().getTime()}`);
        const dados = await resposta.json();

        CONFIG_LOTEAMENTO.statusLotes = {};

        dados.features.forEach(feature => {
            const idLote = String(feature.properties.Lote || feature.properties.id || feature.properties.ID);
            const status = feature.properties.status || "disponivel";
            
            let corLote = "#00ff00"; // Verde (Disponível)
            if (status === "vendido") corLote = "#ff4d4d"; // Vermelho
            if (status === "reservado") corLote = "#f1c40f"; // Amarelo

            CONFIG_LOTEAMENTO.statusLotes[idLote] = {
                status: status.charAt(0).toUpperCase() + status.slice(1),
                cor: corLote,
                obs: feature.properties.obs || ""
            };
        });

        console.log(`Dados do ${nomePasta} carregados!`, CONFIG_LOTEAMENTO.statusLotes);
        
        // --- COMANDO CRÍTICO: ATUALIZA O MAPA VISUALMENTE ---
        if (typeof renderMap === "function") {
            renderMap(); // Chama a função que desenha os polígonos com as novas cores
        } else if (typeof drawMap === "function") {
            drawMap();
        }
        // --------------------------------------------------

    } catch (erro) {
        console.error("Erro ao carregar os lotes do GitHub:", erro);
    }
}

// Inicia o carregamento
carregarDadosLoteamento('LOTEAMENTO 1');

// ==========================================
// SEUS SCRIPTS ORIGINAIS (MANTIDOS 100%)
// ==========================================
function openTab(evt, tabName) {
    const contents = document.getElementsByClassName("tab-content");
    for (let c of contents) c.classList.remove("active");
    const btns = document.getElementsByClassName("tab-btn");
    for (let b of btns) b.classList.remove("active");
    document.getElementById(tabName).classList.add("active");
    evt.currentTarget.classList.add("active");
}

function toggleDesc(card) {
    card.classList.toggle('active-card');
}

function initParticles() {
    const container = document.getElementById('particles-container');
    if(!container) return; 
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

const s = document.createElement('style');
s.innerHTML = `@keyframes slowMove { 
    0% { transform: translateY(100vh); opacity: 0; } 
    20% { opacity: 0.5; } 
    80% { opacity: 0.5; } 
    100% { transform: translateY(-10vh); opacity: 0; } 
}`;
document.head.appendChild(s);

window.onload = initParticles;