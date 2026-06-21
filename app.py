import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="ESG Аналитика", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('df_USA_for_models.csv')

df = load_data()

st.title("📊 ESG & Financial Benchmarking")

# Вкладки для разделения функционала
tab1, tab2 = st.tabs(["🔍 Профиль и Радар", "⚖️ Сравнитель компаний"])

with tab1:
    st.header("Анализ отдельной компании")
    selected_ticker = st.selectbox("Выберите компанию для детального анализа", df['ticker'].unique())
    company_data = df[df['ticker'] == selected_ticker].iloc[0]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Основные метрики")
        st.write(f"**Название:** {company_data['name']}")
        st.write(f"**Сектор:** {company_data['sector']}")
        st.metric("Total ESG Score", company_data['total_score'])
        st.metric("Market Cap", f"{company_data['market_cap']:.2f}")

    with col2:
        st.subheader("ESG Профиль (Радар)")
        categories = ['Environment', 'Social', 'Governance']
        values = [company_data['environment_score'], company_data['social_score'], company_data['governance_score']]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name=company_data['ticker']))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
        st.plotly_chart(fig)

with tab2:
    st.header("Сравнение компаний")
    selected_tickers = st.multiselect("Выберите до 5 компаний для сравнения", df['ticker'].unique(), default=df['ticker'][:2])
    
    if selected_tickers:
        comp_df = df[df['ticker'].isin(selected_tickers)]
        
        # Сравнительная таблица
        st.write("Сравнение ключевых показателей:")
        st.dataframe(comp_df[['ticker', 'name', 'total_score', 'roe', 'pe', 'debt_to_capital']])
        
        # Сравнительный график
        st.subheader("Сравнение Total Score")
        st.bar_chart(comp_df.set_index('ticker')['total_score'])
    else:
        st.info("Пожалуйста, выберите компании в списке выше.")
