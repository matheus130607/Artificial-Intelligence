import os
import json
from flask import Flask, request, jsonify, render_template
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
chave = os.environ.get("GROQ_API_KEY")
app = Flask(__name__)
client = Groq(api_key=chave)

# Novo System Prompt: Agora ele é treinado para retornar um JSON estruturado
SYSTEM_PROMPT = """
Você é o ChatMammo, um assistente virtual empático especializado em tumores de mama.

DIRETRIZES:
1. Você não é médico. Recomende a busca por um profissional.
2. Seja acolhedor e objetivo.
3. Se a pergunta envolver estatísticas, probabilidades, fatores de risco ou comparações, gere dados ilustrativos para um gráfico.

VOCÊ DEVE SEMPRE RESPONDER EXATAMENTE NESTE FORMATO JSON, SEM NENHUM TEXTO FORA DELE:
{
  "texto": "Sua resposta amigável e explicativa aqui.",
  "grafico": {
    "exibir": true, 
    "tipo": "pie", 
    "titulo": "Título do Gráfico (ex: Probabilidade ao longo da vida)",
    "labels": ["Categoria 1", "Categoria 2"],
    "dados": [12, 88]
  }
}
* Se a pergunta NÃO precisar de gráfico, defina "exibir" como false.
* O "tipo" pode ser "pie" (pizza) ou "bar" (barras).
"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "Mensagem vazia"}), 400

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=1024,
            response_format={"type": "json_object"} # Isso força o Groq a não errar o formato!
        )
        
        # Lê a resposta do Groq e transforma de texto para um dicionário Python
        resposta_bruta = chat_completion.choices[0].message.content
        resposta_json = json.loads(resposta_bruta)

        return jsonify(resposta_json)

    except Exception as e:
        print(f"ERRO: {e}")
        return jsonify({"error": "Desculpe, ocorreu um erro."}), 500

if __name__ == '__main__':
    app.run(debug=True)