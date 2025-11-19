# Importa a função necessária para obter uma conexão com o banco de dados.
# Este módulo 'database' deve conter a lógica para se conectar ao seu banco de dados (ex: PostgreSQL, MySQL, etc.).
from database import get_connection

def atualizar_status(num_notificacao: str, novo_status: str = "concluido"):
    """
    Atualiza o status de uma notificação específica no banco de dados.

    Args:
        num_notificacao (str): O número identificador da notificação a ser atualizada.
        novo_status (str, optional): O novo status a ser atribuído. O valor padrão é "concluido".

    Returns:
        dict: Um dicionário contendo uma mensagem de sucesso ou um erro.
    """
    conn = get_connection()
    cur = conn.cursor()
    sucesso = False

    try:
        # Executa o comando SQL UPDATE para alterar o status na tabela 'rpa_notificacoes'.
        cur.execute(
            "UPDATE rpa_notificacoes SET status = %s WHERE num_notificacao = %s",
            (novo_status, num_notificacao)
        )

        # Se pelo menos uma linha foi afetada, consideramos sucesso.
        if cur.rowcount > 0:
            conn.commit() # Confirma a transação imediatamente após o sucesso
            sucesso = True
            return {"mensagem": f"Status da notificação {num_notificacao} atualizado para '{novo_status}'."}
        else:
            # Se nenhuma linha foi afetada, a notificação não foi encontrada.
            conn.rollback()
            return {"erro": f"Notificação {num_notificacao} não encontrada."}
            
    except Exception as e:
        # Se ocorrer qualquer erro SQL/DB, desfaz a transação e retorna erro.
        conn.rollback()
        return {"erro": f"Erro ao atualizar status da notificação {num_notificacao}: {e}"}
        
    finally:
        # O bloco 'finally' garante que o cursor e a conexão sejam sempre fechados.
        if cur:
            cur.close()
        if conn:
            conn.close()

# A função obter_status permanece inalterada, pois não é a causa do problema de atualização.

def obter_status(num_notificacao: str):
    """
    Obtém o status atual de uma notificação específica do banco de dados.

    Args:
        num_notificacao (str): O número identificador da notificação a ser consultada.

    Returns:
        dict: Um dicionário com o número da notificação e seu status, ou uma mensagem de erro.
    """
    # Obtém uma nova conexão com o banco de dados.
    conn = get_connection()
    # Cria um cursor para executar comandos SQL.
    cur = conn.cursor()

    try:
        # Executa o comando SQL SELECT para buscar o status da notificação.
        # A cláusula WHERE especifica qual notificação buscar.
        cur.execute(
            "SELECT status FROM rpa_notificacoes WHERE num_notificacao = %s",
            (num_notificacao,)  # A vírgula é importante para que o Python entenda como uma tupla.
        )

        # 'fetchone()' recupera a próxima linha do resultado da consulta.
        # Se nenhuma linha for encontrada, retorna None.
        resultado = cur.fetchone()

        # Verifica se um resultado foi encontrado.
        if resultado:
            # Se encontrou, retorna um dicionário com os dados da notificação.
            # resultado[0] contém o valor da primeira coluna selecionada (neste caso, 'status').
            return {"num_notificacao": num_notificacao, "status": resultado[0]}
        
        # Se 'resultado' for None, a notificação não existe.
        return {"erro": f"Notificação {num_notificacao} não encontrada."}

    finally:
        # Garante que o cursor e a conexão sejam sempre fechados após o uso.
        if cur:
            cur.close()
        if conn:
            conn.close()