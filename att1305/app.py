"""
SafeGuard - Plataforma de Apoio Jurídico com IA
Versão 2.0 | GuardTech Solutions

Melhorias v2.0:
- Interface redesenhada com visual profissional e acolhedor
- Melhor estrutura de código com separação de responsabilidades
- PDF melhorado com formatação profissional e suporte a UTF-8
- Anonimização automática antes de processar
- Validação de entrada do usuário
- Histórico de sessão com exportação completa
- Métricas de sensibilidade mais inteligentes
- Tratamento de erros robusto
"""

import streamlit as st
import os
from datetime import datetime
from io import BytesIO

# ── Configuração da Página (deve ser o primeiro comando Streamlit) ──
st.set_page_config(
    page_title="SafeGuard | Apoio Jurídico Trabalhista",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "mailto:suporte@guardtech.com.br",
        "About": "SafeGuard v2.0 - Apoio jurídico com IA para trabalhadores."
    }
)

# ── Importações do core (após set_page_config) ──
from core.engine import analisar_relato, gerar_esqueleto, anonimizar, validar_relato

# ── Carrega CSS ──
def carregar_css():
    css_path = "assets/custom.css"
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

carregar_css()


# ════════════════════════════════════════
#  FUNÇÕES UTILITÁRIAS
# ════════════════════════════════════════

