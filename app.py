import os
import json
import pandas as pd
from groq import Groq
from pypdf import PdfReader
import streamlit as st

st.set_page_config(
    page_title="Empório da Música - Atendimento",
    page_icon="🎸",
    layout="centered"
)

client = Groq()

DATA_DIR = "data"

@st.cache_data
def load_data():
    try:
        products = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
        orders = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))
        customers = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
        promotions = pd.read_csv(os.path.join(DATA_DIR, "promotions.csv"))
        return products, orders, customers, promotions
    except Exception as e:
        return None, None, None, None

products_df, orders_df, customers_df, promotions_df = load_data()

@st.cache_data
def load_policies():
    pdf_path = os.path.join(DATA_DIR, "politicas_da_loja.pdf")
    if not os.path.exists(pdf_path):
        return "Manual de políticas não encontrado."
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

policies_text = load_policies()

def search_products(query: str = "") -> str:
    """Busca produtos no catálogo da Empório da Música por nome ou descrição."""
    if products_df is None:
        return "Catálogo indisponível."
    if query:
        result = products_df[
            products_df['name'].str.contains(query, case=False, na=False) | 
            products_df['description'].str.contains(query, case=False, na=False)
        ]
    else:
        result = products_df.head(10)
    
    if result.empty:
        return "Nenhum produto encontrado com esse termo."
        
    return result[['product_id', 'name', 'price_brl', 'stock_quantity', 'status']].to_string(index=False)

def check_order_status(order_id: str) -> str:
    """Verifica o status de um pedido pelo ID."""
    if orders_df is None:
        return "Dados de pedidos indisponíveis."
    result = orders_df[orders_df['order_id'].astype(str) == str(order_id)]
    if result.empty:
        return f"Pedido {order_id} não encontrado."
    return result.to_string(index=False)

def query_store_policies(topic: str) -> str:
    """Consulta regras, prazos, formas de pagamento e políticas de troca no manual da loja."""
    lines = policies_text.split('\n')
    relevant_lines = [line for line in lines if topic.lower() in line.lower()]
    if not relevant_lines:
        return "Nenhuma regra específica encontrada para o tópico."
    return "\n".join(relevant_lines[:15])

tools_map = {
    "search_products": search_products,
    "check_order_status": check_order_status,
    "query_store_policies": query_store_policies
}

groq_tools = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Busca instrumentos musicais, preços e disponibilidade no catálogo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Nome do instrumento ou categoria."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": "Verifica o status, rastreamento e dados de um pedido do cliente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "ID ou código do pedido."}
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_store_policies",
            "description": "Consulta regras de troca, devolução, garantia, formas de pagamento e frete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Tópico da dúvida."}
                },
                "required": ["topic"]
            }
        }
    }
]

st.title("🎸 Empório da Música")
st.caption("Seu assistente virtual de atendimento especializado em instrumentos musicais (Campo Grande/MS)")

system_prompt = """
Você é o assistente virtual da "Empório da Música", uma loja de instrumentos musicais de Campo Grande/MS.
Sua missão é atender clientes via WhatsApp com um tom informal, mas profissional.
1. Trabalhamos EXCLUSIVAMENTE com instrumentos musicais. NUNCA venda acessórios.
2. Nunca invente preços, estoque ou prazos. Sempre utilize as ferramentas disponíveis.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

for message in st.session_state.messages:
    role = message.get("role")
    content = message.get("content")
    if role != "system" and content:
        with st.chat_message(role):
            st.markdown(content)

if user_input := st.chat_input("Digite sua dúvida (ex: Quanto custa o Takamine GD20?)..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=st.session_state.messages,
            tools=groq_tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            tool_calls_dicts = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in response_message.tool_calls
            ]
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_message.content or "",
                "tool_calls": tool_calls_dicts
            })
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_to_call = tools_map[function_name]
                function_args = json.loads(tool_call.function.arguments)
                
                tool_output = function_to_call(**function_args)
                
                st.session_state.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(tool_output),
                })
            
            second_response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=st.session_state.messages
            )
            final_message = second_response.choices[0].message.content
            
            st.session_state.messages.append({"role": "assistant", "content": final_message})
            
            with st.chat_message("assistant"):
                st.markdown(final_message)
        else:
            final_content = response_message.content
            st.session_state.messages.append({"role": "assistant", "content": final_content})
            with st.chat_message("assistant"):
                st.markdown(final_content)
                
    except Exception as e:
        st.error(f"Ocorreu um erro ao comunicar com a IA: {e}")
        