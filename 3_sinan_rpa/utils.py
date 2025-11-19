# ==========================================================
# File: utils.py
# Versão Final - OpenCV + MSS + Log multilinha + Fluxo de erro completo
# Autor: André Bezerra
# Data: 18/11/2025
# ==========================================================

import pyautogui
import time
import json
import os
import cv2
import mss
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from logger import log_debug, log_erro, log_info
from api_client import registrar_erro

# --- CONFIGURAÇÕES GERAIS ---
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2
pyautogui.MINIMUM_CONFIDENCE = 0.8

load_dotenv()

# Caminhos absolutos
IMAGENS_RPA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "imagens"))
PASTA_ERROS = os.path.abspath(os.path.join(os.path.dirname(__file__), "erros"))
RPA_LOG = os.path.abspath(os.path.join(os.path.dirname(__file__), "rpa_log.txt"))

SAIR_IMG = os.path.join(IMAGENS_RPA_DIR, "sair.png")
NAO_IMG = os.path.join(IMAGENS_RPA_DIR, "nao.png")

os.makedirs(PASTA_ERROS, exist_ok=True)

# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)


def wait_and_click(image_path, timeout=10, intervalo=0.5, confidence=0.9):
    start_time = time.time()
    while True:
        try:
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location:
                pyautogui.click(location)
                log_debug(f"Encontrou e clicou na imagem: {image_path}")
                return True
        except Exception as e:
            log_erro(f"Erro pyautogui ao processar {image_path}: {e}")
        if time.time() - start_time > timeout:
            log_debug(f"Timeout ao procurar imagem: {image_path}")
            return False
        time.sleep(intervalo)


def get_usuario_ativo():
    chave = os.getenv("USUARIO_LOGIN", "USUARIO1").upper()
    username = os.getenv(f"{chave}_USERNAME")
    password = os.getenv(f"{chave}_PASSWORD")
    return username, password


def formatar_unidade_saude(valor):
    if not valor:
        return ""
    partes = valor.strip().split()
    ultimas_duas = partes[-3:] if len(partes) >= 3 else partes
    return f"%{' '.join(ultimas_duas)}%"


def calcular_idade_formatada(data_nascimento_str: str) -> int:
    try:
        nascimento = datetime.strptime(data_nascimento_str, "%d%m%Y")
        hoje = datetime.today()
        idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        return idade
    except Exception:
        return 0


# ==========================================================
# FUNÇÃO DE ABERTURA DO AGRAVO
# ==========================================================

def selecionar_agravo_atual(nome_agravo: str):
    pyautogui.moveTo(x=72, y=59, duration=1)
    pyautogui.click(x=72, y=59)
    time.sleep(1)
    log_debug(f"Focado no menu para reabrir Notificação do Agravo: {nome_agravo}")
    pyautogui.press("enter", clicks=2)
    time.sleep(6)
    log_info("Tela de Notificação Individual reaberta.")


# ==========================================================
# FUNÇÃO DE LOCALIZAÇÃO DE TEMPLATE
# ==========================================================

def localizar_template_rapido_pos(template_path, confidence=0.8):
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = np.array(sct.grab(monitor))
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                return None
            res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val >= confidence:
                h, w = template.shape
                return (max_loc[0], max_loc[1], w, h)
    except Exception as e:
        log_erro(f"Erro ao localizar template {template_path}: {e}")
    return None


# ==========================================================
# FUNÇÃO DE FECHAMENTO DE TELA DE ERRO
# ==========================================================

