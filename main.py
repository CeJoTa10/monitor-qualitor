import os
import time
import requests
from bs4 import BeautifulSoup

# Configurações do Telegram e Qualitor
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8737903636:AAFAHYt9DFATprVRHgPknjmhV1_yNrxgVZc")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1700818551")

QUALITOR_LOGIN_URL = "https://servicedesktic.santacasaba.org.br/login.php?cdlingua=1"
QUALITOR_CHAMADOS_URL = "https://servicedesktic.santacasaba.org.br/html/index.php?cryptget=95t112g111W114g116s97W108x95s61B84qesctjsiWHBUgHgi&idpopup=false"

USUARIO = os.environ.get("QUALITOR_USER", "caio.lima")
SENHA = os.environ.get("QUALITOR_PASS", "@caio123")

chamados_notificados = set()

# Sessão global para reutilizar os cookies do login
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Erro no Telegram: {response.text}")
    except Exception as e:
        print(f"Erro ao enviar para o Telegram: {e}")

def realizar_login():
    payload_login = {
        "cdusuario": USUARIO,
        "cdsenha": SENHA,
        "cdidiomalogin": "1"
    }
    try:
        res_login = session.post(QUALITOR_LOGIN_URL, data=payload_login, timeout=15)
        if res_login.status_code == 200:
            print("Autenticado no Qualitor com sucesso!")
            return True
        else:
            print(f"Falha na tentativa de login no Qualitor. Status: {res_login.status_code}")
            return False
    except Exception as e:
        print(f"Erro ao tentar realizar login: {e}")
        return False

def monitorar_qualitor():
    try:
        # Acessa a página de chamados logado
        res_chamados = session.get(QUALITOR_CHAMADOS_URL, timeout=15)
        
        # Se for redirecionado para a tela de login, refaz a autenticação
        if "login.php" in res_chamados.url or "cdusuario" in res_chamados.text:
            print("Sessão expirada. Efetuando login novamente...")
            if not realizar_login():
                return
            res_chamados = session.get(QUALITOR_CHAMADOS_URL, timeout=15)

        soup = BeautifulSoup(res_chamados.text, "html.parser")

        # Busca pelas linhas da tabela de chamados
        linhas_chamados = soup.find_all("tr", class_="linha_chamado") 

        for linha in linhas_chamados:
            colunas = linha.find_all("td")
            if len(colunas) >= 2:
                chamado_id = colunas[0].text.strip()
                titulo = colunas[1].text.strip()

                if chamado_id not in chamados_notificados:
                    msg = f"🚨 *Novo Chamado no Qualitor!*\n\n*Nº:* `{chamado_id}`\n*Assunto:* {titulo}"
                    enviar_telegram(msg)
                    chamados_notificados.add(chamado_id)

    except Exception as e:
        print(f"Erro durante a execução do monitoramento: {e}")

if __name__ == "__main__":
    print("Iniciando serviço de monitoramento do Qualitor...")
    if realizar_login():
        # Envia mensagem de teste de inicialização para o Telegram
        enviar_telegram("🤖 *Bot do Qualitor iniciado e a monitorar novos chamados!*")
        while True:
            monitorar_qualitor()
            time.sleep(120)  #