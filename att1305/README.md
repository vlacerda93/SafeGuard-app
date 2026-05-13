# 🛡️ SafeGuard v2.0
### Plataforma de Apoio Jurídico Trabalhista com IA

> Protegemos sua história. Você não está sozinho(a).

SafeGuard é uma ferramenta de suporte jurídico com inteligência artificial voltada para trabalhadores em situação de assédio moral ou sexual no ambiente de trabalho. A plataforma oferece análise empática, orientação jurídica baseada na legislação brasileira e geração de documentos estruturados de denúncia.

⚠️ **Protótipo acadêmico.** Esta ferramenta é um co-piloto informacional e **não substitui** consulta com advogado(a) habilitado(a).

---

## ✨ Novidades v2.0

- 🎨 Interface redesenhada — visual profissional, acolhedor e acessível
- 🤖 Prompts mais empáticos, detalhados e juridicamente precisos
- 📄 PDF profissional com suporte completo a caracteres especiais (reportlab)
- 🔒 Anonimização automática de dados pessoais antes do envio à IA
- ✅ Validação de entrada do usuário
- 📊 Detecção de categorias de violação (moral, sexual, discriminação, saúde mental)
- 💾 Exportação em PDF e TXT
- ⚙️ Código modular, documentado e com tratamento de erros robusto
- 🔄 Fallback automático entre modelos de IA

---

## 🏗️ Estrutura do Projeto

```
SafeGuard-app/
├── app.py                  # Interface principal (Streamlit)
├── requirements.txt        # Dependências
├── rxconfig.py             # Config Reflex (se usado)
├── assets/
│   └── custom.css          # Estilos personalizados v2.0
├── core/
│   ├── __init__.py
│   ├── engine.py           # Motor de IA + funções utilitárias
│   └── prompts.py          # Sistema de prompts jurídicos
└── README.md
```

---

## 🚀 Como Rodar

### 1. Clone o repositório
```bash
git clone https://github.com/vlacerda93/SafeGuard-app.git
cd SafeGuard-app
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure a chave de API
```bash
# Linux/Mac
export GROQ_API_KEY="sua_chave_aqui"

# Windows (PowerShell)
$env:GROQ_API_KEY="sua_chave_aqui"
```

> Obtenha sua chave gratuita em: https://console.groq.com

### 4. Execute
```bash
streamlit run app.py
```

---

## ⚖️ Base Legal

- CLT — Arts. 482, 483, 186, 927, 932
- Lei 9.029/1995 (práticas discriminatórias)
- Lei 14.457/2022 (Programa Emprega + Mulher / Combate ao Assédio)
- Código Penal — Arts. 146, 147, 213, 216-A
- NR-01 atualizada (gestão de riscos psicossociais)

---

## 🆘 Canais de Apoio

- **MPT (Ministério Público do Trabalho):** 0800 723 0099
- **CVV (Centro de Valorização da Vida):** 188 (24h)
- **Disque 100:** Direitos Humanos

---

## 👥 Equipe

Desenvolvido por **GuardTech Solutions** como protótipo acadêmico.

---

*SafeGuard v2.0 — Porque ninguém deveria sofrer em silêncio.*
