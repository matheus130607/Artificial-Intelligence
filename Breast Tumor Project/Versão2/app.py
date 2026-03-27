import os
import json
import asyncio
import uuid
from datetime import datetime
from io import BytesIO
from flask import Flask, request, jsonify, render_template, send_file
from groq import Groq
from dotenv import load_dotenv
import edge_tts

load_dotenv()
chave = os.environ.get("GROQ_API_KEY")
app = Flask(__name__)
client = Groq(api_key=chave)

# ==========================================
# 1. SYSTEM PROMPT PROFISSIONAL E MÉDICO
# ==========================================
SYSTEM_PROMPT = """
Você é o ChatMammo, um assistente virtual altamente profissional, empático e com base científica, especializado em saúde da mulher, com foco absoluto em tumores de mama (benignos e malignos).

DIRETRIZES FUNDAMENTAIS:
1. FOCO RESTRITO: Responda APENAS sobre saúde mamária, nódulos, câncer de mama, prevenção e exames. Se o usuário perguntar sobre outros temas, recuse educadamente e volte ao assunto principal.
2. PRECISÃO CIENTÍFICA: Explique a diferença entre tumores benignos (ex: fibroadenomas, cistos, lipomas) e malignos (ex: carcinomas) com clareza. Use termos médicos corretos, mas explique-os de forma simples e acessível.
3. ISENÇÃO DE RESPONSABILIDADE MÉDICA (CRÍTICO): Você NÃO é médico. Nunca dê diagnósticos definitivos. SEMPRE termine sua resposta orientando a usuária a buscar um mastologista ou ginecologista para avaliação clínica e exames de imagem (ultrassom, mamografia, biópsia).
4. TOM E EMPATIA: Seja acolhedor, calmo e tranquilizador. Muitas usuárias chegam ansiosas. Evite alarmismo.
5. GRÁFICOS E DADOS: Se a pergunta envolver dados (probabilidades, fatores de risco), gere dados ilustrativos coerentes com a literatura médica para um gráfico.

VOCÊ DEVE SEMPRE RESPONDER EXATAMENTE NESTE FORMATO JSON, SEM NENHUM TEXTO FORA DELE:
{
  "texto": "Sua resposta profissional, empática e explicativa aqui.",
  "grafico": {
    "exibir": true, 
    "tipo": "pie", 
    "titulo": "Título do Gráfico",
    "labels": ["Categoria 1", "Categoria 2"],
    "dados": [10, 90]
  }
}
* Se a pergunta NÃO precisar de gráfico, defina "exibir" false.
* O "tipo" pode ser "pie" (pizza) ou "bar" (barras).
"""

ARQUIVO_MEMORIA = "memoria_bot.json"

def carregar_memoria():
    if os.path.exists(ARQUIVO_MEMORIA):
        try:
            with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
                dados = json.load(f)
                # MIGRAR DADOS ANTIGOS (Se for uma lista, transforma no novo formato)
                if isinstance(dados, list):
                    novo_id = str(uuid.uuid4())
                    return {"chats": {novo_id: {"titulo": "Conversa Antiga", "mensagens": dados}}}
                return dados
        except Exception as e:
            print(f"Erro ao carregar a memória: {e}")
            
    return {"chats": {}}

def salvar_memoria_json(memoria):
    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=4)

banco_de_dados = carregar_memoria()

def salvar_conversa_em_arquivo_txt(chat_id, mensagem_usuario, mensagem_bot):
    with open("historico_chats.txt", "a", encoding="utf-8") as arquivo:
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        arquivo.write(f"[{data_atual}] [Chat: {chat_id}]\nUsuário: {mensagem_usuario}\n")
        arquivo.write(f"ChatMammo: {mensagem_bot}\n")
        arquivo.write("-" * 50 + "\n")

@app.route('/')
def home():
    return render_template('index.html')

# --- ROTAS PARA GERENCIAR AS CONVERSAS ---
@app.route('/api/chats', methods=['GET'])
def listar_chats():
    lista = []
    for chat_id, dados in banco_de_dados["chats"].items():
        lista.append({"id": chat_id, "titulo": dados["titulo"]})
    return jsonify(lista)