def inicializar_sessao():
    """Inicializa variáveis de estado da sessão."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "analises_realizadas" not in st.session_state:
        st.session_state.analises_realizadas = 0
    if "anonimizar_ativo" not in st.session_state:
        st.session_state.anonimizar_ativo = True


def limpar_historico():
    """Limpa histórico de conversa e reinicia contadores."""
    st.session_state.messages = []
    st.session_state.analises_realizadas = 0
    st.cache_data.clear()


def detectar_termos_sensiveis(texto: str) -> dict:
    """
    Analisa o texto para detectar termos sensíveis por categoria.
    Retorna dicionário com categorias encontradas.
    """
    categorias = {
        "assédio_moral": ["humilhação", "xingamento", "gritos", "ameaça", "constrangimento",
                          "pressão", "intimidação", "isolamento", "ridicularizar", "ofensa"],
        "assédio_sexual": ["assédio sexual", "toque", "insinuação", "proposta", "câmera",
                           "foto", "importunação", "abuso", "chantagem sexual"],
        "discriminação": ["discriminação", "racismo", "preconceito", "gordofobia",
                          "homofobia", "transfobia", "sexismo", "etarismo"],
        "saúde_mental": ["ansiedade", "depressão", "síndrome", "burnout", "afastamento",
                         "médico", "psicólogo", "licença", "transtorno"],
    }

    encontrados = {}
    texto_lower = texto.lower()
    for categoria, termos in categorias.items():
        achados = [t for t in termos if t in texto_lower]
        if achados:
            encontrados[categoria] = achados

    return encontrados


def gerar_pdf_profissional(esqueleto: str, relato_original: str = "") -> bytes:
    """
    Gera um PDF profissional com suporte completo a UTF-8 e formatação adequada.
    Usa reportlab se disponível, senão fpdf2 com fallback.
    """
    try:
        # Tenta usar reportlab (melhor suporte a Unicode)
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2.5*cm,
            leftMargin=2.5*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm,
        )

        styles = getSampleStyleSheet()
        cor_primaria = HexColor('#0f2744')
        cor_secundaria = HexColor('#2563eb')
        cor_aviso = HexColor('#d97706')

        estilo_titulo = ParagraphStyle(
            'Titulo', parent=styles['Title'],
            fontSize=18, textColor=cor_primaria,
            spaceAfter=6, alignment=TA_CENTER,
        )
        estilo_subtitulo = ParagraphStyle(
            'Subtitulo', parent=styles['Normal'],
            fontSize=10, textColor=cor_secundaria,
            spaceAfter=4, alignment=TA_CENTER,
        )
        estilo_cabecalho = ParagraphStyle(
            'Cabecalho', parent=styles['Heading2'],
            fontSize=12, textColor=cor_primaria,
            spaceBefore=12, spaceAfter=4,
        )
        estilo_corpo = ParagraphStyle(
            'Corpo', parent=styles['Normal'],
            fontSize=10, leading=15,
            spaceAfter=6, alignment=TA_JUSTIFY,
        )
        estilo_aviso = ParagraphStyle(
            'Aviso', parent=styles['Normal'],
            fontSize=9, textColor=cor_aviso,
            borderPad=6, backColor=HexColor('#fef3c7'),
            spaceAfter=6,
        )

        elementos = []
        timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M")

        # Cabeçalho
        elementos.append(Paragraph("🛡️ SafeGuard", estilo_titulo))
        elementos.append(Paragraph("Plataforma de Apoio Jurídico Trabalhista", estilo_subtitulo))
        elementos.append(Paragraph(f"Documento gerado em {timestamp}", estilo_subtitulo))
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(HRFlowable(width="100%", thickness=2, color=cor_primaria))
        elementos.append(Spacer(1, 0.5*cm))

        # Aviso de confidencialidade
        elementos.append(Paragraph(
            "🔒 DOCUMENTO CONFIDENCIAL — Para uso exclusivo da vítima e seu advogado(a)",
            estilo_aviso
        ))
        elementos.append(Spacer(1, 0.3*cm))

        # Conteúdo principal
        for linha in esqueleto.split('\n'):
            linha = linha.strip()
            if not linha:
                elementos.append(Spacer(1, 0.15*cm))
                continue

            # Remove marcadores markdown
            if linha.startswith('**') and linha.endswith('**'):
                linha_limpa = linha.replace('**', '')
                elementos.append(Paragraph(linha_limpa, estilo_cabecalho))
            elif linha.startswith('#'):
                linha_limpa = linha.lstrip('#').strip()
                elementos.append(Paragraph(linha_limpa, estilo_cabecalho))
            elif linha.startswith('- ') or linha.startswith('• '):
                linha_limpa = '• ' + linha[2:]
                elementos.append(Paragraph(linha_limpa, estilo_corpo))
            else:
                # Converte bold inline
                linha_limpa = linha.replace('**', '<b>', 1).replace('**', '</b>', 1)
                elementos.append(Paragraph(linha_limpa, estilo_corpo))

        # Rodapé
        elementos.append(Spacer(1, 0.5*cm))
        elementos.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e2e8f0')))
        elementos.append(Spacer(1, 0.2*cm))
        elementos.append(Paragraph(
            "⚠️ AVISO LEGAL: Este documento foi gerado por inteligência artificial com fins informativos. "
            "Não constitui consultoria jurídica e não substitui a orientação de um advogado(a) trabalhista habilitado(a). "
            "SafeGuard v2.0 | GuardTech Solutions",
            estilo_aviso
        ))

        doc.build(elementos)
        return buffer.getvalue()

    except ImportError:
        # Fallback para fpdf2
        return _gerar_pdf_fpdf(esqueleto)


def _gerar_pdf_fpdf(esqueleto: str) -> bytes:
    """Fallback: gera PDF usando fpdf2."""
    from fpdf import FPDF

    class PDFSafeGuard(FPDF):
        def header(self):
            self.set_font('Helvetica', 'B', 14)
            self.set_text_color(15, 39, 68)
            self.cell(0, 10, 'SafeGuard - Documento de Apoio Juridico', align='C', ln=1)
            self.set_font('Helvetica', '', 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 6, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', align='C', ln=1)
            self.ln(3)
            self.set_draw_color(37, 99, 235)
            self.set_line_width(0.5)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)

        def footer(self):
            self.set_y(-20)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 5, 'AVISO: Documento informativo. Nao substitui consultoria juridica profissional.', align='C', ln=1)
            self.cell(0, 5, f'Pagina {self.page_no()}', align='C')

    pdf = PDFSafeGuard()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(30, 41, 59)

    # Sanitiza para Latin-1
    texto_sanitizado = esqueleto.encode('latin-1', 'replace').decode('latin-1')

    for linha in texto_sanitizado.split('\n'):
        if linha.startswith('**') or linha.startswith('#'):
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(15, 39, 68)
            linha_limpa = linha.replace('**', '').replace('#', '').strip()
            pdf.cell(0, 8, linha_limpa, ln=1)
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(30, 41, 59)
        elif linha.strip():
            pdf.multi_cell(0, 6, linha.strip())
        else:
            pdf.ln(3)

    return bytes(pdf.output())


# ════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════

def renderizar_sidebar():
    with st.sidebar:
        st.title("🛡️ SafeGuard")
        st.markdown("### GuardTech Solutions")

        st.markdown("""
        **Apoio Jurídico com IA**
        para trabalhadores em situação
        de assédio moral ou sexual.

        *Protegemos sua história.*
        """)

        st.markdown("---")

        # Toggle de anonimização
        st.session_state.anonimizar_ativo = st.toggle(
            "🔒 Anonimizar antes de enviar",
            value=st.session_state.get("anonimizar_ativo", True),
            help="Remove nomes, CPFs e dados pessoais antes de enviar para análise"
        )

        if st.session_state.anonimizar_ativo:
            st.caption("✅ Seus dados pessoais serão removidos antes da análise")

        st.markdown("---")

        # Links legais
        st.markdown("**📚 Legislação**")
        st.markdown("• [Art. 483 CLT](https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm#art483)")
        st.markdown("• [Lei 14.457/2022](https://www.planalto.gov.br/ccivil_03/leis/l14457.htm)")
        st.markdown("• [Art. 216-A CP (Assédio Sexual)](https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848.htm)")

        st.markdown("---")

        # Canais de apoio
        st.markdown("**🆘 Canais de Apoio**")
        st.markdown("• **MPT:** 0800 723 0099")
        st.markdown("• **CVV:** 188 (24h)")
        st.markdown("• [Disque 100](https://www.gov.br/mdh/pt-br/disque100)")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpar", use_container_width=True, help="Limpa o histórico"):
                limpar_historico()
                st.rerun()
        with col2:
            if st.button("🚨 Pânico", use_container_width=True, help="Fecha e limpa tudo"):
                limpar_historico()
                st.markdown('<script>window.close();</script>', unsafe_allow_html=True)
                st.success("Histórico apagado.")

        st.markdown("---")
        st.caption(f"SafeGuard v2.0 | {datetime.now().strftime('%d/%m/%Y')}")
        st.caption("Análises realizadas nesta sessão: "
                   f"**{st.session_state.get('analises_realizadas', 0)}**")


# ════════════════════════════════════════
#  ÁREA PRINCIPAL
# ════════════════════════════════════════

def renderizar_cabecalho():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <h1 style='margin-bottom: 0;'>🛡️ SafeGuard</h1>
        <p style='color: #64748b; font-size: 1rem; margin-top: 0.2rem;'>
        Apoio jurídico inteligente para trabalhadores em situação de assédio
        </p>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='text-align: right; padding-top: 0.5rem;'>
        <span style='background: #d1fae5; color: #065f46; padding: 4px 12px;
        border-radius: 20px; font-size: 0.78rem; font-weight: 600;
        border: 1px solid #6ee7b7;'>
        🔒 Ambiente Seguro
        </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")


def renderizar_mensagem_boas_vindas():
    if not st.session_state.messages:
        st.markdown("""
        <div style='background: white; border-radius: 12px; padding: 1.5rem;
        border-left: 4px solid #2563eb; box-shadow: 0 2px 12px rgba(15,39,68,0.08);
        margin-bottom: 1.5rem;'>
        <h4 style='color: #0f2744; margin: 0 0 0.5rem 0;'>💙 Olá, você não está sozinho(a)</h4>
        <p style='color: #475569; margin: 0; line-height: 1.6;'>
        Este é um espaço seguro e confidencial. Você pode descrever livremente o que está
        vivendo no trabalho. Analisarei sua situação com base na legislação trabalhista
        brasileira e orientarei sobre seus direitos e próximos passos.
        </p>
        <p style='color: #64748b; font-size: 0.85rem; margin: 0.75rem 0 0 0;'>
        ℹ️ Seus relatos são processados com segurança e não são armazenados em nossos servidores.
        </p>
        </div>
        """, unsafe_allow_html=True)


def exibir_analise_completa(prompt: str):
    """Processa o relato e exibe análise + esqueleto + PDF."""

    with st.chat_message("assistant"):
        # 1. Anonimização (se ativa)
        relato_para_analise = prompt
        if st.session_state.get("anonimizar_ativo", True):
            with st.spinner("🔒 Anonimizando dados pessoais..."):
                relato_para_analise = anonimizar(prompt)

        # 2. Análise principal
        with st.spinner("⚖️ Analisando com IA jurídica..."):
            analise = analisar_relato(relato_para_analise)

        # Exibe análise
        st.markdown(analise)
        st.markdown(
            "⚠️ **AVISO LEGAL:** Esta análise é meramente informativa e **não substitui** "
            "consulta com advogado(a) trabalhista habilitado(a).",
        )

        st.markdown("---")

        # 3. Esqueleto de denúncia
        st.markdown("### 📋 Esqueleto de Denúncia")
        st.info(
            "Este rascunho estruturado foi gerado para facilitar sua conversa com um(a) advogado(a). "
            "Revise e complete os campos indicados como [A PREENCHER]."
        )

        with st.spinner("📝 Gerando estrutura de denúncia..."):
            esqueleto = gerar_esqueleto(relato_para_analise, analise)

        with st.expander("📄 Ver esqueleto completo", expanded=True):
            st.markdown(esqueleto)

        # 4. Exportação PDF
        st.markdown("#### 📥 Exportar Documento")
        col_pdf, col_txt = st.columns(2)

        with col_pdf:
            try:
                pdf_bytes = gerar_pdf_profissional(esqueleto)
                nome_arquivo = f"safeguard_denuncia_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                st.download_button(
                    label="📥 Baixar PDF Profissional",
                    data=pdf_bytes,
                    file_name=nome_arquivo,
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")

        with col_txt:
            texto_completo = f"SAFEGUARD - ANÁLISE JURÍDICA\n{'='*50}\n\n{analise}\n\n{'='*50}\nESQUELETO DE DENÚNCIA\n{'='*50}\n\n{esqueleto}"
            st.download_button(
                label="📄 Baixar como Texto",
                data=texto_completo.encode("utf-8"),
                file_name=f"safeguard_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

        st.session_state.analises_realizadas += 1
        return analise + "\n\n" + esqueleto


def exibir_metricas_sensibilidade(texto: str):
    """Exibe métricas de termos sensíveis detectados."""
    categorias = detectar_termos_sensiveis(texto)

    if not categorias:
        return

    labels = {
        "assédio_moral": "Assédio Moral",
        "assédio_sexual": "Assédio Sexual",
        "discriminação": "Discriminação",
        "saúde_mental": "Saúde Mental",
    }
    ícones = {
        "assédio_moral": "⚠️",
        "assédio_sexual": "🚨",
        "discriminação": "🏳️",
        "saúde_mental": "💙",
    }

    partes = [f"{ícones[c]} **{labels[c]}**" for c in categorias]
    st.caption(f"🔍 Categorias identificadas: {' · '.join(partes)}")


# ════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════

def main():
    inicializar_sessao()
    renderizar_sidebar()
    renderizar_cabecalho()
    renderizar_mensagem_boas_vindas()

    # Exibe histórico de mensagens
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input do usuário
    placeholder = "Descreva o que está acontecendo no seu trabalho... (pode escrever com suas próprias palavras)"
    if prompt := st.chat_input(placeholder):

        # Valida entrada
        valido, erro = validar_relato(prompt)
        if not valido:
            st.warning(f"💙 {erro}")
            st.stop()

        # Exibe mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Processa e exibe resposta
        resposta_completa = exibir_analise_completa(prompt)
        st.session_state.messages.append({"role": "assistant", "content": resposta_completa})

        # Métricas de sensibilidade
        exibir_metricas_sensibilidade(prompt)


if __name__ == "__main__":
    main()
