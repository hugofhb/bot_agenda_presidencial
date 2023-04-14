import os

from datetime import datetime

from flask import Flask, request ,render_template
from tchan import ChannelScraper
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import date, timedelta
import telegram
import pandas as pd
from bs4 import BeautifulSoup



TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]
bot = telegram.Bot(token=os.environ["TELEGRAM_API_KEY"])
TELEGRAM_ADMIN_ID = os.environ["TELEGRAM_ADMIN_ID"]

app = Flask(__name__)

menu = """ 
<a href="/">Página inicial</a> | <a href="/sobre">Sobre</a> |
<br>
"""



@app.route("/sobre")
def sobre():
    return menu + "Aqui vai o conteúdo da página Sobre"



# Obtém a data atual
hoje = datetime.now().strftime("%Y-%m-%d")

def compromissos_presidenciais():
    try:
        # Obtém o conteúdo HTML da página da agenda presidencial
        url = "https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/agenda-do-presidente-da-republica-lula/agenda-do-presidente-da-republica/" + hoje
        response = requests.get(url)
        html = response.content

        # Analisa o HTML para obter as informações relevantes
        soup = BeautifulSoup(html, 'html.parser')

        if soup.find('ul', 'list-compromissos'):
            eventos = []
            lista_compromissos = soup.find('ul', 'list-compromissos')
            for item in lista_compromissos.find_all('div', 'item-compromisso'):
                titulo = item.find('h2', 'compromisso-titulo').text
                inicio = item.find('time', 'compromisso-inicio').text
                local = item.find('div', 'compromisso-local').text
                novo_evento = {
                    'titulo': titulo,
                    'inicia_as': inicio,
                    'local': local
                }
                eventos.append(novo_evento)

            # Atualiza a lista de compromissos
            global compromissos_presidenciais
            compromissos_presidenciais = eventos

            return eventos
        else:
            return []
    except:
        return None


@app.route("/telegram-bot", methods=["POST"])
def telegram_bot():
    update = request.json
    chat_id = update["message"]["chat"]["id"]
    message = update["message"]["text"]

    if message.lower() == '1':
        compromissos = get_compromissos_presidenciais()
        if compromissos:
            mensagem_compromissos = f"🗓️ Compromissos do presidente em {hoje}:\n\n"
            for evento in compromissos:
                mensagem_compromissos += f"🔸 *{evento['titulo']}*\n"
                mensagem_compromissos += f"    🕒 Início: {evento['inicia_as']}\n"
                mensagem_compromissos += f"    📍 Local: {evento['local']}\n\n"
            mensagem = mensagem_compromissos
        else:
            mensagem = f"🤔 O presidente não tem compromissos agendados para hoje ({hoje})."
    elif message.lower() == '2':
        mensagem = "🔗 Acesse o site do governo federal para mais detalhes:\nhttps://www.gov.br/planalto/pt-br/acompanhe-o-planalto/agenda-do-presidente-da-republica-lula/agenda-do-presidente-da-republica/"
    else:
        mensagem = "Escolha uma das opções abaixo:\n1. Ver compromissos do presidente\n2. Acessar o site do governo federal para mais detalhes"

    partes = []
    while mensagem:
        partes.append(mensagem[:4096])
        mensagem = mensagem[4096:]

    for parte in partes:
        nova_mensagem = {
            "chat_id": chat_id,
            "text": parte,
            "parse_mode": "MarkdownV2"
        }
        resposta = requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage", json=nova_mensagem)
        print(resposta.text)

    return "ok"
   
