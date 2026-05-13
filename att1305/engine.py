"""
SafeGuard - Motor de IA Jurídica
Versão 2.0 - Engine robusta com tratamento de erros e múltiplos provedores
"""

import os
import re
import hashlib
import logging
from typing import Optional
from groq import Groq
from core.prompts import (
    SYSTEM_PROMPT_ANALISE,
    SYSTEM_PROMPT_ESQUELETO,
    SYSTEM_PROMPT_ANONIMIZACAO,
    PROMPT_ANALISE_TEMPLATE,
    PROMPT_ESQUELETO_TEMPLATE,
)

# Configuração de logging (não loga conteúdo sensível)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("safeguard.engine")

# Modelos disponíveis em ordem de preferência
MODELOS_PREFERIDOS = [
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "llama3-8b-8192",
]

def _get_client() -> Optional[Groq]:
    """Inicializa o cliente Groq de forma segura."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY não encontrada nas variáveis de ambiente.")
        return None
    return Groq(api_key=api_key)


def _chamar_llm(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 2048,
    temperatura: float = 0.4,
) -> str:
    """
    Função central para chamar o LLM com fallback entre modelos.
    Retorna a resposta como string ou uma mensagem de erro amigável.
    """
    client = _get_client()
    if not client:
        return (
            "⚠️ **Serviço temporariamente indisponível.**\n\n"
            "A chave de API não foi configurada. Por favor, defina a variável "
            "de ambiente `GROQ_API_KEY` e reinicie a aplicação."
        )

    for modelo in MODELOS_PREFERIDOS:
        try:
            logger.info(f"Tentando modelo: {modelo}")
            resposta = client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperatura,
            )
            conteudo = resposta.choices[0].message.content
            if conteudo:
                logger.info(f"Resposta obtida com sucesso via {modelo}")
                return conteudo.strip()
        except Exception as e:
            logger.warning(f"Falha no modelo {modelo}: {type(e).__name__} - {str(e)[:100]}")
            continue

    return (
        "⚠️ **Não foi possível processar sua solicitação no momento.**\n\n"
        "Todos os modelos disponíveis falharam. Por favor, verifique sua conexão "
        "e tente novamente em alguns instantes."
    )


def validar_relato(relato: str) -> tuple[bool, str]:
    """
    Valida se o relato tem conteúdo mínimo para análise.
    Retorna (valido, mensagem_erro).
    """
    relato = relato.strip()

    if len(relato) < 20:
        return False, "Por favor, descreva a situação com um pouco mais de detalhes para que eu possa ajudar melhor."

    if len(relato) > 10000:
        return False, "O relato está muito longo. Por favor, resuma os principais eventos (máx. 10.000 caracteres)."

    # Verifica se não é apenas caracteres repetidos ou spam
    palavras_unicas = set(relato.lower().split())
    if len(palavras_unicas) < 5:
        return False, "Por favor, descreva a situação com suas próprias palavras para que eu possa analisá-la."

    return True, ""


def analisar_relato(relato: str) -> str:
    """
    Analisa um relato de assédio e retorna orientação jurídica empática.
    """
    valido, erro = validar_relato(relato)
    if not valido:
        return f"💙 {erro}"

    prompt_usuario = PROMPT_ANALISE_TEMPLATE.format(relato=relato)

    return _chamar_llm(
        system_prompt=SYSTEM_PROMPT_ANALISE,
        user_prompt=prompt_usuario,
        max_tokens=2048,
        temperatura=0.3,  # Mais consistente para análise jurídica
    )


def gerar_esqueleto(relato: str, analise: str) -> str:
    """
    Gera um esqueleto estruturado de denúncia com base no relato e análise.
    """
    valido, erro = validar_relato(relato)
    if not valido:
        return f"⚠️ {erro}"

    prompt_usuario = PROMPT_ESQUELETO_TEMPLATE.format(
        relato=relato,
        analise=analise,
    )

    return _chamar_llm(
        system_prompt=SYSTEM_PROMPT_ESQUELETO,
        user_prompt=prompt_usuario,
        max_tokens=3000,
        temperatura=0.2,  # Mais determinístico para documentos técnicos
    )


def anonimizar(texto: str) -> str:
    """
    Remove informações pessoais identificáveis do texto.
    Aplica anonimização via LLM + regex como camada extra de segurança.
    """
    if not texto or len(texto.strip()) < 10:
        return texto

    # Primeira camada: regex para padrões óbvios
    texto_anon = _anonimizar_regex(texto)

    # Segunda camada: LLM para padrões mais sutis
    resultado = _chamar_llm(
        system_prompt=SYSTEM_PROMPT_ANONIMIZACAO,
        user_prompt=texto_anon,
        max_tokens=2000,
        temperatura=0.1,
    )

    return resultado


def _anonimizar_regex(texto: str) -> str:
    """Anonimização rápida via regex para padrões conhecidos."""
    # CPF: 000.000.000-00
    texto = re.sub(r'\d{3}[\.\s]?\d{3}[\.\s]?\d{3}[-\s]?\d{2}', '[CPF]', texto)
    # CNPJ: 00.000.000/0000-00
    texto = re.sub(r'\d{2}[\.\s]?\d{3}[\.\s]?\d{3}[\/\s]?\d{4}[-\s]?\d{2}', '[CNPJ]', texto)
    # Telefones brasileiros
    texto = re.sub(r'(\+55\s?)?(\(?\d{2}\)?\s?)(\d{4,5}[-\s]?\d{4})', '[TELEFONE]', texto)
    # E-mails
    texto = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', texto)
    # CEP
    texto = re.sub(r'\d{5}-?\d{3}', '[CEP]', texto)

    return texto


def gerar_hash_relato(relato: str) -> str:
    """
    Gera um hash único do relato para rastreamento sem armazenar o conteúdo.
    Útil para logs de auditoria sem expor dados sensíveis.
    """
    return hashlib.sha256(relato.encode()).hexdigest()[:12]
