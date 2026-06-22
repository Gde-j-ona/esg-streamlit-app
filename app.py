
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="ESG Invest Dashboard",
    layout="wide"
)


@st.cache_data
def load_data():
    return pd.read_csv("df_USA_for_models.csv")


df = load_data()

def format_market_cap(value):
    if pd.isna(value):
        return "N/A"

    # триллионы
    if value >= 1e12:
        return f"${value / 1e12:.2f}T"

    # миллиарды
    elif value >= 1e9:
        return f"${value / 1e9:.2f}B"

    # миллионы
    elif value >= 1e6:
        return f"${value / 1e6:.2f}M"

    # тысячи
    elif value >= 1e3:
        return f"${value / 1e3:.2f}K"

    else:
        return f"${value:.2f}"

st.title("💼 ESG Инвестиционный Дашборд")

# =========================
# ВЫБОР СЕКТОРА И КОМПАНИИ
# =========================

sectors = sorted(df["sector"].dropna().unique())

selected_sector = st.sidebar.selectbox(
    "Выберите сектор",
    sectors
)

sector_df = (
    df[df["sector"] == selected_sector]
    .sort_values("ticker")
)

ticker = st.sidebar.selectbox(
    "Выберите компанию",
    sector_df["ticker"].tolist()
)

company = sector_df[sector_df["ticker"] == ticker].iloc[0]

# =========================
# KPI
# =========================

col1, col2, col3, col4 = st.columns(4)

market_cap = company["market_cap"]
pe = company["pe"]
roe = company["roe"]

col1.metric(
    "Рыночная капитализация",
    format_market_cap(market_cap)
)

col2.metric(
    "Total ESG Score",
    f"{company['total_score']}",
    company["total_level"]
)

col3.metric(
    "ROE",
    f"{roe:.1%}" if pd.notna(roe) else "N/A"
)

col4.metric(
    "P/E Ratio",
    f"{pe:.2f}" if pd.notna(pe) else "N/A"
)

st.markdown("---")

# =========================
# СЕКТОРАЛЬНЫЙ АНАЛИЗ
# =========================

st.subheader(f"Позиция в секторе: {selected_sector}")

plot_df = sector_df.copy()
plot_df["is_selected"] = plot_df["ticker"] == ticker

fig_bar = px.bar(
    plot_df,
    x="ticker",
    y="total_score",
    color="is_selected",
    color_discrete_map={
        True: "#FF4B4B",
        False: "#1f77b4"
    },
    title="Сравнение Total ESG Score внутри сектора"
)

fig_bar.update_layout(showlegend=False)

st.plotly_chart(
    fig_bar,
    use_container_width=True
)

