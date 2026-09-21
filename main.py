import streamlit as st
import requests
import pandas as pd

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ==========================================================
# 1. 기본 설정
# ==========================================================

st.set_page_config(
    page_title="KOBIS 박스오피스",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 KOBIS 일일 박스오피스")


# ==========================================================
# 2. 한국 시간 기준 날짜
# ==========================================================

kst = ZoneInfo("Asia/Seoul")

today_kst = datetime.now(kst).date()
yesterday_kst = today_kst - timedelta(days=1)


# ==========================================================
# 3. 조회 날짜 선택
# ==========================================================
# 기본값은 '어제'입니다.
# 단, 사용자가 원하는 날짜를 직접 선택할 수도 있습니다.

selected_date = st.date_input(
    "📅 조회 날짜",
    value=yesterday_kst,
    max_value=yesterday_kst
)

target_dt = selected_date.strftime("%Y%m%d")


# ==========================================================
# 4. KOBIS API 호출
# ==========================================================
# 같은 날짜의 데이터를 1시간 동안 캐시합니다.
# 따라서 같은 날짜를 다시 조회해도 API를 계속 호출하지 않습니다.

@st.cache_data(ttl=3600)
def get_boxoffice(target_dt, api_key):

    url = (
        "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
        "boxoffice/searchDailyBoxOfficeList.json"
    )

    params = {
        "key": api_key,
        "targetDt": target_dt
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return data, None

    except requests.exceptions.RequestException as e:

        return None, str(e)

    except ValueError:

        return None, "JSON 형식의 응답을 받지 못했습니다."


# ==========================================================
# 5. API 인증키 가져오기
# ==========================================================
# Streamlit Cloud의 Secrets에
#
# KOBIS_KEY = "인증키"
#
# 를 등록합니다.

try:

    api_key = st.secrets["KOBIS_KEY"]

except KeyError:

    st.error("🔑 KOBIS_KEY를 찾을 수 없습니다.")

    st.info(
        "Streamlit Cloud → Settings → Secrets에서 "
        "`KOBIS_KEY`를 등록했는지 확인하세요."
    )

    st.stop()


# ==========================================================
# 6. API 요청
# ==========================================================

data, error = get_boxoffice(
    target_dt,
    api_key
)


# API 요청 자체가 실패한 경우
if error:

    st.error("❌ 박스오피스 정보를 가져오지 못했습니다.")

    st.warning(
        "다음 사항을 확인해 주세요.\n\n"
        "• 인터넷 연결 상태\n"
        "• KOBIS API 서버 상태\n"
        "• API 주소\n"
        "• Streamlit Cloud 상태"
    )

    st.stop()


# ==========================================================
# 7. KOBIS API 오류 확인
# ==========================================================
# 인증키가 틀려도 HTTP 상태코드는 200일 수 있기 때문에
# faultInfo를 반드시 확인합니다.

if "faultInfo" in data:

    fault_info = data["faultInfo"]

    message = fault_info.get(
        "message",
        "KOBIS API에서 오류가 발생했습니다."
    )

    st.error("❌ KOBIS API 오류")

    st.warning(
        f"오류 내용: {message}\n\n"
        "KOBIS 인증키가 정확한지 확인하세요."
    )

    st.stop()


# ==========================================================
# 8. 박스오피스 데이터 확인
# ==========================================================

boxoffice_result = data.get("boxOfficeResult")

if not boxoffice_result:

    st.error("❌ 박스오피스 결과가 없습니다.")

    st.info(
        "선택한 날짜에 대한 KOBIS 데이터가 존재하는지 확인하세요."
    )

    st.stop()


movie_list = boxoffice_result.get(
    "dailyBoxOfficeList",
    []
)


if not movie_list:

    st.warning(
        "🎬 해당 날짜의 박스오피스 영화 목록이 없습니다."
    )

    st.info(
        "다음 사항을 확인해 주세요.\n\n"
        "• 조회 날짜가 올바른지\n"
        "• KOBIS에서 해당 날짜의 데이터가 집계되었는지\n"
        "• KOBIS API가 정상적으로 응답했는지"
    )

    st.stop()


# ==========================================================
# 9. 데이터 숫자 변환
# ==========================================================
# KOBIS API는 숫자를 문자열로 보내므로 int로 변환합니다.

movies = []

for movie in movie_list:

    rank = int(movie.get("rank", 0))
    rank_inten = int(movie.get("rankInten", 0))

    movies.append({

        "순위": rank,

        "증감": rank_inten,

        "영화명": movie.get(
            "movieNm",
            ""
        ),

        "개봉일": movie.get(
            "openDt",
            ""
        ),

        "관객수": int(
            movie.get("audiCnt", 0)
        ),

        "누적관객": int(
            movie.get("audiAcc", 0)
        ),

        "스크린수": int(
            movie.get("scrnCnt", 0)
        )
    })


# 순위순으로 정렬
movies.sort(
    key=lambda x: x["순위"]
)


# ==========================================================
# 10. 100만 관객 트로피 표시 함수
# ==========================================================

def trophy(movie_name, audience):

    if audience >= 1_000_000:
        return f"🏆 {movie_name}"

    return movie_name


# ==========================================================
# 11. 조회 날짜 표시
# ==========================================================

st.subheader(
    f"📅 {selected_date.strftime('%Y년 %m월 %d일')} 박스오피스"
)


# ==========================================================
# 12. 1위 영화
# ==========================================================

first_movie = movies[0]

first_movie_name = trophy(
    first_movie["영화명"],
    first_movie["누적관객"]
)

st.subheader(
    f"🥇 1위 — {first_movie_name}"
)


# ==========================================================
# 13. 1위 영화 지표 카드
# ==========================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "당일 관객수",
        f"{first_movie['관객수']:,}명"
    )


with col2:

    st.metric(
        "누적 관객수",
        f"{first_movie['누적관객']:,}명"
    )


with col3:

    st.metric(
        "스크린수",
        f"{first_movie['스크린수']:,}개"
    )


# ==========================================================
# 14. 관객수 상위 5편
# ==========================================================

st.subheader("📊 관객수 상위 5편")


top5 = sorted(
    movies,
    key=lambda x: x["관객수"],
    reverse=True
)[:5]


chart_data = pd.DataFrame({

    "영화명": [
        trophy(
            movie["영화명"],
            movie["누적관객"]
        )
        for movie in top5
    ],

    "관객수": [
        movie["관객수"]
        for movie in top5
    ]

})


chart_data = chart_data.set_index(
    "영화명"
)


st.bar_chart(
    chart_data,
    y="관객수"
)


# ==========================================================
# 15. 전체 박스오피스 표
# ==========================================================

st.subheader("🎥 전체 박스오피스")


# 표에 표시할 데이터를 별도로 만듭니다.
# 영화명 앞에 100만 관객 달성 시 🏆를 붙입니다.

table_movies = []

for movie in movies:

    table_movies.append({

        "순위": movie["순위"],

        "증감": movie["증감"],

        "영화명": trophy(
            movie["영화명"],
            movie["누적관객"]
        ),

        "개봉일": movie["개봉일"],

        "관객수": movie["관객수"],

        "누적관객": movie["누적관객"],

        "스크린수": movie["스크린수"]

    })


table_data = pd.DataFrame(
    table_movies
)


# ==========================================================
# 16. 증감 표시
# ==========================================================
# +숫자 → 전날보다 순위 상승
# -숫자 → 전날보다 순위 하락
# 0 → 순위 동일
#
# 예:
# +2 → 2계단 상승
# -1 → 1계단 하락
# 0  → 변동 없음

def format_rank_change(value):

    if value > 0:
        return f"▲ {value}"

    elif value < 0:
        return f"▼ {abs(value)}"

    else:
        return "―"


table_data["증감"] = table_data["증감"].apply(
    format_rank_change
)


# ==========================================================
# 17. 표 출력
# ==========================================================

st.dataframe(

    table_data,

    use_container_width=True,

    hide_index=True,

    column_config={

        "순위":
            st.column_config.NumberColumn(
                "순위",
                format="%d"
            ),

        "증감":
            st.column_config.TextColumn(
                "전일 대비"
            ),

        "영화명":
            st.column_config.TextColumn(
                "영화명"
            ),

        "개봉일":
            st.column_config.TextColumn(
                "개봉일"
            ),

        "관객수":
            st.column_config.NumberColumn(
                "관객수",
                format="%d명"
            ),

        "누적관객":
            st.column_config.NumberColumn(
                "누적관객",
                format="%d명"
            ),

        "스크린수":
            st.column_config.NumberColumn(
                "스크린수",
                format="%d개"
            )
    }
)


# ==========================================================
# 18. 100만 관객 안내
# ==========================================================

million_movies = [

    movie["영화명"]

    for movie in movies

    if movie["누적관객"] >= 1_000_000
]


if million_movies:

    st.success(
        "🏆 100만 관객 돌파 영화: "
        + ", ".join(million_movies)
    )


# ==========================================================
# 19. 데이터 출처
# ==========================================================

st.caption(
    "데이터 출처: 영화진흥위원회(KOBIS) "
    f"일일 박스오피스 · {target_dt}"
)
