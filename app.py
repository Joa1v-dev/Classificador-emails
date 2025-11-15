from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from openai import OpenAI
import os

# inicializa o client usando a variável de ambiente
client = OpenAI()

app = Flask(__name__)

def extrair_texto_pdf(arquivo_pdf):
    reader = PdfReader(arquivo_pdf)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() + "\n"
    return texto

def classificar_email(texto_email):
    prompt = f"""
Você é um assistente virtual para uma grande empresa financeira que recebe muitos emails diariamente. 
Seu objetivo é automatizar a leitura, classificação e sugestão de respostas automáticas para cada email.

**Instruções:**
1. Classifique cada email em **PRODUTIVO** ou **IMPRODUTIVO**.
   - PRODUTIVO: solicitações de status, envio de arquivos, dúvidas importantes ou pedidos de serviço.
   - IMPRODUTIVO: felicitações, mensagens irrelevantes ou perguntas que não exigem ação.
2. Gere uma resposta automática adequada.
   - Tom cordial, profissional e objetivo.
   - Para emails improdutivos, responda educadamente, reconhecendo a mensagem.

**Exemplos de classificação e resposta:**

Email: "Gostaria de saber qual o horário de funcionamento da empresa."
Categoria: PRODUTIVO
Resposta: Olá! Nosso horário de funcionamento é de segunda a sexta, das 8h às 17h. Posso ajudá-lo em mais alguma coisa?

Email: "Meu pedido chegou danificado, preciso de uma solução urgente."
Categoria: PRODUTIVO
Resposta: Pedimos desculpas pelo transtorno! Por favor, envie uma foto do item danificado para que possamos resolver o mais rápido possível.

Email: "Feliz Natal! Espero que todos estejam bem."
Categoria: IMPRODUTIVO
Resposta: Agradecemos sua mensagem e desejamos boas festas para você também!

Email: "Vocês nunca respondem nada, empresa horrível!"
Categoria: IMPRODUTIVO
Resposta: Lamentamos que tenha tido essa experiência. Gostaríamos de entender melhor para tentar ajudar. Pode nos enviar mais detalhes?

Agora classifique o seguinte email e gere a resposta:

Email: "{texto_email}"
"""

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        conteudo = resposta.choices[0].message.content
        return conteudo
    except Exception as e:
        print("Erro ao ler resposta:", e)
        return "Categoria: Erro ao processar a resposta\nResposta: Não foi possível gerar resposta."



@app.route("/", methods=["GET", "POST"])
def index():
    categoria = ""
    resposta = ""

    if request.method == "POST":
        texto_email = ""

        if request.form["email_text"]:
            texto_email = request.form["email_text"]

        if "arquivo_pdf" in request.files:
            arquivo_pdf = request.files["arquivo_pdf"]
            if arquivo_pdf.filename.endswith(".txt"):
                texto_email = arquivo_pdf.read().decode("utf-8")
            elif arquivo_pdf.filename.endswith(".pdf"):
                texto_email = extrair_texto_pdf(arquivo_pdf)

        if texto_email:
            saida = classificar_email(texto_email)

            #separando a categoria e a resposta
            try:
                partes = saida.split("Resposta:")
                categoria = partes[0].replace("Categoria:", "").strip()
                resposta = partes[1].strip()
            except:
                categoria = "Erro ao processar a resposta"
                resposta = saida

    return render_template("index.html", categoria=categoria, resposta=resposta)

if __name__ == "__main__":
    app.run(debug=True)

       