from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import openai
import os

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


app = Flask(__name__)

#configuração da API
openai.api_key = os.getenv("OPENAI_API_KEY")

def extrair_texto_pdf(arquivo_pdf):
    reader = PdfReader(arquivo_pdf)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() + "\n"
    return texto

from openai import OpenAI
client = OpenAI()

def classificar_email(texto_email):
    prompt = f"""
    Classifique o email abaixo como PRODUTIVO ou IMPRODUTIVO.
    Em seguida gere uma resposta automática apropriada.

    Retorne exatamente neste formato:

    Categoria: <PRODUTIVO/IMPRODUTIVO>
    Resposta: <TEXTO DA RESPOSTA>

    Email:
    {texto_email}
    """

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Segurança extra: captura independente do formato
    try:
        conteudo = resposta.choices[0].message["content"]
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

       