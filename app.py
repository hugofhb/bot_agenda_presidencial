import os

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



# Define a data de hoje
hoje = date.today().strftime('%Y-%m-%d')

# Função para obter os compromissos da agenda presidencial
def get_compromissos_presidenciais():
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

            return eventos
        else:
            return []
    except:
        return None

    
 
compromissos = get_compromissos_presidenciais()

if compromissos:
    print("Compromissos do Presidente da República - " + hoje + ":\n")
    for evento in compromissos:
        print(evento['titulo'] + " - " + evento['inicia_as'] + " - " + evento['local'] + "\n")
else:
    print("Não há compromissos agendados para o Presidente da República - " + hoje + ".")

# Variável global para armazenar os compromissos
compromissos_presidenciais = []
boas_vindas_exibida = []
chat_ids_notificacoes = []
boas_vindas_exibida = False



@app.route("/telegram-bot", methods=["POST"])
def telegram_bot():
    global boas_vindas_exibida
    update = request.json
    chat_id = update["message"]["chat"]["id"]
    message_text = update["message"]["text"]

    if not boas_vindas_exibida:
        # Verifica se a mensagem de boas-vindas já foi exibida
        nova_mensagem = {
            "chat_id": chat_id,
            "text": "👋 Seja bem-vindo ao bot Agenda Presidencial!\n\n"
                    "📌 Digite o número da opção desejada:\n"
                    "1. Ver compromissos do presidente\n"
                    "2. Acessar o site do governo federal para mais detalhes",
            "parse_mode": "MarkdownV2"
        }
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage", json=nova_mensagem)
        boas_vindas_exibida = True

    if message_text == '1':
        compromissos = get_compromissos_presidenciais()
        if compromissos:
            mensagem_compromissos = f"🗓️ Compromissos do presidente em {hoje}:\n\n"
            for evento in compromissos:
                mensagem_compromissos += f"🔸 *{evento['titulo']}*\n"
                mensagem_compromissos += f"    🕒 Início: {evento['inicia_as']}\n"
                mensagem_compromissos += f"    📍 Local: {evento['local']}\n\n"
            nova_mensagem = {
                "chat_id": chat_id,
                "text": mensagem_compromissos,
                "parse_mode": "MarkdownV2"
            }
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage", json=nova_mensagem)
        else:
            nova_mensagem = {
                "chat_id": chat_id,
                "text": f"🤔 O presidente não tem compromissos agendados para hoje ({hoje}).",
                "parse_mode": "MarkdownV2"
            }
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage", json=nova_mensagem)
    elif message_text == '2':
        nova_mensagem = {
            "chat_id": chat_id,
            "text": "🔗 Acesse o site do governo federal para mais detalhes:\n"
                    "https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/agenda-do-presidente-da-republica-lula/agenda-do-presidente-da-republica/",
            "disable_web_page_preview": True,
            "parse_mode": "MarkdownV2"
        }
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage", json=nova_mensagem)
    else:
        nova_mensagem = {
            "chat_id": chat_id,
            "text": "❌ Opção inválida. Por favor, digite '1' para ver os compromissos do presidente ou '2' para acessar o site do governo federal.",
            "parse_mode": "MarkdownV2"
        }
        requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
        
    
    return "ok"
    
   
