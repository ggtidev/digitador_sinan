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
    # Obtém uma nova conexão com o banco de dados.
    conn = get_connection()
    # Cria um cursor para executar comandos SQL.
    cur = conn.cursor()

    try:
        # Executa o comando SQL UPDATE para alterar o status na tabela 'rpa_notificacoes'.
        # A cláusula WHERE garante que apenas a notificação com o 'num_notificacao' correspondente seja atualizada.
        # Usar parâmetros (%s) previne injeção de SQL.
        cur.execute(
            "UPDATE rpa_notificacoes SET status = %s WHERE num_notificacao = %s",
            (novo_status, num_notificacao)
        )

        # 'rowcount' retorna o número de linhas afetadas pelo último comando.
        # Se nenhuma linha foi afetada, significa que a notificação não foi encontrada.
        if cur.rowcount == 0:
            # Desfaz a transação, embora nenhum dado tenha sido alterado. É uma boa prática.
            conn.rollback()
            # Retorna um dicionário com uma mensagem de erro.
            return {"erro": f"Notificação {num_notificacao} não encontrada."}

        # Se a atualização foi bem-sucedida (pelo menos uma linha afetada),
        # confirma a transação, salvando as alterações permanentemente no banco de dados.
        conn.commit()

        # Retorna uma mensagem de sucesso.
        return {"mensagem": f"Status da notificação {num_notificacao} atualizado para '{novo_status}'."}
        
    finally:
        # O bloco 'finally' garante que o cursor e a conexão sejam sempre fechados,
        # independentemente de ter ocorrido um erro ou não. Isso evita vazamento de recursos.
        if cur:
            cur.close()
        if conn:
            conn.close()


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