# ==========================================
# 2. INJEÇÃO DE TREINAMENTO (FEW-SHOT)
# ==========================================
@app.route('/api/chat/novo', methods=['POST'])
def novo_chat():
    chat_id = str(uuid.uuid4())
    banco_de_dados["chats"][chat_id] = {
        "titulo": "Nova Conversa",
        "mensagens": [
            {"role": "system", "content": SYSTEM_PROMPT},
            
            # --- INÍCIO DO TREINAMENTO DE TOM DE VOZ INVISÍVEL ---
            {"role": "user", "content": "Achei um caroço que se move facilmente. Pode ser câncer?"},
            {"role": "assistant", "content": '{\n  "texto": "Entendo que encontrar um nódulo possa causar preocupação, mas tente manter a calma. Nódulos que são bem delimitados e móveis ao toque frequentemente são fibroadenomas ou cistos, que são tumores benignos (não cancerígenos) muito comuns, especialmente em mulheres jovens. Nódulos malignos (câncer) costumam ser mais endurecidos, de contornos irregulares e fixos aos tecidos. No entanto, é impossível dar um diagnóstico apenas pelo toque. Recomendo fortemente que você agende uma consulta com um mastologista para um exame clínico e, se necessário, exames de imagem como ultrassom ou mamografia.",\n  "grafico": {\n    "exibir": false,\n    "tipo": "pie",\n    "titulo": "",\n    "labels": [],\n    "dados": []\n  }\n}'}
            # --- FIM DO TREINAMENTO ---
        ]
    }
    salvar_memoria_json(banco_de_dados)
    return jsonify({"id": chat_id, "titulo": "Nova Conversa"})

# ==========================================
# 3. CARREGAR CHAT (ESCONDENDO O TREINAMENTO)
# ==========================================
@app.route('/api/chat/<chat_id>', methods=['GET'])
def carregar_chat(chat_id):
    chat = banco_de_dados["chats"].get(chat_id)
    if chat:
        # Pula as 3 primeiras mensagens (System Prompt + Pergunta de exemplo + Resposta de exemplo)
        # Assim o frontend acha que o chat está vazio e exibe a mensagem de boas-vindas!
        mensagens_visiveis = chat["mensagens"][3:] if len(chat["mensagens"]) >= 3 else []
        return jsonify({"mensagens": mensagens_visiveis})
    return jsonify({"error": "Chat não encontrado"}), 404

@app.route('/api/chat/<chat_id>', methods=['DELETE'])
def excluir_chat(chat_id):
    if chat_id in banco_de_dados["chats"]:
        del banco_de_dados["chats"][chat_id]
        salvar_memoria_json(banco_de_dados)
        return jsonify({"success": True})
    return jsonify({"error": "Chat não encontrado"}), 404

# --- ROTA DE CHAT ---
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    chat_id = data.get('chat_id', '')

    if not user_message or not chat_id or chat_id not in banco_de_dados["chats"]:
        return jsonify({"error": "Dados inválidos"}), 400

    chat_atual = banco_de_dados["chats"][chat_id]

    # Atualiza o título se for a primeira mensagem real do usuário (ignorando o system e o exemplo)
    if len(chat_atual["mensagens"]) <= 3: 
        chat_atual["titulo"] = user_message[:25] + "..." if len(user_message) > 25 else user_message

    chat_atual["mensagens"].append({"role": "user", "content": user_message})
    salvar_memoria_json(banco_de_dados)

    try:
        chat_completion = client.chat.completions.create(
            messages=chat_atual["mensagens"],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        
        resposta_bruta = chat_completion.choices[0].message.content
        resposta_json = json.loads(resposta_bruta)

        chat_atual["mensagens"].append({"role": "assistant", "content": resposta_bruta})
        salvar_memoria_json(banco_de_dados)

        texto_do_bot = resposta_json.get("texto", "")
        salvar_conversa_em_arquivo_txt(chat_id, user_message, texto_do_bot)

        # Retornamos o título também caso ele tenha acabado de ser atualizado
        resposta_json["titulo"] = chat_atual["titulo"] 
        return jsonify(resposta_json)

    except Exception as e:
        print(f"ERRO: {e}")
        if len(chat_atual["mensagens"]) > 1:
            chat_atual["mensagens"].pop()
            salvar_memoria_json(banco_de_dados)
        return jsonify({"error": "Desculpe, ocorreu um erro."}), 500

@app.route('/tts', methods=['POST'])
def tts():
    data = request.json
    texto = data.get('texto', '')
    if not texto:
        return {"error": "Nenhum texto fornecido"}, 400

    VOZ = "pt-BR-ThalitaNeural"
    async def gerar_audio_em_memoria():
        comunicador = edge_tts.Communicate(texto, VOZ)
        audio_data = b""
        async for chunk in comunicador.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    try:
        audio_bytes = asyncio.run(gerar_audio_em_memoria())
        return send_file(BytesIO(audio_bytes), mimetype="audio/mpeg", as_attachment=False, download_name="audio.mp3")
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)