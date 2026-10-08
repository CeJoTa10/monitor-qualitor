import requests
import time

# Configurações do Telegram
TELEGRAM_TOKEN = "8737903636:AAFAHYt9DFATprVRHgPknjmhV1_yNrxgVZc"
CHAT_ID = "@MeusChamados_bot"

# IDs já notificados para não repetir
chamados_notificados = set()

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar para o Telegram: {e}")

def verificar_chamados():
    # -------------------------------------------------------------
    # Exemplo via API REST do Qualitor (caso sua empresa tenha chave/token)
    # -------------------------------------------------------------
    url_qualitor = "http://qualitor.suaempresa.local/api/v1/chamados"
    headers = {"Authorization": "Bearer SEU_TOKEN_QUALITOR"}
    
    try:
        response = requests.get(url_qualitor, headers=headers, timeout=10)
        if response.status_code == 200:
            chamados = response.json() # Ajuste conforme o JSON retornado pelo Qualitor
            
            for chamado in chamados:
                chamado_id = chamado.get("cd_chamado")
                titulo = chamado.get("ds_chamado")
                
                if chamado_id not in chamados_notificados:
                    msg = f"🚨 *Novo Chamado Qualitor!*\n\n*Nº:* {chamado_id}\n*Título:* {titulo}"
                    enviar_telegram(msg)
                    chamados_notificados.add(chamado_id)
    except Exception as e:
        print(f"Erro ao consultar o Qualitor: {e}")

# Loop de monitoramento (ex: a cada 2 minutos)
if __name__ == "__main__":
    while True:
        verificar_chamados()
        time.sleep(120)