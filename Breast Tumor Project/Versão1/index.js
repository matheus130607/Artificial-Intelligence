document.addEventListener("DOMContentLoaded", () => {
    const inputField = document.getElementById("userInput");
    const sendButton = document.getElementById("sendBtn");
    const chatHistory = document.getElementById("chatHistory");

    // ==========================================
    // CÉREBRO DO BOT: BANCO DE PALAVRAS-CHAVE
    // ==========================================   
    const botKnowledge = [
        {
            keywords: ["oi", "ola", "olá", "bom dia", "boa tarde", "boa noite", "tudo bem", "start"],
            response: "Olá! Sou o ChatMammo. Estou aqui para ajudar você a entender melhor sobre saúde das mamas, nódulos e prevenção. Sobre o que você gostaria de saber?"
        },
        {
            keywords: ["sintoma", "sintomas", "sinal", "sinais", "dor", "caroco", "caroço", "inchaço", "inchaco", "vermelhidao", "secreção", "secrecao", "mamilo"],
            response: "Os principais sinais de alerta incluem: um caroço (nódulo) fixo e geralmente indolor, pele da mama avermelhada ou retraída (aspecto de casca de laranja), alterações no mamilo, e saída de secreção anormal. Lembre-se: sentir dor nas mamas é muito comum e raramente é sinal de câncer, mas qualquer alteração deve ser vista por um médico."
        },
        {
            keywords: ["mamografia", "ultrassom", "ecografia", "exame", "rastreio", "preventivo", "ressonancia"],
            response: "A mamografia é o principal exame para detecção precoce do câncer de mama, recomendada anualmente para mulheres a partir dos 40 anos. O ultrassom de mamas costuma ser pedido para mulheres mais jovens ou como complemento para analisar nódulos específicos."
        },
        {
            keywords: ["biopsia", "biópsia", "puncao", "punção", "diagnostico", "resultado"],
            response: "A biópsia é o único exame que pode confirmar com 100% de certeza se um nódulo é benigno ou maligno. O médico retira um pequeno pedacinho do tecido com uma agulha para ser analisado no laboratório. É um procedimento rápido e feito com anestesia local."
        },
        {
            keywords: ["benigno", "cisto", "fibroadenoma", "lipoma", "nao e cancer", "não é cancer"],
            response: "Uma ótima notícia é que cerca de 80% dos nódulos na mama são benignos! Os mais comuns são os cistos (bolsas de líquido) e os fibroadenomas (nódulos sólidos). Eles não viram câncer, mas o mastologista pode recomendar acompanhamento."
        },
        {
            keywords: ["maligno", "cancer", "câncer", "tumor", "carcinoma", "sarcoma"],
            response: "Um tumor maligno (câncer) ocorre quando células anormais se multiplicam de forma descontrolada. Os tipos mais comuns são os carcinomas ductais ou lobulares. O diagnóstico precoce é fundamental, pois as chances de cura chegam a 95% quando descoberto no início."
        },
        {
            keywords: ["prevencao", "prevenção", "evitar", "risco", "genetica", "hereditario", "historico familiar", "idade"],
            response: "O risco aumenta com a idade (especialmente após os 50 anos) e com histórico familiar (mãe ou irmã com a doença). Para prevenir, recomenda-se: manter o peso adequado, praticar exercícios, evitar o excesso de álcool e realizar seus exames de rotina (mamografia)."
        },
        {
            keywords: ["tratamento", "cirurgia", "quimioterapia", "quimio", "radioterapia", "radio", "mastectomia", "remedio"],
            response: "O tratamento varia muito dependendo do tipo e estágio do tumor. Pode incluir cirurgia (retirada do nódulo ou da mama), radioterapia, quimioterapia ou hormonioterapia. Hoje em dia, os tratamentos são muito personalizados e focados na qualidade de vida da paciente."
        },
        {
            keywords: ["obrigado", "obrigada", "valeu", "tchau", "adeus", "ate logo"],
            response: "Por nada! Lembre-se que sou apenas um assistente virtual e não substituo uma consulta médica. Cuide-se bem, faça o autoexame e visite seu ginecologista ou mastologista regularmente. Até a próxima!"
        }
    ];

    // Função para adicionar mensagens
    function addMessage(text, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message");
        
        if (sender === "user") {
            messageDiv.classList.add("user-message");
        } else {
            messageDiv.classList.add("bot-message");
        }
        
        messageDiv.textContent = text;
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight; // Rola para o final
    }

    // Função para procurar a resposta
    function getBotResponse(userText) {
        const textLower = userText.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        let finalResponse = "Desculpe, não entendi muito bem. Você poderia usar palavras mais específicas? Tente perguntar sobre 'sintomas', 'mamografia', 'biópsia', 'cisto' ou 'tratamento'.";

        for (let item of botKnowledge) {
            let found = item.keywords.some(keyword => {
                const cleanKeyword = keyword.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                return textLower.includes(cleanKeyword);
            });

            if (found) {
                finalResponse = item.response;
                break;
            }
        }

        // Simula digitação (1 segundo)
        setTimeout(() => {
            addMessage(finalResponse, "bot");
        }, 1000);
    }

    // Função para tratar o envio
    function handleSend() {
        const text = inputField.value.trim();
        if (text === "") return;

        addMessage(text, "user");
        inputField.value = "";
        getBotResponse(text);
    }

    // Cliques e Teclado
    sendButton.addEventListener("click", handleSend);
    inputField.addEventListener("keypress", (e) => {
        if (e.key === "Enter") handleSend();
    });
});