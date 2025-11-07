# frontend.py
import streamlit as st
from backend import login_api, extrair_dados
from datetime import datetime

st.set_page_config(page_title="Extrator de Dados - Gestão", page_icon="💼", layout="wide")

st.title("💼 Extração de Dados Geral - Gestão")
st.markdown("Use seu login para acessar os dados e gerar relatórios customizados.")

# --- LOGIN ---
with st.expander("🔐 Login no sistema", expanded=True):
    email = st.text_input("E-mail corporativo")
    senha = st.text_input("Senha", type="password")
    login_btn = st.button("Entrar")

# Variável de sessão para armazenar token
if "token" not in st.session_state:
    st.session_state["token"] = None

# Realiza login
if login_btn:
    try:
        with st.spinner("Realizando login..."):
            token = login_api(email, senha)
            st.session_state["token"] = token
            st.success("✅ Login realizado com sucesso!")
    except Exception as e:
        st.error(f"❌ Erro no login: {e}")

# Só mostra filtros se o login foi bem-sucedido
if st.session_state["token"]:
    st.divider()
    st.subheader("📆 Filtros de extração")

    col1, col2 = st.columns(2)
    data_inicio = col1.date_input("Data Início")
    data_fim = col2.date_input("Data Fim")

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

    # Botão para extrair dados
    if st.button("🚀 Extrair Dados"):
        try:
            with st.spinner("Consultando API e gerando relatório..."):
                df = extrair_dados(
                    st.session_state["token"],
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

                csv = df.to_csv(index=False).encode('utf-8')
                file_name = f"extracao_dados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                st.download_button(
                    label="📥 Baixar CSV",
                    data=csv,
                    file_name=file_name,
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"❌ Erro durante a extração: {e}")
