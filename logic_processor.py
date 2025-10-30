# logic_processor.py

import sympy
from sympy.logic.boolalg import Implies, Equivalent
import google.generativeai as genai
import json
import re
import streamlit as st


# modo 1 - português -> lógica (gemini)
@st.cache_data
def translate_nl_to_cpc(sentence: str, api_key: str) -> dict:
  try:
    genai.configure(api_key=api_key)
    
    generation_config = {
      "temperature": 0.1,
      "response_mime_type": "application/json", 
    }
    
    model = genai.GenerativeModel(
      model_name="models/gemini-flash-latest",
      generation_config=generation_config,
    )

    prompt_template = f"""
    Sua tarefa é atuar como um especialista em lógica proposicional.
    Traduza a seguinte sentença em português para uma fórmula de Cálculo Proposicional Clássico (CPC).

    Regras de Formatação da Saída:
    1.  Use 'P', 'Q', 'R', etc., para as proposições atômicas.
    2.  Use os seguintes símbolos para os conectivos:
        - E (and): &
        - OU (or): |
        - NÃO (not): ~
        - IMPLICA (if... then...): ->
        - SE E SOMENTE SE (iff): <->
    3.  Retorne a resposta APENAS no seguinte formato JSON.
    
    Exemplo de JSON:
    {{
      "formula": "P -> (Q | R)",
      "propositions": {{
        "P": "significado de P",
        "Q": "significado de Q",
        "R": "significado de R"
      }}
    }}

    Sentença de Entrada para Traduzir:
    "{sentence}"
    
    JSON de Saída:
    """
    
    response = model.generate_content(prompt_template)
    cleaned_response = response.text.strip().replace("```json\n", "").replace("\n```", "")
    result_dict = json.loads(cleaned_response)
    
    return result_dict

  except Exception as e:
    print(f"Erro na API do Gemini: {e}")
    return {"error": str(e)}


# modo 2 - lógica -> português (gemini)
try:
  _A, _B = sympy.symbols('A B')
  OPERADOR_RSHIFT = sympy.sympify('_A >> _B').func
  OPERADOR_MOD = sympy.sympify('_A % _B').func
except Exception:
  OPERADOR_RSHIFT = None
  OPERADOR_MOD = None


@st.cache_data
def get_variables_from_formula(formula_str: str) -> set:
  if not formula_str:
    return set()

  try:
    processed_str = formula_str.replace("∧", "&") \
                               .replace("∨", "|") \
                               .replace("¬", "~") \
                               .replace("→", "->") \
                               .replace("↔", "<->") \
                               .replace("<->", "%") \
                               .replace("->", ">>")

    symbol_names = sorted(list(set(re.findall(r'[A-Z]', formula_str))))
    symbols_dict = {}
    if symbol_names:
      for name in symbol_names:
        symbols_dict[name] = sympy.symbols(name)
    
    parsed_formula = sympy.sympify(processed_str, locals=symbols_dict)
        
    if OPERADOR_RSHIFT and ">>" in processed_str:
      parsed_formula = parsed_formula.subs(OPERADOR_RSHIFT, Implies)
    if OPERADOR_MOD and "%" in processed_str:
      parsed_formula = parsed_formula.subs(OPERADOR_MOD, Equivalent)
        
    atoms = parsed_formula.atoms(sympy.Symbol)
    
    return {str(atom) for atom in atoms}
  
  except Exception as e:
    print(f"Erro ao parsear a fórmula: {e}")
    return set() 

@st.cache_data
def translate_cpc_to_nl_AI(formula_str: str, api_key: str) -> dict:
  try:
    genai.configure(api_key=api_key)
    
    generation_config = {
      "temperature": 0.7, 
      "response_mime_type": "application/json",
    }
    
    model = genai.GenerativeModel(
      model_name="models/gemini-flash-latest",
      generation_config=generation_config,
    )
    
    prompt_template = f"""
    Sua tarefa é atuar como um professor de lógica criativo.
    Você receberá uma fórmula de Cálculo Proposicional Clássico (CPC).
    
    Sua missão é:
    1.  Analisar a fórmula: {formula_str}
    2.  Inventar um conjunto de proposições simples e coerentes (P, Q, R, etc.) do mundo real, em português do Brasil.
    3.  Usar essas proposições para construir uma única frase de exemplo, em português, que corresponda perfeitamente à estrutura lógica da fórmula.
    4.  A frase deve ser natural e fácil de entender, como no exemplo: "Se chover e fizer frio, então a aula será cancelada."

    Retorne a resposta APENAS no seguinte formato JSON:
    {{
      "sentence": "Sua frase de exemplo coerente aqui.",
      "propositions": {{
        "P": "O que P significa (ex: chover)",
        "Q": "O que Q significa (ex: fizer frio)",
        "R": "O que R significa (ex: a aula será cancelada)"
      }}
    }}
    (Se a fórmula tiver ~S, a proposição 'S' deve ser a versão positiva. Ex: S = "Eu vou sair")

    Fórmula de Entrada:
    "{formula_str}"
    
    JSON de Saída:
    """
    
    response = model.generate_content(prompt_template)
    cleaned_response = response.text.strip().replace("```json\n", "").replace("\n```", "")
    result_dict = json.loads(cleaned_response)
    
    return result_dict

  except Exception as e:
    print(f"Erro na API do Gemini (Modo 2): {e}")
    return {"error": str(e)}