import io
from datetime import datetime

def gerar_pdf_profissional(esqueleto: str) -> bytes:
    """Gera um PDF com suporte a UTF-8 usando reportlab, com fallback para fpdf2."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2.5*cm, bottomMargin=2.5*cm,
        )

        styles = getSampleStyleSheet()
        cor_primaria = HexColor('#0f2744')
        cor_secundaria = HexColor('#2563eb')
        cor_aviso = HexColor('#d97706')

        estilo_titulo = ParagraphStyle('Titulo', parent=styles['Title'], fontSize=18, textColor=cor_primaria, spaceAfter=6, alignment=TA_CENTER)
        estilo_subtitulo = ParagraphStyle('Subtitulo', parent=styles['Normal'], fontSize=10, textColor=cor_secundaria, spaceAfter=4, alignment=TA_CENTER)
        estilo_cabecalho = ParagraphStyle('Cabecalho', parent=styles['Heading2'], fontSize=12, textColor=cor_primaria, spaceBefore=12, spaceAfter=4)
        estilo_corpo = ParagraphStyle('Corpo', parent=styles['Normal'], fontSize=10, leading=15, spaceAfter=6, alignment=TA_JUSTIFY)
        estilo_aviso = ParagraphStyle('Aviso', parent=styles['Normal'], fontSize=9, textColor=cor_aviso, borderPad=6, backColor=HexColor('#fef3c7'), spaceAfter=6)

        elementos = []
        timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M")

        elementos.append(Paragraph("🛡️ SafeGuard", estilo_titulo))
        elementos.append(Paragraph("Plataforma de Apoio Jurídico Trabalhista", estilo_subtitulo))
        elementos.append(Paragraph(f"Documento gerado em {timestamp}", estilo_subtitulo))
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(HRFlowable(width="100%", thickness=2, color=cor_primaria))
        elementos.append(Spacer(1, 0.5*cm))

        elementos.append(Paragraph("🔒 DOCUMENTO CONFIDENCIAL — Para uso exclusivo da vítima e seu advogado(a)", estilo_aviso))
        elementos.append(Spacer(1, 0.3*cm))

        for linha in esqueleto.split('\n'):
            linha = linha.strip()
            if not linha:
                elementos.append(Spacer(1, 0.15*cm))
                continue
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
                linha_limpa = linha.replace('**', '<b>', 1).replace('**', '</b>', 1)
                elementos.append(Paragraph(linha_limpa, estilo_corpo))

        elementos.append(Spacer(1, 0.5*cm))
        elementos.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e2e8f0')))
        elementos.append(Spacer(1, 0.2*cm))
        elementos.append(Paragraph(
            "⚠️ AVISO LEGAL: Este documento foi gerado por inteligência artificial com fins informativos. "
            "Não constitui consultoria jurídica e não substitui a orientação de um advogado(a) trabalhista.",
            estilo_aviso
        ))

        doc.build(elementos)
        return buffer.getvalue()

    except ImportError:
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

    pdf_output = pdf.output()
    return bytes(pdf_output) if isinstance(pdf_output, (bytearray, bytes)) else pdf_output
