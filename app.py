import streamlit as st
import pandas as pd

# Настройка страницы
st.set_page_config(page_title="ESG Financial Dashboard", layout="wide")

# 1. Загрузка данных
@st.cache_data
def load_data():
    # Убедитесь, что файл лежит в той же папке
    df = pd.read_csv('df_USA_for_models.csv')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Ошибка загрузки файла: {e}")
    st.stop()

# 2. Боковая панель (Фильтры)
st.sidebar.header("Навигация")

# Фильтр по сектору
sectors = ["Все"] + sorted(df['sector'].unique().tolist())
selected_sector = st.sidebar.selectbox("Выберите сектор", sectors)

# Фильтр по компании
if selected_sector != "Все":
    filtered_df = df[df['sector'] == selected_sector]
else:
    filtered_df = df

selected_ticker = st.sidebar.selectbox("Выберите компанию (Ticker)", filtered_df['ticker'].unique())

# Получаем данные выбранной компании
company_data = df[df['ticker'] == selected_ticker].iloc[0]

# 3. Основной интерфейс
st.title(f"Аналитика: {company_data['name']}")
st.subheader(f"Тикер: {company_data['ticker']} | Сектор: {company_data['sector']}")

# Блок ESG показателей
st.markdown("---")
st.header("ESG Метрики")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Score", company_data['total_score'], help=f"Level: {company_data['total_level']}")
col2.metric("Environment", company_data['environment_score'], help=f"Level: {company_data['environment_level']}")
col3.metric("Social", company_data['social_score'], help=f"Level: {company_data['social_level']}")
col4.metric("Governance", company_data['governance_score'], help=f"Level: {company_data['governance_level']}")

# Блок Финансовых показателей
st.markdown("---")
st.header("Финансовые показатели")
f_col1, f_col2, f_col3 = st.columns(3)

f_col1.metric("Market Cap", f"{company_data['market_cap']:.2f}" if pd.notnull(company_data['market_cap']) else "N/A")
f_col2.metric("Revenue", f"{company_data['total_revenue']:,.0f}" if pd.notnull(company_data['total_revenue']) else "N/A")
f_col3.metric("PE Ratio", f"{company_data['pe']:.2f}" if pd.notnull(company_data['pe']) else "N/A")

f_col1.metric("ROE", f"{company_data['roe']:.2%}" if pd.notnull(company_data['roe']) else "N/A")
f_col2.metric("ROA", f"{company_data['roa']:.2%}" if pd.notnull(company_data['roa']) else "N/A")
f_col3.metric("Debt/Capital", f"{company_data['debt_to_capital']:.2f}" if pd.notnull(company_data['debt_to_capital']) else "N/A")

# Блок детальной информации (таблица)
with st.expander("Посмотреть полные данные компании"):
    st.write(company_data)

# Блок сравнения (простой график)
st.markdown("---")
st.header(f"Сравнение компаний в секторе: {company_data['sector']}")
st.bar_chart(filtered_df.set_index('ticker')['total_score'])