def fechar_tela_erro():
    """
    Executa a sequência completa após encontrar um erro:
    ESC → SAIR → NÃO → clique fixo → ENTER ×2 → espera 3s
    """
    print("🧩 Executando sequência de fechamento: ESC → SAIR → NÃO → REINICIAR DIGITAÇÃO")
    pyautogui.press('esc')
    time.sleep(1)

    try:
        sair = pyautogui.locateCenterOnScreen(SAIR_IMG, confidence=0.8)
    except pyautogui.ImageNotFoundException:
        sair = None

    if sair:
        pyautogui.click(sair)
        print("   ✅ Botão 'Sair' clicado.")
        time.sleep(1)
    else:
        print("   ⚠️ Botão 'Sair' não encontrado. Continuando fluxo...")

    try:
        nao = pyautogui.locateCenterOnScreen(NAO_IMG, confidence=0.8)
    except pyautogui.ImageNotFoundException:
        nao = None

    if nao:
        pyautogui.click(nao)
        print("   ✅ Botão 'Não' clicado (descartar alterações).")
        time.sleep(1)

        # Clique fixo para garantir foco na tela de Notificação Individual
        pyautogui.click(x=395, y=229)
        print("   🖱️ Clique fixo em (395, 229) para focar na tela de notificação individual.")

        # Pressiona ENTER duas vezes
        pyautogui.press('enter', presses=2, interval=0.5)
        print("   ⌨️ Pressionado ENTER duas vezes para iniciar nova notificação.")

        # Espera 3 segundos
        time.sleep(3)
        print("   ⏳ Aguardando 3 segundos para carregamento da nova ficha...")
        print("   ✅ Pronto para iniciar a próxima notificação.\n")

    else:
        print("   ⚠️ Botão 'Não' não encontrado. Continuando normalmente.")


# ==========================================================
# FUNÇÃO PRINCIPAL DE VERIFICAÇÃO E TRATAMENTO DE ERRO
# ==========================================================

def verificar_e_tratar_erro(num_notificacao: str, agravo: str, tem_proxima=True):
    """
    Detecta pop-ups de erro e realiza o fluxo de correção automatizado.
    Retorna True se erro tratado e precisa reiniciar digitação.
    """
    ERROS_TEMPLATES = [
        os.path.join(IMAGENS_RPA_DIR, f) for f in [
            'erro-01-atencao.png','erro-02-atencao.png','erro-03-informacoes.png',
            'erro-04-popup.png','erro-05-intem_ja_cadastrado.png','erro-05-popup.png',
            'erro-06-opcao-invalida.png','erro-07-atencao_uf.png','erro-08-atencao_so_recebe_valores_numericos.png',
            'erro-10-dt_nascimento_ou_idade_obrigatorio.png','erro-11-dt_invalida.png','erro-12-idade_inferior_ou_superior.png'
        ]
    ]

    for template in ERROS_TEMPLATES:
        try:
            inicio = time.time()
            pos = localizar_template_rapido_pos(template, confidence=0.8)
            duracao = round(time.time() - inicio, 2)

            if pos:
                template_nome = os.path.basename(template)
                log_info(f"⚠️ Erro detectado: {template_nome}")

                # Screenshot e log
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_filename = f"erro_{num_notificacao}_{template_nome}_{timestamp}.png"
                screenshot_path = os.path.join(PASTA_ERROS, screenshot_filename)
                pyautogui.screenshot(screenshot_path)

                with open(RPA_LOG, 'a', encoding='utf-8') as log_file:
                    log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] - Template: {template_nome}\n")
                    log_file.write(f"   Caminho: {template}\n")
                    log_file.write(f"   Tempo de processamento: {duracao}s\n")
                    log_file.write(f"   Resultado: ENCONTRADO\n")

                registrar_erro(num_notificacao)
                log_info(f"Erro registrado para notificação {num_notificacao} na API.")

                # Clique + ESC + fechamento
                #VERIFICAR ISSO AQUI: DEPOIS QUE ELE ABRE UMA NOVA FICHA
                x, y, w, h = pos
                pyautogui.click(x + w // 2, y + h // 2)
                pyautogui.press('esc')
                time.sleep(0.5)

                fechar_tela_erro()

                # Reabre agravo se houver próxima ficha
                if tem_proxima:
                    selecionar_agravo_atual(agravo)

                return True

        except Exception as e:
            log_erro(f"Falha ao tratar template {template}: {e}")
            continue

    return False


# ==========================================================
# FUNÇÃO OPCIONAL PARA LOGAR POSIÇÃO DO MOUSE
# ==========================================================

def log_posicoes_mouse(log_filepath, intervalo=1, duracao=60):
    end_time = time.time() + duracao
    with open(log_filepath, 'a', encoding='utf-8') as log_file:
        log_file.write("Timestamp, X, Y\n")
        while time.time() < end_time:
            x, y = pyautogui.position()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"{timestamp}, {x}, {y}\n")
            time.sleep(intervalo)
