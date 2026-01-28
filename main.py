from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pandas as pd

#----------------------------------------------------------------
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request



#Criado por Rafael Alves Faria
#Para meu caro amigo Chinelo
#---------------------------------------------------------------

# Lê a planilha 
df = pd.read_excel("aniversarios.xlsx", engine="openpyxl")


#---------------------------------------------------------------


#Parte do criação das credenciais da conta google
#IMPORTANTE: NUNCA COMPARTILHE O TOKEN.JSON

SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None

# Se já existir token salvo
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

# Se não existir ou estiver inválido
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES
        )
        creds = flow.run_local_server(port=0)

    # Salva o token para próximas execuções
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# Cria o serviço do Google Calendar
service = build('calendar', 'v3', credentials=creds)

#---------------------------------------------------------------

for _, row in df.iterrows():
    data = pd.to_datetime(row['Aniversário'])

    evento = {
        'summary': f" Aniversário de {row['Nome']}",
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
                {'method': 'popup', 'minutes': 1440}  # 1 dia antes
            ]
        }
    }

    service.events().insert(
        calendarId='primary',
        body=evento
    ).execute()
