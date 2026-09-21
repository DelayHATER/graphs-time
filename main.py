import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


# ==============================
# 데이터 불러오기
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d"
    )

    # 숫자형 데이터 변환
    numeric_columns = [
        "순위",
        "영화코드",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.sort_values("날짜")

    return df


df = load_data()


# ==============================
# 제목
# ==============================
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.write(
    "최근 1년간 영화관 일일 관객 데이터를 시간에 따라 분석합니다."
)


# =========================================================
# 그래프 1
# =========================================================
st.header("그래프 1. 영화별 일관객 변화")

movie_list = sorted(
    df["영화명"].dropna().unique().tolist()
)

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_list
)

movie_df = df[
    df["영화명"] == selected_movie
].sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"{selected_movie}의 날짜별 일관객"
)

fig1.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,.0f}명<extra></extra>"
)

fig1.update_layout(
    hovermode="closest",
    xaxis_title="날짜",
    yaxis_title="일관객"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.info(
    "이 그래프로 알 수 있는 것: 영화의 개봉 이후 일관객이 시간에 따라 어떻게 변화했는지 확인할 수 있습니다."
)


# =========================================================
# 그래프 2
# =========================================================
st.divider()
st.header("그래프 2. 기간 내 일관객 합계 상위 5편의 변화")

movie_total = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
)

top5_movies = movie_total.head(5)["영화명"].tolist()

top5_df = df[
    df["영화명"].isin(top5_movies)
].sort_values("날짜")

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="기간 내 일관객 합계 상위 5편의 날짜별 일관객"
)

fig2.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,.0f}명<extra></extra>"
)

fig2.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객",
    legend_title="영화"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.info(
    "이 그래프로 알 수 있는 것: 기간 전체에서 관객이 많았던 영화들의 흥행 추세를 서로 비교할 수 있습니다."
)


# =========================================================
# 그래프 3
# =========================================================
st.divider()
st.header("그래프 3. 날짜별 전체 일관객")

daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

top3_days = (
    daily_total.nlargest(3, "일관객")
    .sort_values("날짜")
)

fig3 = go.Figure()

# 전체 일관객 영역 그래프
fig3.add_trace(
    go.Scatter(
        x=daily_total["날짜"],
        y=daily_total["일관객"],
        mode="lines",
        fill="tozeroy",
        name="전체 일관객",
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>전체 일관객: %{y:,.0f}명<extra></extra>"
    )
)

# 최고 관객 3일 표시
fig3.add_trace(
    go.Scatter(
        x=top3_days["날짜"],
        y=top3_days["일관객"],
        mode="markers+text",
        name="관객 최고 3일",
        text=[
            f"{value:,.0f}명"
            for value in top3_days["일관객"]
        ],
        textposition="top center",
        marker=dict(size=10),
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>전체 일관객: %{y:,.0f}명<extra></extra>"
    )
)

fig3.update_layout(
    title="날짜별 전체 일관객",
    xaxis_title="날짜",
    yaxis_title="일관객",
    hovermode="x unified"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.subheader("관객이 가장 많았던 날짜 TOP 3")

for i, (_, row) in enumerate(
    top3_days.sort_values(
        "일관객",
        ascending=False
    ).iterrows(),
    start=1
):
    st.write(
        f"{i}위. {row['날짜'].strftime('%Y-%m-%d')} — "
        f"{row['일관객']:,.0f}명"
    )

st.info(
    "이 그래프로 알 수 있는 것: 날짜에 따라 영화관 전체 관객 수가 언제 크게 증가하거나 감소했는지 확인할 수 있습니다."
)


# =========================================================
# 그래프 4
# =========================================================
st.divider()
st.header("그래프 4. 기간 내 일관객 합계 TOP 10")

movie_summary = (
    df.groupby("영화명")
    .agg(
        총_일관객=("일관객", "sum"),
        등장일수=("날짜", "nunique")
    )
    .reset_index()
    .sort_values(
        "총_일관객",
        ascending=False
    )
    .head(10)
)

# 가로 막대그래프에서 가장 큰 값이 위에 오도록 뒤집기
movie_summary = movie_summary.sort_values(
    "총_일관객",
    ascending=True
)

fig4 = go.Figure()

fig4.add_trace(
    go.Bar(
        x=movie_summary["총_일관객"],
        y=movie_summary["영화명"],
        orientation="h",
        customdata=movie_summary["등장일수"],
        hovertemplate=(
            "영화: %{y}<br>"
            "기간 내 총 일관객: %{x:,.0f}명<br>"
            "10위권 등장일수: %{customdata}일"
            "<extra></extra>"
        )
    )
)

fig4.update_layout(
    title="기간 내 일관객 합계 TOP 10",
    xaxis_title="기간 내 총 일관객",
    yaxis_title="영화",
    hovermode="closest"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.info(
    "이 그래프로 알 수 있는 것: 해당 기간 동안 누적된 일관객이 가장 많았던 영화와 10위권에 등장한 기간을 비교할 수 있습니다."
)


# =========================================================
# 그래프 5
# =========================================================
st.divider()
st.header("그래프 5. 월 × 요일별 일관객 히트맵")

# 월
df["월"] = df["날짜"].dt.month

# 요일
weekday_map = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일"
}

df["요일"] = df["날짜"].dt.weekday.map(weekday_map)

weekday_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]

heatmap_data = (
    df.groupby(
        ["월", "요일"],
        as_index=False
    )["일관객"]
    .sum()
)

heatmap_pivot = heatmap_data.pivot(
    index="월",
    columns="요일",
    values="일관객"
)

heatmap_pivot = heatmap_pivot.reindex(
    index=range(1, 13),
    columns=weekday_order
)

fig5 = px.imshow(
    heatmap_pivot,
    labels={
        "x": "요일",
        "y": "월",
        "color": "일관객"
    },
    x=weekday_order,
    y=list(range(1, 13)),
    text_auto=".3s",
    color_continuous_scale="Blues",
    title="월 × 요일별 일관객 합계"
)

fig5.update_traces(
    hovertemplate=(
        "%{y}월 %{x}<br>"
        "일관객: %{z:,.0f}명"
        "<extra></extra>"
    )
)

fig5.update_layout(
    xaxis_title="요일",
    yaxis_title="월"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.info(
    "이 그래프로 알 수 있는 것: 어느 월과 요일에 영화관 관객이 상대적으로 많이 몰렸는지 한눈에 확인할 수 있습니다."
)


# ==============================
# 데이터 출처
# ==============================
st.divider()

st.caption(
    "데이터 출처: 영화진흥위원회(KOBIS)"
)
