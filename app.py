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
Você é um assistente que classifica emails como PRODUTIVO ou IMPRODUTIVO e gera uma resposta apropriada.
Use sempre o seguinte formato:

Categoria: <PRODUTIVO/IMPRODUTIVO>
Resposta: <texto da resposta>

Aqui estão alguns exemplos:

Email: "Gostaria de saber qual o horário de funcionamento da empresa."
Categoria: PRODUTIVO
Resposta: Olá! Nosso horário de funcionamento é de segunda a sexta, das 8h às 17h. Posso te ajudar em mais alguma coisa?

Email: "Meu pedido chegou danificado, preciso de uma solução urgente."
Categoria: IMPRODUTIVO
Resposta: Pedimos desculpas pelo transtorno! Por favor, envie uma foto do item danificado para que possamos resolver.

Agora classifique o seguinte email:

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

       