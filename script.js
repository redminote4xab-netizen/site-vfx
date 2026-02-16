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

// 1. FUNÇÃO QUE PINTA O MAPA (O que estava faltando)
function atualizarMapaVisual() {
    console.log("Pintando o mapa com novos status...");
    // Esta função procura todos os elementos de lote no seu HTML e troca a cor
    Object.keys(CONFIG_LOTEAMENTO.statusLotes).forEach(idLote => {
        const info = CONFIG_LOTEAMENTO.statusLotes[idLote];
        
        // Tenta encontrar o lote pelo ID (Ex: Lote_1, Lote_2 ou apenas 1, 2)
        const elementoLote = document.getElementById(`lote-${idLote}`) || document.getElementById(idLote);
        
        if (elementoLote) {
            elementoLote.style.fill = info.cor; // Muda a cor do polígono
            elementoLote.setAttribute('fill', info.cor);
        }
    });
}

// 2. FUNÇÃO QUE BUSCA OS DADOS DO PYTHON
async function carregarDadosLoteamento(nomePasta) {
    try {
        // O "?t=" impede que o navegador use dados antigos do cache
        const url = `./${nomePasta}/LOTES.geojson?t=${new Date().getTime()}`;
        const resposta = await fetch(url);
        const dados = await resposta.json();

        CONFIG_LOTEAMENTO.statusLotes = {};

        dados.features.forEach(feature => {
            const props = feature.properties;
            const idLote = String(props.Lote || props.id || props.ID);
            const status = (props.status || "disponivel").toLowerCase();
            
            let corLote = "#2ECC71"; // Verde (Disponível) - Padronizado com seu software
            if (status === "vendido") corLote = "#FF4D4D";   // Vermelho
            if (status === "reservado") corLote = "#F1C40F"; // Amarelo

            CONFIG_LOTEAMENTO.statusLotes[idLote] = {
                status: status,
                cor: corLote,
                obs: props.obs || ""
            };
        });

        console.log(`Dados carregados para: ${nomePasta}`);
        
        // CHAMA A PINTURA DO MAPA
        atualizarMapaVisual();

    } catch (erro) {
        console.error("Erro ao carregar os lotes do GitHub:", erro);
    }
}

// Inicia o sistema
carregarDadosLoteamento('LOTEAMENTO 1');

// ==========================================
// SEUS SCRIPTS DE INTERFACE (MANTIDOS)
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

window.onload = initParticles;