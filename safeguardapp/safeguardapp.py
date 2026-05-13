import reflex as rx
from core.engine import analisar_relato, gerar_esqueleto, validar_relato
from core.pdf_generator import gerar_pdf_profissional
import os
import datetime

def detectar_termos_sensiveis(texto: str) -> list[str]:
    categorias = {
        "Assédio Moral": ["humilhação", "xingamento", "gritos", "ameaça", "constrangimento", "pressão", "intimidação", "isolamento", "ridicularizar", "ofensa"],
        "Assédio Sexual": ["assédio sexual", "toque", "insinuação", "proposta", "câmera", "foto", "importunação", "abuso", "chantagem sexual"],
        "Discriminação": ["discriminação", "racismo", "preconceito", "gordofobia", "homofobia", "transfobia", "sexismo", "etarismo"],
        "Saúde Mental": ["ansiedade", "depressão", "síndrome", "burnout", "afastamento", "médico", "psicólogo", "licença", "transtorno"],
    }
    encontrados = []
    texto_lower = texto.lower()
    for cat, termos in categorias.items():
        if any(t in texto_lower for t in termos):
            encontrados.append(cat)
    return encontrados

class State(rx.State):
    """O estado da aplicação."""
    has_started: bool = False
    messages: list[dict[str, str]] = []
    current_message: str = ""
    processing: bool = False
    esqueleto: str = ""  # Armazena o resumo/esqueleto da denúncia
    termos_sensiveis: list[str] = []

    def panic_button(self):
        self.reset_session()
        return rx.redirect("https://www.google.com")

    async def download_pdf(self):
        if not self.esqueleto: return
        pdf_bytes = gerar_pdf_profissional(self.esqueleto)
        filename = f"safeguard_denuncia_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        return rx.download(data=pdf_bytes, filename=filename)

    async def download_txt(self):
        if not self.esqueleto: return
        texto = f"SAFEGUARD - ESQUELETO DE DENÚNCIA\n{'='*50}\n\n{self.esqueleto}"
        filename = f"safeguard_denuncia_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        return rx.download(data=texto.encode('utf-8'), filename=filename)

    def start_chat(self):
        """Muda para a tela de chat."""
        self.has_started = True

    def reset_session(self):
        """Limpa o histórico e volta para o início."""
        self.messages = []
        self.has_started = False
        self.current_message = ""
        self.esqueleto = ""
        self.termos_sensiveis = []

    def handle_key(self, key: str):
        """Trata o pressionamento de teclas no input."""
        if key == "Enter":
            return State.answer

    async def answer(self):
        """Envia a mensagem para a IA e processa a resposta."""
        if not self.current_message:
            return

        # Adiciona mensagem do usuário
        user_msg = self.current_message
        self.messages.append({"role": "user", "content": user_msg})
        self.current_message = ""
        self.processing = True
        yield
        
        # Validation
        valido, erro = validar_relato(user_msg)
        if not valido:
            self.messages.append({"role": "assistant", "content": f"💙 {erro}"})
            self.processing = False
            return
            
        # Detectar termos sensíveis
        novos_termos = detectar_termos_sensiveis(user_msg)
        for t in novos_termos:
            if t not in self.termos_sensiveis:
                self.termos_sensiveis.append(t)


        # Chama a IA de análise
        try:
            answer = analisar_relato(user_msg)
            self.messages.append({"role": "assistant", "content": answer})
            
            # Tenta gerar o esqueleto (resumo) se for um relato
            if "probabilidade" in answer.lower() or "análise" in answer.lower():
                self.esqueleto = gerar_esqueleto(user_msg, answer)
        except Exception as e:
            self.messages.append({"role": "assistant", "content": f"Erro técnico: {str(e)}"})
        
        self.processing = False

def info_card(title: str, text: str, icon: str):
    """Cria um pequeno card informativo para o onboarding."""
    return rx.vstack(
        rx.icon(icon, size=24, color="violet"),
        rx.text(title, font_weight="bold", color="white", size="3"),
        rx.text(text, color="#d1d5db", size="2"),
        padding="20px",
        bg="rgba(15, 23, 42, 0.6)",
        backdrop_filter="blur(8px)",
        border_radius="16px",
        border="1px solid rgba(255, 255, 255, 0.1)",
        align="center",
        flex="1",
        width="100%",
    )

def onboarding_screen():
    """Tela de introdução / Explicação (Modern UI 2026)."""
    return rx.center(
        rx.vstack(
            rx.heading("🛡️ SafeGuard", size="9", color="white", margin_bottom="10px"),
            rx.text("Plataforma destinada a diminuir dúvidas e orientar quanto a casos de assédio.", color="#d1d5db", size="4"),
            rx.divider(margin_y="20px", border_color="rgba(255, 255, 255, 0.1)"),
            rx.hstack(
                info_card("Privacidade", "Sem login, sem rastros.", "shield"),
                info_card("Especialista", "Foco em Leis do Trabalho.", "scale"),
                info_card("Anônimo", "Sessão deletada ao sair.", "user-round-x"),
                spacing="4",
                width="100%",
            ),
            rx.button(
                "Iniciar Sessão Segura",
                on_click=State.start_chat,
                size="4",
                variant="solid",
                color_scheme="indigo",
                cursor="pointer",
                margin_top="30px",
                padding="24px 40px",
                border_radius="12px",
                transition="all 0.3s ease",
                _hover={"transform": "scale(1.05)", "box_shadow": "0 0 30px rgba(99, 102, 241, 0.5)"},
            ),
            bg="rgba(15, 23, 42, 0.7)",
            backdrop_filter="blur(20px)",
            padding="60px",
            border_radius="32px",
            border="1px solid rgba(255, 255, 255, 0.1)",
            max_width="850px",
            align="center",
        ),
        height="100vh",
        width="100%",
        background_image="url('/bg.png')",
        background_size="cover",
        background_position="center",
    )

