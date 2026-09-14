import streamlit as st
import random
import json
import os
from datetime import datetime

# ==========================================
# 기본 설정
# ==========================================

st.set_page_config(
    page_title="숫자 맞히기 게임",
    page_icon="🎯",
    layout="centered"
)

RANKING_FILE = "ranking.json"


# ==========================================
# 랭킹 데이터 관리
# ==========================================

def load_ranking():
    """ranking.json에서 랭킹 데이터를 불러옵니다."""
    if not os.path.exists(RANKING_FILE):
        return []

    try:
        with open(RANKING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_ranking(ranking):
    """랭킹 데이터를 ranking.json에 저장합니다."""
    with open(RANKING_FILE, "w", encoding="utf-8") as f:
        json.dump(ranking, f, ensure_ascii=False, indent=2)


def add_ranking(name, attempts):
    """게임 결과를 랭킹에 추가합니다."""
    ranking = load_ranking()

    ranking.append({
        "name": name,
        "attempts": attempts,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    # 시도 횟수가 적은 순서대로 정렬
    ranking.sort(key=lambda x: x["attempts"])

    # 상위 20명만 저장
    ranking = ranking[:20]

    save_ranking(ranking)

    return ranking


# ==========================================
# 세션 상태 초기화
# ==========================================

if "target_number" not in st.session_state:
    st.session_state.target_number = random.randint(1, 100)

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "game_over" not in st.session_state:
    st.session_state.game_over = False

if "message" not in st.session_state:
    st.session_state.message = "숫자를 입력해 보세요!"

if "player_name" not in st.session_state:
    st.session_state.player_name = ""


# ==========================================
# 새 게임
# ==========================================

def new_game():
    st.session_state.target_number = random.randint(1, 100)
    st.session_state.attempts = 0
    st.session_state.game_over = False
    st.session_state.message = "숫자를 입력해 보세요!"


# ==========================================
# 제목
# ==========================================

st.title("🎯 숫자 맞히기 게임")

st.write(
    "컴퓨터가 **1부터 100 사이의 숫자 하나를 랜덤으로 선택했습니다.**"
)
st.write("숫자를 입력해서 컴퓨터가 선택한 숫자를 맞혀보세요!")


# ==========================================
# 플레이어 이름
# ==========================================

st.subheader("👤 플레이어")

player_name = st.text_input(
    "이름을 입력하세요",
    value=st.session_state.player_name,
    max_chars=20,
    disabled=st.session_state.game_over
)

st.session_state.player_name = player_name


# ==========================================
# 게임 영역
# ==========================================

st.subheader("🎮 게임")

guess = st.number_input(
    "1~100 사이의 숫자를 입력하세요",
    min_value=1,
    max_value=100,
    value=50,
    step=1,
    disabled=st.session_state.game_over
)


if st.button(
    "🎯 숫자 맞히기",
    use_container_width=True,
    disabled=st.session_state.game_over
):

    if not player_name.strip():
        st.warning("먼저 이름을 입력해주세요.")
        st.stop()

    st.session_state.attempts += 1

    target = st.session_state.target_number

    if guess < target:

        st.session_state.message = "⬆️ 더 큰 숫자입니다!"

    elif guess > target:

        st.session_state.message = "⬇️ 더 작은 숫자입니다!"

    else:

        st.session_state.message = (
            f"🎉 정답입니다! 숫자는 **{target}**였습니다!"
        )

        st.session_state.game_over = True

        # 랭킹 저장
        ranking = add_ranking(
            player_name.strip(),
            st.session_state.attempts
        )

        st.balloons()


# ==========================================
# 게임 결과 표시
# ==========================================

st.divider()

st.subheader("💡 결과")

st.info(st.session_state.message)

st.metric(
    "현재 시도 횟수",
    f"{st.session_state.attempts}회"
)


# ==========================================
# 게임 종료
# ==========================================

if st.session_state.game_over:

    st.success(
        f"🏆 {player_name}님은 "
        f"**{st.session_state.attempts}번** 만에 성공했습니다!"
    )

    st.button(
        "🔄 새 게임 시작",
        use_container_width=True,
        on_click=new_game
    )


# ==========================================
# 랭킹
# ==========================================

st.divider()

st.subheader("🏆 명예의 전당")

ranking = load_ranking()

if not ranking:

    st.write("아직 기록이 없습니다. 첫 번째 기록의 주인공이 되어보세요! 🎯")

else:

    # 테이블용 데이터 생성
    ranking_data = []

    for index, record in enumerate(ranking, start=1):

        if index == 1:
            rank = "🥇"
        elif index == 2:
            rank = "🥈"
        elif index == 3:
            rank = "🥉"
        else:
            rank = str(index)

        ranking_data.append({
            "순위": rank,
            "플레이어": record["name"],
            "시도 횟수": f"{record['attempts']}회",
            "날짜": record["date"]
        })

    st.table(ranking_data)


# ==========================================
# 게임 규칙
# ==========================================

with st.expander("📖 게임 방법"):

    st.markdown("""
    ### 게임 방법

    1. 이름을 입력합니다.
    2. 컴퓨터가 1~100 사이의 숫자를 랜덤으로 선택합니다.
    3. 숫자를 입력합니다.
    4. 컴퓨터가 다음과 같이 알려줍니다.
       - ⬆️ **더 큰 숫자입니다**
       - ⬇️ **더 작은 숫자입니다**
       - 🎉 **정답입니다**
    5. 적은 횟수로 정답을 맞힐수록 높은 순위에 올라갑니다.

    ### 🏆 랭킹 기준

    **시도 횟수가 적을수록 높은 순위입니다.**

    현재 랭킹은 상위 20개 기록까지 저장됩니다.
    """)


# ==========================================
# 하단 안내
# ==========================================

st.divider()

st.caption("🎯 Number Guessing Game | GitHub + Streamlit")
