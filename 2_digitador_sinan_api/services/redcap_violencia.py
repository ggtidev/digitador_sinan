from database import get_connection
from collections import OrderedDict
from utils.utils import formatar_data, formatar_sexo, get_labels_map, formatar_deficiencia, formatar_vio_trabalho, remover_acentos_recursivo

REDCAP_TOKEN = '15A28A0BA2CFF32380E87F2003FDA610'
REDCAP_URL = 'https://redcap.recife.pe.gov.br/api/'

labels_map = get_labels_map()

def map_to_rpa_format(raw_data):
    notificacao_fields = {
        "dt_not_vio": "data_notificacao",
        "nm_pct_vio": "nome_paciente",
        "dt_ocor_vio": "data_ocorrencia",
        "dt_nasc_violencia": "data_nascimento",
        "id_vio": "idade",
        "sexo_vio": "sexo",
        "gest_vio": "gestante",
        "raca_cor_vio": "raca",
        "escol_vio": "escolaridade",
        "sus_vio": "cartao_sus",
        "nm_mae_vio": "nome_mae",
        "uf_resid_vio": "uf_residencia_vio",
        "mun_resid_vio_lista": "municipio_residencia",
        "mun_notif_vio": "mun_notificacao_vio",
        "tel_notif_vio": "telefone_uni_notif",
        "ds_resid": "distrito_residencia",
        "bairro_vio": "bairro_residencia",
        "log_vio": "endereco_residencia",
        "num_resid_vio": "numero_residencia",
        "comp_vio": "complemento_residencia",
        "cep_vio": "cep_residencia",
        "tel_vio": "telefone",
        "un_not_vio": "unidade_notificadora",
        "nm_notif_vio": "nome_notificador",
        "idade_calc_vio": "idade_calculada_notificador",
        "us_vio": "nome_unidade_saude",
        "nm_un_vio": "nome_unidade_notificadora",
    }

    investigacao_fields = {
        "ocup_vio": "ocupacao",
        "cpf_vio":"cpf_vio",
        "sit_conj_vio": "estado_civil",
        "orient_vio": "orientacao_sexual",
        "def_transt_vio": "deficiencia",
        "viol_1": "deficiencia_fisica",
        "viol_2": "deficiencia_intelectual",
        "viol_3": "deficiencia_visual",
        "viol_4": "deficiencia_auditiva",
        "viol_5": "deficiencia_mental",
        "viol_6":"transtorno_comportamento",
        "viol_7":"outras_deficiencias",
        "qual_defic": "tipo_deficiencia",
        "out_def_vio": "outra_deficiencia",
        "uf_ocor_vio": "uf_ocorrencia",
        "gen_vio": "identidade_genero",
        "mun_ocor_vio": "municipio_ocorrencia",
        
        "bairro_ocor_vio": "bairro_ocorrencia",
        "log_ocor_vio": "endereco_ocorrencia",
        "num_ocor_vio": "numero_ocorrencia",
        "comp_ocor_vio": "complemento_ocorrencia",
        "hora_ocor_vio": "horario_ocorrencia",
        "local_oc_vio": "local_ocorrencia",
        "out_loc_vio": "outro_local",
        "vezes_vio": "ocorreu_outras_vezes",
        "lesao_auto": "lesao_autoprovocada",
        "motiv_vio": "motivo_violencia",
        "tp_viol": "tipo_violencia",
        "out_tp_viol": "esp_outro_tipo_violencia",
        "meio_agres": "meio_agressao",
        "out_agres_vio": "esp_outro_meio_agressao",
        "nm_env_vio": "numero_envolvidos",
        "grau_parent": "grau_parentesco",
        "out_vinc_vio": "outro_vinculo",
        "sex_autor_vio": "sexo_agressor",
        "alcool_vio": "suspeita_alcool",
        "ciclo_aut_vio": "ciclo_vida_autor",
        "encaminh_viol": "encaminhamento",
        "rel_trab_vio": "relacao_trabalho",
        "dt_encerra_viole": "data_encerramento",
        "obs_vio": "observacoes",
        "cep_ocor_vio": "cep_ocor_vio",
        "cep_vio_2": "cep_ocor_vio2",
        "comp_vio_2": "complemento_ocor_vio",
        "dt_nas_vio": "dt_nascimento_vio",
        "fun_notif_vio": "funcao_notificador",
        "log_vio_2": "logradouro_ocor_vio",
        "num_resid_vio_2": "numero_residencia_ocor_vio",
        "situ_rua_vio": "situacao_rua_vio",
        "uf_notif_vio": "uf_notificacao_vio",
        "viol_10": "tortura",
        "viol_12": "trafico_pessoas",
        "viol_13": "financeiro",
        "viol_14": "negligencia_abandono",
        "viol_15": "trabalho_infantil",
        "viol_16": "intervencao_legal",
        "viol_17": "outro_tipo_violencia",
        "viol_18": "forca_corporal_espancamento",
        "viol_19": "enforcamento",
        "viol_20": "objeto_contundente",
        "viol_21": "objeto_perfurante",
        "viol_22": "objeto_quente",
        "viol_23": "envenenamento",
        "viol_24": "arma_fogo",
        "viol_25": "ameaca",
        "viol_26": "outro_meio_agressao",
        "viol_40": "pai",
        "viol_41": "mae",
        "viol_42": "padrasto",
        "viol_43": "madrasta",
        "viol_44": "conjuge_parceiro",
        "viol_45": "ex_conjuge_parceiro",
        "viol_46": "namorado",
        "viol_47": "ex_namorado",
        "viol_48": "filho",
        "viol_49": "irmao",
        "viol_50": "amigos_conhecidos",
        "viol_51": "desconhecido",
        "viol_52": "cuidador",
        "viol_53": "patrao_chefe",
        "viol_54": "pessoa_relacao_instituicao",
        "viol_55": "policial_agente",
        "viol_56": "propria_pessoa",
        "viol_57": "outros_envolvidos",
        "out_vinc_vio": "esp_outros_envolvidos",
        "viol_60": "rede_saude",
        "viol_61": "rede_assistencia_social",
        "viol_62": "rede_educacao",
        "viol_63": "rede_atendimento_mulher",
        "viol_64": "conselho_tutelar",
        "viol_65": "conselho_idoso",
        "viol_66": "delegacia_atendimento_idoso",
        "viol_67": "centro_ref_direitos_humanos",
        "viol_68": "ministerio_publico",
        "viol_69": "delegacia_especializada_infancia",
        "viol_70": "delegacia_atendimento_mulher",
        "viol_71": "outras_delegacias",
        "viol_72": "justica_infancia_juventude",
        "viol_73": "defensoria_publica",
        "viol_8": "fisica",
        "viol_9": "moral_psicologica",
    }

    notificacao, investigacao, outros = {}, {}, {}

    for k, v in raw_data.items():
        if k in notificacao_fields:
            campos_sexo = ["sexo_vio", "sex_autor_vio", "sexo_notificador_vio"]
            if k in campos_sexo:
                valor = formatar_sexo(v)
            elif "dt_" in k:
                valor = formatar_data(v)
            elif k in labels_map:
                valor = labels_map[k].get(v, v)
            else:
                valor = v
            notificacao[notificacao_fields[k]] = valor

        elif k in investigacao_fields:
            if k == "motiv_vio":
                if v == "10":
                    valor = "88"
                elif v == "11":
                    valor = "99"
                else:
                    valor = v
            elif "dt_" in k:
                valor = formatar_data(v)
            elif k == "def_transt_vio":
                valor = formatar_deficiencia(v)
            elif k == "rel_trab_vio":
                valor = formatar_vio_trabalho(v)
            elif k in labels_map:
                valor = labels_map[k].get(v, v)
            else:
                valor = v
            investigacao[investigacao_fields[k]] = valor

        else:
            outros[k] = v

    resultado = {
        "agravo": "VIOLENCIA_INTERPESSOAL_AUTOPROVOCADA",
        "notificacao": notificacao,
        "investigacao": investigacao,
        "outros": outros
    }
    
    return remover_acentos_recursivo(resultado)
    

def get_redcap_filas():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT v.record, v.num_notificacao, v.status, d.field_name, d.value
        FROM rpa_notificacoes v
        JOIN rpa_notificacao_detalhes d ON v.id = d.rpa_notificacao_id
        WHERE v.status = 'pendente'
        ORDER BY v.record::int, d.field_name;
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    filas = {}
    for record, num_notificacao, status, field, value in rows:
        if record not in filas:
            filas[record] = {
                "num_notificacao": num_notificacao,
                "status": status,
                "dados": {}
            }
        filas[record]["dados"][field] = value

    filas_formatadas = []
    for fila in filas.values():
        dado_formatado = map_to_rpa_format(fila["dados"])

        ordenado = OrderedDict()
        ordenado["agravo"] = dado_formatado["agravo"]
        ordenado["num_notificacao"] = fila["num_notificacao"]
        ordenado["status"] = fila["status"]
        ordenado["notificacao"] = dado_formatado["notificacao"]
        ordenado["investigacao"] = dado_formatado["investigacao"]
        ordenado["outros"] = dado_formatado["outros"]

        filas_formatadas.append(ordenado)

    return filas_formatadas