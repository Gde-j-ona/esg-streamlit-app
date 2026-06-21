import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="ESG Invest Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('df_USA_for_models.csv')

df = load_data()

st.title("💼 ESG Инвестиционный Дашборд")

# Выбор компании
ticker = st.sidebar.selectbox("Выберите компанию для анализа", df['ticker'].unique())
company = df[df['ticker'] == ticker].iloc[0]
sector_df = df[df['sector'] == company['sector']]

# --- КАРТОЧКИ KPI ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Рыночная капитализация", f"{company['market_cap']:.1f}B")
col2.metric("Total ESG Score", company['total_score'], company['total_level'])
col3.metric("ROE", f"{company['roe']:.1%}")
col4.metric("P/E Ratio", f"{company['pe']:.2f}")

st.markdown("---")

# --- СЕКТОРАЛЬНЫЙ АНАЛИЗ ---
st.subheader(f"Позиция в секторе: {company['sector']}")
# Создаем график, где текущая компания выделена цветом
sector_df = sector_df.copy()
sector_df['is_selected'] = sector_df['ticker'] == ticker

fig_bar = px.bar(
    sector_df, x='ticker', y='total_score', 
    color='is_selected', 
    color_discrete_map={True: '#FF4B4B', False: '#1f77b4'},
    title="Сравнение Total ESG Score в секторе"
)
st.plotly_chart(fig_bar, use_container_width=True)

# --- ESG РАСПРЕДЕЛЕНИЕ ---
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("ESG Составляющие")
    labels = ['Environment', 'Social', 'Governance']
    values = [company['environment_score'], company['social_score'], company['governance_score']]
    fig_pie = px.pie(values=values, names=labels, hole=0.4, title="Структура ESG рейтинга")
    st.plotly_chart(fig_pie, use_container_width=True)

with col_b:
    st.subheader("Финансовые мультипликаторы")
    fin_data = pd.DataFrame({
        'Метрика': ['ROE', 'ROA', 'Debt/Capital', 'Current Ratio'],
        'Значение': [company['roe'], company['roa'], company['debt_to_capital'], company['current_ratio']]
    })
    st.table(fin_data)

# --- ИНВЕСТИЦИОННЫЙ ВЫВОД ---
st.markdown("---")
st.subheader("Аналитическая сводка")
if company['total_score'] > 70 and company['pe'] < 20:
    st.success("Компания выглядит привлекательно: высокий ESG-рейтинг при разумной оценке.")
elif company['total_score'] < 40:
    st.warning("Внимание: низкие показатели устойчивого развития могут нести репутационные риски.")
else:
    st.info("Компания имеет средние показатели по рынку.")
