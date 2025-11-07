# frontend.py
import streamlit as st
from backend import login_api, extrair_dados
from datetime import datetime

st.set_page_config(page_title="Extrator Financeiro", page_icon="💰", layout="wide")

st.title("💰 Sistema de Extração Financeira")
st.markdown("Selecione o período e as unidades para extrair os dados.")

# --- Inputs ---
email = st.text_input("E-mail", "alisson.marchiori@finanto.com.br")
senha = st.text_input("Senha", "#Alisson.2025", type="password")

col1, col2 = st.columns(2)
data_inicio = col1.date_input("Data Início")
data_fim = col2.date_input("Data Fim")

# Dicionário de unidades
unidades_dict = {
    "CALLCENTER": 4,
    "FINANTO BUSINESS": 1,
    "FINANTO HUB": 2,
    "FINANTO TECH": 3
}

unidades_selecionadas = st.multiselect(
    "Selecione as Unidades (pode escolher várias)",
    options=list(unidades_dict.keys()),
    default=["CALLCENTER"]
)

# --- Botão principal ---
if st.button("🚀 Extrair Dados"):
    try:
        with st.spinner("Realizando login..."):
            token = login_api(email, senha)

        with st.spinner("Consultando API e gerando relatório..."):
            df = extrair_dados(
                token,
                data_inicio.strftime("%Y-%m-%d"),
                data_fim.strftime("%Y-%m-%d"),
                unidades_dict,
                unidades_selecionadas
            )

        if df.empty:
            st.warning("Nenhum dado retornado para os filtros selecionados.")
        else:
            st.success(f"✅ {len(df)} registros obtidos!")
            st.dataframe(df)

            # Download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            file_name = f"extracao_financeira_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            st.download_button(
                label="📥 Baixar CSV",
                data=csv,
                file_name=file_name,
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"❌ Erro: {e}")
