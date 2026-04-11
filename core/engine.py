"""
Engine Groq para AppGuard - Versão RAG Robusta
Foco: Imparcialidade Analítica e Doutrina Jurídica
"""
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
import streamlit as st
from core.prompts import SYSTEM_PROMPT, TRIAAGEM_PROMPT, ESQUELETO_PROMPT

# load_dotenv() - Não é necessário no Streamlit Cloud
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        # Tenta pegar das variáveis de ambiente como fallback
        import os
        key = os.getenv("GROQ_API_KEY")
        if key:
            client = Groq(api_key=key)
        else:
            client = None
            st.error("🚨 ERRO: A chave 'GROQ_API_KEY' não foi encontrada.")
            st.write("🔍 **Chaves detectadas nos Secrets:**", list(st.secrets.keys()))
except Exception as e:
    client = None
    st.error(f"🚨 ERRO ao inicializar Groq: {e}")

def carregar_doutrina():
    """
    Simula um RAG (Retrieval-Augmented Generation).
    Lê a base de conhecimento técnica para dar robustez à análise.
    """
    caminho = "core/doutrina_trabalhista.txt"
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return "Erro ao carregar doutrina técnica."
    return "Base doutrinária não encontrada. Utilize critérios gerais da CLT."

def anonimizar(relato):
    """Máscara básica para proteção de dados (LGPD)."""
    relato = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[COLABORADOR]', relato)
    relato = re.sub(r'\b\d{3}\.\d{3}\.\d{3}-\\d{2}\b', '[CPF]', relato)
    relato = re.sub(r'(S\.A\.|Ltda|ME|EIRE|Empresa [A-Z])', '[EMPRESA]', relato)
    return relato

def analisar_relato(relato):
    """
    Analisa o relato usando RAG injetado para evitar tendenciosidade.
    """
    anon_relato = anonimizar(relato)
    doutrina_texto = carregar_doutrina()
    
    # Montamos o prompt que obriga a IA a consultar a doutrina antes de opinar
    prompt_analitico = f"""
    VOCÊ DEVE ANALISAR O RELATO ABAIXO À LUZ DA DOUTRINA FORNECIDA.
    
    ### DOUTRINA TÉCNICA (Sua régua de análise):
    {doutrina_texto}
    
    ### RELATO DO USUÁRIO:
    "{anon_relato}"
    
    ### INSTRUÇÃO:
    Seja cético. Diferencie o que é um 'desconforto do empregado' do que é 'violação da lei'. 
    Se a conduta do chefe estiver dentro do Poder Diretivo (como cobrar horário), declare Probabilidade 0%.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_analitico}
        ],
        temperature=0.0, # Temperatura ZERO para evitar respostas 'emocionadas'
    )
    return response.choices[0].message.content

def gerar_esqueleto(relato, analise):
    """Gera o documento técnico para o PDF."""
    data_atual = datetime.now().strftime("%d/%m/%Y")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Você é um assistente jurídico que estrutura fatos para advogados."},
            {"role": "user", "content": ESQUELETO_PROMPT.format(data=data_atual, relato=relato, analise=analise)}
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content