// FUNÇÃO PARA CARREGAR OS DADOS QUE O PYTHON ENVIA
async function carregarStatusLotes() {
    try {
        // O final "?t=" + Date.now() obriga o site a baixar o arquivo novo e ignorar o cache
        const resposta = await fetch('./LOTEAMENTO 1/LOTES.geojson?t=' + Date.now());
        const dados = await resposta.json();

        dados.features.forEach(feature => {
            const idLote = feature.properties.Lote || feature.properties.id;
            const status = feature.properties.status;
            
            // Procura o lote no seu HTML/SVG pelo ID
            const elementoLote = document.getElementById('lote-' + idLote) || document.getElementById(idLote);
            
            if (elementoLote) {
                if (status === 'vendido') elementoLote.style.fill = '#FF4D4D';      // Vermelho
                else if (status === 'reservado') elementoLote.style.fill = '#F1C40F'; // Amarelo
                else elementoLote.style.fill = '#2ECC71';                            // Verde
            }
        });
        console.log("Mapa atualizado com os dados do Python!");
    } catch (erro) {
        console.error("Erro ao ler dados do Python:", erro);
    }
}

// Executa ao abrir o site
carregarStatusLotes();
// Atualiza sozinho a cada 30 segundos para quem estiver com o site aberto
setInterval(carregarStatusLotes, 30000);