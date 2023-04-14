import os

from flask import Flask, request ,render_template
from tchan import ChannelScraper
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import date, timedelta
import telegram
import pandas as pd


TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]
bot = telegram.Bot(token=os.environ["TELEGRAM_API_KEY"])
TELEGRAM_ADMIN_ID = os.environ["TELEGRAM_ADMIN_ID"]

app = Flask(__name__)

menu = """ 
<a href="/">Página inicial</a> | <a href="/sobre">Sobre</a> |
<br>
"""

@app.route("/")
def index():
    menu = """<a href="/">Página inicial</a> | <a href="/sobre">Sobre</a> |"""
    projetos = projetos_aprovados()
    return menu + "Olá, este é o site do robô sobre PLs aprovadas.<br><br>Projetos de Lei Aprovados:<br>" + "<br>".join(projetos)

@app.route("/sobre")
def sobre():
    return menu + "Aqui vai o conteúdo da página Sobre"
