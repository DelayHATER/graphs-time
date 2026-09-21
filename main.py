```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ==========================================================
# 기본 설정
# ==========================================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")

st.write(
    "영화의 박스오피스 데이터를 시간의 흐름에 따라 살펴보는 그래프 도감입니다."
)


# ==========================================================
# 데이터 주소
# ==========================================================

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_daily.csv"
)


# ==========================================================
# 데이터 불러오기
# ==========================================================

@st.cache_data
def load_data():
    # CSV 파일을 불러옵니다.
    df = pd.read_csv(DATA_URL)

    # 날짜를 진짜 날짜 형식으로 변환합니다.
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d"
    )

    # 숫자로 사용할 열들을 숫자형으로 변환합니다.
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

    # 날짜순으로 정렬합니다.
    df = df.sort_values("날짜")

    return df


# ==========================================================
# 데이터 불러오기
# ==========================================================

try:
    df = load_data()

except Exception:
    st.error("❌ 데이터를 불러오는 중 문제가 발생했습니다.")

    st.info(
        "다음 사항을 확인해 주세요.\n\n"
        "• 데이터 주소가 정상인지 확인\n"
        "• GitHub 파일이 존재하는지 확인\n"
        "• 인터넷 연결 상태 확인"
    )

    st.stop()


# ==========================================================
# 데이터 기간
# ==========================================================

min_date = df["날짜"].min()
max_date = df["날짜"].max()

st.caption(
    f"데이터 기간: {min_date.strftime('%Y-%m-%d')} ~ "
    f"{max_date.strftime('%Y-%m-%d')}"
)


# ==========================================================
# 그래프 1
# 시간에 따른 영화의 일관객 변화
# ==========================================================

st.header("1. 시간에 따른 영화의 일관객 변화")

st.write(
    "영화를 하나 선택하면 해당 영화의 날짜별 일관객 변화를 확인할 수 있습니다."
)


# 영화 목록
movie_list = sorted(
    df["영화명"].dropna().unique().tolist()
)


# 영화 선택
selected_movie = st.selectbox(
    "🎬 영화를 선택하세요",
    movie_list
)


# 선택한 영화만 추출
movie_df = df[
    df["영화명"] == selected_movie
].copy()

movie_df = movie_df.sort_values("날짜")


# 선 그래프
fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"{selected_movie}의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    }
)

fig1.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}<br>"
        "관객수: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig1.update_layout(
    hovermode="closest",
    height=500,
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# 그래프 설명 자리
st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "이곳에 그래프를 통해 발견한 영화의 관객 변화 특징을 한 문장으로 작성하세요."
)


# ==========================================================
# 그래프 2
# 기간 일관객 합계 TOP 5 영화의 날짜별 일관객
# ==========================================================

st.divider()

st.header("2. 일관객 합계가 가장 큰 영화 TOP 5")

st.write(
    "이 기간 동안 일관객의 합계가 가장 큰 5편의 날짜별 관객 변화를 비교합니다."
)


# 영화별 일관객 합계 계산
movie_total = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
)

# 상위 5편
top5_movies = movie_total.head(5)["영화명"].tolist()


# TOP 5 영화만 추출
top5_df = df[
    df["영화명"].isin(top5_movies)
].copy()

top5_df = top5_df.sort_values("날짜")


# 여러 영화의 선 그래프
fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 TOP 5 영화의 날짜별 관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화"
    }
)

fig2.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}<br>"
        "관객수: %{y:,.0f}명"
        "<extra>%{fullData.name}</extra>"
    )
)

fig2.update_layout(
    hovermode="closest",
    height=600,
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)",
    legend_title="영화"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.info(
    "범례에서 영화명을 클릭하면 해당 영화의 그래프를 켜거나 끌 수 있습니다."
)


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "이곳에 기간 전체에서 관객 규모가 큰 영화들의 시간에 따른 차이를 한 문장으로 작성하세요."
)


# ==========================================================
# 그래프 3
# 날짜별 10위권 전체 일관객 합계
# ==========================================================

st.divider()

st.header("3. 날짜별 10위권 일관객 합계")

st.write(
    "매일 박스오피스 10위권 영화의 일관객을 모두 더해 전체적인 영화관 관객 규모의 변화를 봅니다."
)


# 날짜별 일관객 합계
daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)


# 가장 관객이 많았던 날짜 3개
top3_days = (
    daily_total
    .nlargest(3, "일관객")
    .sort_values("날짜")
)


# 영역 그래프
fig3 = go.Figure()


fig3.add_trace(
    go.Scatter(
        x=daily_total["날짜"],
        y=daily_total["일관객"],
        mode="lines",
        fill="tozeroy",
        name="10위권 일관객 합계",
        hovertemplate=(
            "날짜: %{x|%Y-%m-%d}<br>"
            "10위권 합계: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)


# 상위 3일 표시
fig3.add_trace(
    go.Scatter(
        x=top3_days["날짜"],
        y=top3_days["일관객"],
        mode="markers+text",
        text=[
            f"{date.strftime('%m/%d')}<br>{value:,.0f}명"
            for date, value
            in zip(
                top3_days["날짜"],
                top3_days["일관객"]
            )
        ],
        textposition="top center",
        marker=dict(
            size=10
        ),
        name="관객수 TOP 3",
        hovertemplate=(
            "날짜: %{x|%Y-%m-%d}<br>"
            "합계: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)


fig3.update_layout(
    title="날짜별 10위권 일관객 합계",
    height=550,
    xaxis_title="날짜",
    yaxis_title="10위권 일관객 합계(명)",
    hovermode="x unified"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


st.subheader("📌 관객수가 가장 많았던 3일")

for _, row in daily_total.nlargest(3, "일관객").iterrows():
    st.write(
        f"**{row['날짜'].strftime('%Y년 %m월 %d일')}** — "
        f"{row['일관객']:,.0f}명"
    )


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "이곳에 기간 중 영화관 전체 관객 규모가 언제 높고 낮았는지 한 문장으로 작성하세요."
)


# ==========================================================
# 그래프 4
# 영화별 기간 일관객 TOP 10
# ==========================================================

st.divider()

st.header("4. 영화별 일관객 TOP 10")

st.write(
    "이 기간 동안 각 영화의 일관객을 모두 합산하여 관객수가 많은 영화부터 보여 줍니다."
)


# 영화별 총 일관객과 10위권 등장 일수 계산
movie_summary = (
    df.groupby("영화명")
    .agg(
        총_일관객=("일관객", "sum"),
        **{"10위권_등장일수": ("날짜", "nunique")}
    )
    .reset_index()
    .sort_values(
        "총_일관객",
        ascending=False
    )
    .head(10)
)


# 많은 영화가 위에 오도록 역순으로 표시하기 위한 데이터
movie_summary_chart = movie_summary.sort_values(
    "총_일관객",
    ascending=True
)


fig4 = go.Figure()


fig4.add_trace(
    go.Bar(
        x=movie_summary_chart["총_일관객"],
        y=movie_summary_chart["영화명"],
        orientation="h",
        customdata=movie_summary_chart["10위권_등장일수"],
        hovertemplate=(
            "<b>%{y}</b><br>"
            "기간 일관객: %{x:,.0f}명<br>"
            "10위권에 든 날: %{customdata}일"
            "<extra></extra>"
        ),
        name="일관객"
    )
)


fig4.update_layout(
    title="영화별 기간 일관객 TOP 10",
    height=600,
    xaxis_title="기간 일관객 합계",
    yaxis_title="영화",
    showlegend=False
)


st.plotly_chart(
    fig4,
    use_container_width=True
)


st.info(
    "막대에 마우스를 올리면 해당 영화가 10위권에 든 날수도 확인할 수 있습니다."
)


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "이곳에 어떤 영화가 장기간 높은 관객을 유지했는지 한 문장으로 작성하세요."
)


# ==========================================================
# 그래프 5
# 월 × 요일별 일관객 합계 히트맵
# ==========================================================

st.divider()

st.header("5. 월 × 요일별 일관객 합계")

st.write(
    "날짜에서 월과 요일을 뽑아 어느 월·요일 조합에서 관객이 많았는지 확인합니다."
)


# 월 추출
df["월"] = df["날짜"].dt.month


# 요일 추출
weekday_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]

df["요일"] = df["날짜"].dt.dayofweek.map(
    dict(enumerate(weekday_order))
)


# 월 × 요일별 일관객 합계
heatmap_data = (
    df.groupby(
        ["월", "요일"],
        as_index=False
    )["일관객"]
    .sum()
)


# 피벗 테이블
heatmap_pivot = heatmap_data.pivot(
    index="월",
    columns="요일",
    values="일관객"
)


# 월 순서 1~12월
heatmap_pivot = heatmap_pivot.reindex(
    index=range(1, 13)
)


# 요일 순서 월~일
heatmap_pivot = heatmap_pivot.reindex(
    columns=weekday_order
)


# 히트맵
fig5 = px.imshow(
    heatmap_pivot,
    labels={
        "x": "요일",
        "y": "월",
        "color": "일관객 합계"
    },
    x=weekday_order,
    y=[f"{month}월" for month in heatmap_pivot.index],
    aspect="auto",
    text_auto=".3s",
    color_continuous_scale="Blues"
)


fig5.update_traces(
    hovertemplate=(
        "%{y} %{x}<br>"
        "일관객 합계: %{z:,.0f}명"
        "<extra></extra>"
    )
)


fig5.update_layout(
    title="월 × 요일별 일관객 합계",
    height=600,
    xaxis_title="요일",
    yaxis_title="월"
)


st.plotly_chart(
    fig5,
    use_container_width=True
)


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "이곳에 어느 월과 요일에 영화 관객이 많이 몰렸는지 한 문장으로 작성하세요."
)


# ==========================================================
# 데이터 출처
# ==========================================================

st.divider()

st.caption(
    "데이터 출처: 영화진흥위원회(KOBIS)"
)
```