def chat_bubble(msg: dict):
    """Bolha de chat estilizada."""
    is_user = msg["role"] == "user"
    return rx.hstack(
        rx.box(
            rx.markdown(msg["content"]),
            bg=rx.cond(is_user, "indigo.600", "rgba(30, 41, 59, 0.85)"),
            color="white",
            padding="16px",
            border_radius="20px",
            max_width="85%",
            box_shadow="0 4px 12px rgba(0,0,0,0.2)",
        ),
        width="100%",
        justify=rx.cond(is_user, "end", "start"),
        margin_y="10px",
    )

def chat_ui():
    """Interface principal de chat."""
    return rx.hstack(
        # Coluna do Chat (Esquerda/Centro)
        rx.vstack(
            # Header do Chat
            rx.hstack(
                rx.heading("🛡️ SafeGuard Chat", size="6", color="white"),
                rx.spacer(),
                rx.button(
                    rx.icon("trash-2", size=20),
                    "Limpar Tudo",
                    on_click=State.reset_session,
                    color_scheme="red",
                    variant="soft",
                    cursor="pointer",
                ),
                rx.button(
                    "🚨 Pânico",
                    on_click=State.panic_button,
                    color_scheme="red",
                    variant="solid",
                    cursor="pointer",
                    margin_left="10px",
                ),
                width="100%",
                padding="20px",
                bg="rgba(15, 23, 42, 0.8)",
                border_bottom="1px solid rgba(255, 255, 255, 0.1)",
            ),
            
            # Área de Mensagens
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(State.messages, chat_bubble),
                    width="100%",
                    padding="20px",
                ),
                height="calc(100vh - 160px)",
                width="100%",
                bg="rgba(15, 23, 42, 0.4)",
            ),
            
            # Input de Mensagem
            rx.hstack(
            rx.text_area(
                placeholder="Descreva sua dúvida ou relato detalhadamente...",
                value=State.current_message,
                on_change=State.set_current_message,
                flex="1",
                bg="rgba(30, 41, 59, 0.5)",
                border="1px solid rgba(255, 255, 255, 0.1)",
                border_radius="12px",
                color="white",
                padding="16px",
                min_height="80px",
                resize="none",
            ),
                rx.button(
                    rx.cond(State.processing, rx.spinner(size="2"), rx.icon("send")),
                    on_click=State.answer,
                    color_scheme="indigo",
                    disabled=State.processing,
                    cursor="pointer",
                ),
                width="100%",
                padding="20px",
                bg="rgba(15, 23, 42, 0.9)",
                border_top="1px solid rgba(255, 255, 255, 0.1)",
            ),
            # Footer: Sensitive Terms
            rx.cond(
                State.termos_sensiveis.length() > 0,
                rx.hstack(
                    rx.icon("alert-triangle", size=14, color="orange"),
                    rx.text("Categorias detectadas:", color="#9ca3af", size="1"),
                    rx.foreach(
                        State.termos_sensiveis,
                        lambda termo: rx.badge(termo, color_scheme="orange", size="1")
                    ),
                    padding="10px",
                    bg="rgba(15, 23, 42, 0.9)",
                    width="100%",
                ),
            ),
            flex="2",
            height="100vh",
        ),
        
        # Coluna do Esqueleto/Resumo (Direita) - Só aparece se houver esqueleto
        rx.cond(
            State.esqueleto != "",
            rx.vstack(
                rx.heading("📄 Resumo para Advogado", size="5", color="white", margin_bottom="10px"),
                rx.scroll_area(
                    rx.box(
                        rx.markdown(State.esqueleto),
                        color="#d1d5db",
                        font_size="0.9rem",
                    ),
                    height="calc(100vh - 120px)",
                ),
                rx.hstack(
                    rx.button("📥 PDF", on_click=State.download_pdf, color_scheme="indigo", size="2", cursor="pointer", width="50%"),
                    rx.button("📄 TXT", on_click=State.download_txt, color_scheme="gray", size="2", cursor="pointer", width="50%"),
                    width="100%",
                    padding_top="10px"
                ),
                bg="rgba(30, 41, 59, 0.7)",
                backdrop_filter="blur(10px)",
                padding="20px",
                width="350px",
                height="100vh",
                border_left="1px solid rgba(255, 255, 255, 0.1)",
            )
        ),
        width="100%",
        bg="#0f172a",
        background_image="url('/bg.png')",
        background_size="cover",
        spacing="0",
    )

def index() -> rx.Component:
    """Página principal com condicional de Onboarding."""
    return rx.fragment(
        rx.cond(
            State.has_started,
            chat_ui(),
            onboarding_screen()
        )
    )

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="indigo",
    )
)
app.add_page(index, title="SafeGuard - Proteção ao Trabalhador")