# =========================
# ESG + ФИНАНСЫ
# =========================

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("ESG Составляющие")

    labels = [
        "Environment",
        "Social",
        "Governance"
    ]

    values = [
        company["environment_score"],
        company["social_score"],
        company["governance_score"]
    ]

    fig_pie = px.pie(
        values=values,
        names=labels,
        hole=0.45
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

with col_b:
    st.subheader("Финансовые показатели")

    fin_data = pd.DataFrame(
        {
            "Метрика": [
                "ROE",
                "ROA",
                "Debt/Capital",
                "Current Ratio",
                "P/E",
                "Beta"
            ],
            "Значение": [
                company["roe"],
                company["roa"],
                company["debt_to_capital"],
                company["current_ratio"],
                company["pe"],
                company["beta"]
            ],
        }
    )

    st.table(fin_data)

# ==========================================================
# ИНВЕСТИЦИОННЫЙ СКОРИНГ
# ==========================================================

st.markdown("---")
st.subheader("Инвестиционный анализ")

score = 0

esg_score = 0
finance_score = 0
risk_score = 0

strengths = []
risks = []
reasons = []

# ================= ESG =================

if company["total_score"] >= 80:
    esg_score = 10
    score += 3
    strengths.append("очень высокий ESG-рейтинг")
    reasons.append("высокий ESG-рейтинг")

elif company["total_score"] >= 70:
    esg_score = 8
    score += 2
    strengths.append("высокий ESG-рейтинг")
    reasons.append("высокий ESG-рейтинг")

elif company["total_score"] >= 50:
    esg_score = 6
    score += 1

else:
    esg_score = 3
    risks.append("низкий ESG-рейтинг")

# ================= ФИНАНСЫ =================

if pd.notna(company["roe"]):
    if company["roe"] >= 0.15:
        finance_score += 4
        score += 2
        strengths.append("высокая рентабельность капитала")
        reasons.append("высокая рентабельность")

    elif company["roe"] >= 0.08:
        finance_score += 2
        score += 1

    elif company["roe"] < 0:
        risks.append("отрицательная рентабельность")

if pd.notna(company["roa"]):
    if company["roa"] >= 0.05:
        finance_score += 2

if pd.notna(company["pe"]):
    if 0 < company["pe"] < 20:
        finance_score += 3
        score += 2
        reasons.append("разумная рыночная оценка")

    elif company["pe"] >= 35:
        risks.append("завышенный P/E")

    elif company["pe"] <= 0:
        risks.append("отрицательный P/E (убыток компании)")

if pd.notna(company["pb"]):
    if company["pb"] < 3:
        finance_score += 1

finance_score = min(finance_score, 10)

# ================= РИСК =================

risk_score = 10

if pd.notna(company["debt_to_capital"]):
    if company["debt_to_capital"] < 0.4:
        strengths.append("низкая долговая нагрузка")
        reasons.append("низкий уровень долга")

    elif company["debt_to_capital"] > 0.7:
        risk_score -= 3
        risks.append("высокая долговая нагрузка")

if pd.notna(company["current_ratio"]):
    if company["current_ratio"] < 1:
        risk_score -= 2
        risks.append("низкая ликвидность")

if pd.notna(company["beta"]):
    if company["beta"] > 1.5:
        risk_score -= 3
        risks.append("высокая β")

if pd.notna(company["net_income"]):
    if company["net_income"] < 0:
        risk_score -= 2
        risks.append("отрицательная чистая прибыль")

risk_score = max(risk_score, 1)

# ================= ИТОГОВЫЙ БАЛЛ =================

total_points = esg_score + finance_score + risk_score

if total_points >= 24:
    recommendation = "BUY"
    recommendation_text = (
        "Компания выглядит привлекательно благодаря: "
        + ", ".join(set(reasons))
    )
    recommendation_type = st.success

elif total_points >= 16:
    recommendation = "HOLD"
    recommendation_text = (
        "Компания имеет смешанный профиль и требует дополнительного анализа."
    )
    recommendation_type = st.info

else:
    recommendation = "AVOID"
    recommendation_text = (
        "Компания демонстрирует повышенный уровень финансовых рисков."
    )
    recommendation_type = st.warning

# ================= КАРТОЧКИ РЕЙТИНГА =================

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("ESG", f"{esg_score}/10")
c2.metric("Финансы", f"{finance_score}/10")
c3.metric("Риск", f"{risk_score}/10")
c4.metric("Итоговый балл", f"{total_points}/30")
c5.metric("Рекомендация", recommendation)

recommendation_type(recommendation_text)

# ================= СИЛЬНЫЕ СТОРОНЫ И РИСКИ =================

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Сильные стороны")

    if len(strengths) == 0:
        st.write("Выраженные преимущества отсутствуют.")
    else:
        for item in sorted(set(strengths)):
            st.write(f"✅ {item}")

with col_right:
    st.subheader("Основные риски")

    if len(risks) == 0:
        st.write("Существенные риски не выявлены.")
    else:
        for item in sorted(set(risks)):
            st.write(f"⚠️ {item}")

# ==========================================================
# РАДАР
# ==========================================================

st.markdown("---")
st.subheader("Профиль компании")

esg_norm = esg_score / 10
finance_norm = finance_score / 10
risk_norm = risk_score / 10

roe_norm = 0
if pd.notna(company["roe"]):
    roe_norm = np.clip(company["roe"] / 0.30, 0, 1)

debt_norm = 0
if pd.notna(company["debt_to_capital"]):
    debt_norm = np.clip(
        1 - company["debt_to_capital"],
        0,
        1
    )

radar_values = [
    esg_norm,
    finance_norm,
    risk_norm,
    roe_norm,
    debt_norm
]

categories = [
    "ESG",
    "Финансы",
    "Риск",
    "ROE",
    "Долг"
]

fig_radar = go.Figure()

fig_radar.add_trace(
    go.Scatterpolar(
        r=radar_values,
        theta=categories,
        fill="toself",
        name=ticker
    )
)

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 1]
        )
    ),
    showlegend=False,
    height=500
)

st.plotly_chart(
    fig_radar,
    use_container_width=True
)
