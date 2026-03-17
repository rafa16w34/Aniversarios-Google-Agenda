from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pandas as pd

import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


#---------------------------------------------------------------
# Criado por Rafael Alves Faria
# Para meu amigo Chinelo
#---------------------------------------------------------------

df = pd.read_excel("aniversarios.xlsx", engine="openpyxl")

#---------------------------------------------------------------
# AUTENTICAÇÃO
#Importante: Não compartilhar seu token com ninguém

SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES
        )
        creds = flow.run_local_server(port=0)

    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)

#---------------------------------------------------------------
# PEGA TODOS EVENTOS EXISTENTES

eventos_existentes = set()

page_token = None

while True:
    eventos = service.events().list(
        calendarId='primary',
        pageToken=page_token
    ).execute()

    for evento in eventos['items']:
        if 'summary' in evento:
            eventos_existentes.add(evento['summary'])

    page_token = eventos.get('nextPageToken')

    if not page_token:
        break

#---------------------------------------------------------------
# CRIA EVENTOS SOMENTE SE NÃO EXISTIREM

for _, row in df.iterrows():

    titulo = f"Aniversário de {row['Nome']}"

    if titulo in eventos_existentes:
        print(f"Evento já existe: {titulo}")
        continue

    data = pd.to_datetime(row['Aniversário'])

    evento = {
        'summary': titulo,
        'description': f"Telefone: {row['Telefone']}",
        'start': {
            'date': data.strftime('%Y-%m-%d')
        },
        'end': {
            'date': (data + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        },
        'recurrence': [
            'RRULE:FREQ=YEARLY'
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 1440}
            ]
        }
    }

    service.events().insert(
        calendarId='primary',
        body=evento
    ).execute()

    print(f"Evento criado: {titulo}")