from database import get_connection

def atualizar_status(num_notificacao: str, novo_status: str = "concluido"):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE rpa_notificacoes SET status = %s WHERE num_notificacao = %s",
        (novo_status, num_notificacao)
    )

    if cur.rowcount == 0:
        conn.rollback()
        cur.close()
        conn.close()
        return {"erro": f"Notificação {num_notificacao} não encontrada."}

    conn.commit()
    cur.close()
    conn.close()

    return {"mensagem": f"Status da notificação {num_notificacao} atualizado para '{novo_status}'."}


def obter_status(num_notificacao: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT status FROM rpa_notificacoes WHERE num_notificacao = %s",
        (num_notificacao,)
    )

    resultado = cur.fetchone()

    cur.close()
    conn.close()

    if resultado:
        return {"num_notificacao": num_notificacao, "status": resultado[0]}
    return {"erro": f"Notificação {num_notificacao} não encontrada."}
