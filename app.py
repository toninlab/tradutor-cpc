# app.py

import streamlit as st
import logic_processor as lp
from streamlit_option_menu import option_menu

# configuração da página
st.set_page_config(
  page_title="Agente de IA Lógico",
  page_icon="🤖",
  layout="centered"
)

# função de injetar CSS
def load_css():
  st.markdown("""
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap" rel="stylesheet">

  <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    [data-testid="stHeading"] a {
      display: none !important;
    }
    
    body {
      font-family: "Inter", sans-serif;
      font-size: 17px;
    }

    .stButton > button {
      font-family: "Inter", sans-serif; 
      border: none;
      background-color: #007bff;
      color: white;
      padding: 0.75em 1.5em;
      border-radius: 50px;
      font-weight: 600;
      width: 100%;
      transition: all 0.3s ease;
    }
    .stButton > button:hover {
      background-color: #0056b3;
      color: white;
    }
    
    .stTextArea textarea, .stTextInput input {
      font-family: "Inter", sans-serif; 
      background-color: #1a1c24;
      border-radius: 10px;
      border: 1px solid #3133f;
      color: #FAFAFA;
      font-size: 1.1rem;
    }
    .stTextArea textarea { 
        min-height: 80px; 
        height: 80px;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] {
      background-color: #1a1c24;
      border-radius: 10px;
      border-color: #31333f;
      padding: 1em;
    }
    
    h3 { 
      font-size: 1.5rem;
      margin-bottom: 0.8em;
    }
              
    .syntax-item {
        margin-bottom: 1em;
    }
      
    .syntax-item .stMarkdown p {
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 0.5em;
    }

    .symbol-pair-container {
        margin-left: -5px; 
        margin-right: -5px;
    }

    [data-testid="stCodeBlock"] {
        /* AJUSTE DE CSS: Largura automática e padding reduzido */
        padding: 0.4em 0.6em !important; 
        width: fit-content; 
        min-width: 40px; 
        text-align: center;
        
        margin: 0 5px; 
        font-family: "monospace", "Inter", sans-serif; 
        font-size: 1.1rem; 
    }

    hr {
        margin-top: 0em !important; 
        margin-bottom: 0em !important; 
    }
    
  </style>
  """, unsafe_allow_html=True)


# execução do CSS e título
load_css()
st.title("Tradutor - Agente de IA", anchor=False)
st.caption("Projeto acadêmico de IA - Uni-FACEF")


# checagem da chave API
try:
  api_key = st.secrets["GOOGLE_API_KEY"]
except (KeyError, FileNotFoundError):
  st.error("Chave de API do Google Gemini não encontrada! Por favor, adicione-a ao arquivo `.streamlit/secrets.toml`.")
  api_key = None 


# seletor dos modos
selected_mode = option_menu(
  menu_title=None, 
  options=["Português ⭢ Lógica", "Lógica ⭢ Português"],
  icons=["translate", "code-slash"], 
  orientation="horizontal",
  styles={
    "container": {"padding": "0!important", "background-color": "#0E1117"},
    "nav-link": {"font-size": "1.1rem", "--hover-color": "#262730"},
    "nav-link-selected": {"background-color": "#007bff"},
  }
)

st.write("---") 


# modo 1 - português -> lógica
if selected_mode == "Português ⭢ Lógica":
  
  st.markdown("Esse modo traduz da linguagem humana para a linguagem formal do Cálculo Proposicional Clássico (CPC).")
  st.subheader("Insira a sentença")
  
  nl_input = st.text_area(
    "Label (escondido)",
    placeholder="Exemplo: Se não estiver chovendo, eu vou a praia.",
    label_visibility="collapsed",
    height=80
  )

  if st.button("Traduzir para CPC", key="nl_button", disabled=(api_key is None), use_container_width=True):
    
    if not nl_input:
      st.warning("Por favor, insira uma sentença.")
    else:
      with st.spinner("A IA (Gemini) está pensando..."): 
        try:
          result = lp.translate_nl_to_cpc(nl_input, api_key)
          
          st.subheader("Resultado (Lógica CPC):")
          with st.container(border=True):
            if "error" in result:
              st.error(f"Erro da API: {result['error']}")
            else:
              st.markdown("**Fórmula Lógica:**")
              st.code(result.get("formula"), language="plaintext")
              
              st.markdown("**Proposições:**")
              propositions = result.get("propositions", {})
              for key, value in propositions.items():
                st.markdown(f"- **`{key}`** = {value}")
        
        except Exception as e:
          st.error(f"Ocorreu um erro inesperado: {e}")

# modo 2 - lógica -> português
if selected_mode == "Lógica ⭢ Português":
  st.markdown("Esse modo traduz do Cálculo Proposicional Clássico (CPC) para uma sentença gerada em linguagem natural.")
  
  st.subheader("Insira a Fórmula")
  
  cpc_input = st.text_area(
    "Label (escondido)",
    placeholder="Exemplo: (P ∧ Q) -> R",
    label_visibility="collapsed",
    height=80
  )

  if st.button("Traduzir para Português", key="translate_button", disabled=(api_key is None), use_container_width=True):
    
    variables = lp.get_variables_from_formula(cpc_input)
    
    if not cpc_input:
      st.error("Por favor, insira uma fórmula lógica.")
    elif not variables and cpc_input: 
      st.error("Fórmula inválida! Verifique os parênteses e conectivos.")
    else:
      with st.spinner("A IA (Gemini) está criando um exemplo..."):
        try:
          result = lp.translate_cpc_to_nl_AI(cpc_input, api_key)
          
          st.subheader("Resultado (Português):")
          with st.container(border=True):
            if "error" in result:
              st.error(f"Erro da API: {result['error']}")
            else:
              st.markdown("**Sentença em Português:**")
              st.markdown(f"### 💬 *{result.get('sentence')}*")
              
              st.markdown("**Proposições:**")
              propositions = result.get("propositions", {})
              for key, value in propositions.items():
                st.markdown(f"- **`{key}`** = {value}")
        
        except Exception as e:
          st.error(f"Ocorreu um erro inesperado: {e}")

  # Seção de Sintaxe reestruturada
  st.subheader("Sintaxe Aceitas:")
  
  syntax_data = [
      ("E (AND)", "&", "∧"),
      ("OU (OR)", "|", "∨"),
      ("NÃO (NOT)", "~", "¬"),
      ("IMPLICA", "->", "→"),
      ("SE E SOMENTE SE", "<->", "↔")
  ]
  
  for name, ascii_sym, unicode_sym in syntax_data:
      with st.container(): 
          st.markdown(f"<div class='syntax-item'>", unsafe_allow_html=True) 
          st.markdown(f"{name}") 
          
          with st.container():
              st.markdown("<div class='symbol-pair-container'>", unsafe_allow_html=True)
              cols = st.columns(2) 
              with cols[0]:
                  st.code(ascii_sym, language='text')
              with cols[1]:
                  st.code(unicode_sym, language='text')
              st.markdown("</div>", unsafe_allow_html=True)

          st.markdown("</div>", unsafe_allow_html=True)
      st.divider() 

  st.markdown("- Proposições devem ser letras **MAIÚSCULAS** (P, Q, A, B)")