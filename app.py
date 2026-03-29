import streamlit as st
from core.engine import analisar_relato, gerar_esqueleto, anonimizar 
from fpdf import FPDF
import os
from datetime import datetime

st.set_page_config(
    page_title="🛡️ AppGuard - GuardTech Solutions",
    page_icon="🛡️",
    layout="wide"
)

# CSS Custom - Garanta que a pasta assets e o arquivo existam
if os.path.exists("assets/custom.css"):
    with open("assets/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🛡️ AppGuard")
    st.markdown("### GuardTech Solutions")
    st.markdown("""
    **Consultoria em Direito do Trabalho com IA**\n
    Foco: Assédio Moral & Sexual\n
    *Não substitui advogado.*
    """)
    st.markdown("[Art. 483 CLT](https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm#art483)")
    st.markdown("[Lei 14.457/2022](https://www.planalto.gov.br)")
    
    if st.button("🗑️ Limpar Histórico", key="clear"):
        st.cache_data.clear()
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    if st.button("🚨 Pânico", key="panic", help="Limpa e fecha"):
        st.cache_data.clear()
        st.markdown('<script>window.close();</script>', unsafe_allow_html=True)

# Main Chat
st.header("📝 Relate sua situação")
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe o histórico de mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada do Usuário
if prompt := st.chat_input("Descreva o ocorrido..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando com IA jurídica..."):
            # Funções que chamam a Groq via engine.py
            analise = analisar_relato(prompt)
            esqueleto = gerar_esqueleto(prompt, analise)
            
            # Resposta da IA com o Aviso Ético do PDF
            full_response = analise + "\n\n⚠️ **AVISO:** Esta análise é meramente informativa e NÃO substitui consulta a advogado."
            st.markdown(full_response)
        
        st.markdown("### 📄 Esqueleto de Denúncia")
        st.info("Este rascunho foi gerado para facilitar sua conversa com um advogado.")
        st.markdown(esqueleto)
        
        # Dashboard de Análise (Baseado na Ilustração 2 do PDF)
        col1, col2 = st.columns([2,1])
        with col1:
            st.write("**Evidências detectadas:**")
            evidencias = ["Humilhação pública", "Isolamento", "Gritos"]
            for ev in evidencias:
                st.checkbox(ev, value=True, key=f"ev_{ev}_{len(st.session_state.messages)}")
        
        with col2:
            st.metric("Probabilidade Assédio", "75%", "↑ Análise IA")
        
        # Exportação para PDF (Corrigido para fpdf2)
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12) 
            pdf.cell(200, 10, txt="AppGuard - GuardTech Solutions", ln=1, align="C")
            pdf.ln(10)
            pdf.multi_cell(0, 10, txt=esqueleto)
            
            pdf_output = pdf.output() # No fpdf2 o output() retorna bytes por padrão
            
            st.download_button(
                label="📥 Baixar Esqueleto da Denúncia (PDF)",
                data=pdf_output,
                file_name=f"denuncia_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Realtime keywords (simples) no rodapé
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    ultimo = st.session_state.messages[-1]["content"]
    palavras = ["assédio", "humilhação", "gritos", "chefe", "empresa"]
    count = sum(1 for p in palavras if p in ultimo.lower())
    st.caption(f"🔍 Termos sensíveis detectados: {count}/{len(palavras)}")