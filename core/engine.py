"""Engine Groq para AppGuard."""
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from core.prompts import SYSTEM_PROMPT, TRIAAGEM_PROMPT, ESQUELETO_PROMPT

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def anonimizar(relato):
    """Máscara básica: nomes, CPF, empresas."""
    relato = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[COLABORADOR]', relato)
    relato = re.sub(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', '[CPF]', relato)
    relato = re.sub(r'(S\.A\.|Ltda|ME|EIRE|Empresa [A-Z])', '[EMPRESA]', relato)
    return relato

def analisar_relato(relato):
    anon_relato = anonimizar(relato)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": TRIAAGEM_PROMPT.format(relato=anon_relato)}
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content

def gerar_esqueleto(relato, analise):
    data = datetime.now().strftime("%d/%m/%Y")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": ESQUELETO_PROMPT.format(data=data, relato=relato, analise=analise)}
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content