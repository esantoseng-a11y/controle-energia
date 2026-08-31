import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Controle de Energia", page_icon="⚡", layout="centered"
)

# Estilo para aumentar fontes e ajustar botões
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-size: 20px !important;
    }
    .stButton>button {
        width: 100%;
        font-size: 20px !important;
        font-weight: bold !important;
        padding: 10px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Preço do kWh e limites das casas
PRECO_KWH = 0.75
LIMITES = {"Dercilio": 400, "Saulo": 500, "Ricardo": 450, "Aligas": 350}

# Inicializa o estado dos dados
if "casas" not in st.session_state:
    st.session_state.casas = {
        "Dercilio": [],
        "Saulo": [],
        "Ricardo": [],
        "Aligas": [],
    }

st.title("⚡ Controle de Consumo de Energia")

# Formulário para adicionar leitura
st.subheader("➕ Adicionar Leitura Diária")
casa_selecionada = st.selectbox(
    "Selecione a Casa:", list(st.session_state.casas.keys())
)
kwh_input = st.number_input(
    "Consumo (kWh):", min_value=0.0, step=0.1, format="%.2f"
)

if st.button("Salvar Leitura"):
    if kwh_input > 0:
        st.session_state.casas[casa_selecionada].append(kwh_input)
        st.success(
            f"✅ {kwh_input:.2f} kWh adicionados para {casa_selecionada}!"
        )
    else:
        st.warning("⚠️ Digite um valor maior que zero.")

st.divider()

# Resumo e cálculos
st.subheader("📊 Resumo das Casas")
relatorio_texto = "=== RELATÓRIO DE CONSUMO DE ENERGIA ===\n\n"

for nome, leituras in st.session_state.casas.items():
    total_kwh = sum(leituras)
    custo = total_kwh * PRECO_KWH
    limite = LIMITES[nome]

    # Prepara texto para exportação
    relatorio_texto += f"Casa: {nome}\n"
    relatorio_texto += f"Histórico: {leituras}\n"
    relatorio_texto += f"Consumo Total: {total_kwh:.2f} kWh\n"
    relatorio_texto += f"Custo Total: R$ {custo:.2f}\n"
    relatorio_texto += "-" * 40 + "\n"

    # Exibição na tela com cartões
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### 🏠 **{nome}**")
            st.write(f"**Total:** {total_kwh:.2f} kWh")
            st.write(f"**Custo:** R$ {custo:.2f}")
        with col2:
            if total_kwh > limite:
                st.error(
                    f"⚠️ **LIMITE EXCEDIDO!**\n\nMáximo recomendado: {limite} kWh"
                )
            else:
                st.info(f"🟢 Dentro do limite ({limite} kWh)")
        st.divider()

# Botão de exportar arquivo .txt
st.download_button(
    label="📥 Exportar Relatório (.txt)",
    data=relatorio_texto,
    file_name="controle_energia.txt",
    mime="text/plain",
)
