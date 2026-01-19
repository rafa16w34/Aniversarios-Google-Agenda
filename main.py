from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pandas as pd

# Lê a planilha
df = pd.read_excel("aniversarios.xlsx", engine="openpyxl")


SCOPES = ['https://www.googleapis.com/auth/calendar']

# Autenticação
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES
)
creds = flow.run_local_server(port=0)

service = build('calendar', 'v3', credentials=creds)

# Criação dos eventos
for _, row in df.iterrows():
    data = pd.to_datetime(row['Aniversário'])

    evento = {
        'summary': f"🎂 Aniversário de {row['Nome']}",
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
