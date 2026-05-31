import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform
import io

# 폰트 설정 (윈도우/맥/웹 호환)
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

# 폰트가 설치되어 있는지 확인하고 적용
if os.path.exists(font_path):
    font_name = fm.FontProperties(fname=font_path).get_name()
    plt.rc('font', family=font_name)
    plt.rcParams['axes.unicode_minus'] = False
else:
    # 폰트가 없으면 기본 폰트 사용 (한글은 깨지겠지만 에러는 안 남)
    pass

# ================= 상태 관리 (Session State) 초기화 ================= #
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.user_name = ""
    st.session_state.user_mbti = ""
    st.session_state.stress_cause = "없음"
    st.session_state.metrics = {'스트레스': 40, '자신감': 60, '감정 안정성': 60, '생활만족도': 60}
    st.session_state.chat_history = []  # 대화 기록 저장소

def add_msg(role, content):
    st.session_state.chat_history.append({"role": role, "content": content})

def update_metrics(stress, conf, stab, satis):
    st.session_state.metrics['스트레스'] = max(0, min(100, st.session_state.metrics['스트레스'] + stress))
    st.session_state.metrics['자신감'] = max(0, min(100, st.session_state.metrics['자신감'] + conf))
    st.session_state.metrics['감정 안정성'] = max(0, min(100, st.session_state.metrics['감정 안정성'] + stab))
    st.session_state.metrics['생활만족도'] = max(0, min(100, st.session_state.metrics['생활만족도'] + satis))

# ================= 화면 UI 구성 ================= #
st.set_page_config(page_title="MBTI 심층 상담 챗봇", page_icon="🤖", layout="centered")

# [Step 0] 로그인(정보 입력) 화면
if st.session_state.step == 0:
    st.title("🧠 MBTI 기반 심리상담 챗봇")
    st.markdown("당신의 성향을 분석하여 맞춤형 심리 처방전을 발급해 드립니다.")
    
    with st.form("login_form"):
        name = st.text_input("이름을 입력하세요:")
        mbti = st.text_input("MBTI를 입력하세요 (예: INFP):").upper()
        submit = st.form_submit_button("심층 상담 시작하기 🚀")
        
        if submit:
            valid_list = ['ISTJ', 'ISFJ', 'INFJ', 'INTJ', 'ISTP', 'ISFP', 'INFP', 'INTP', 
                          'ESTP', 'ESFP', 'ENFP', 'ENTP', 'ESTJ', 'ESFJ', 'ENFJ', 'ENTJ']
            if not name:
                st.warning("이름을 입력해주세요.")
            elif mbti not in valid_list:
                st.warning("올바른 16가지 MBTI 중 하나를 입력해주세요. (예: ENFP)")
            else:
                st.session_state.user_name = name
                st.session_state.user_mbti = mbti
                st.session_state.step = 1
                add_msg("assistant", f"안녕하세요 {name}님!\n오늘 하루 전반적인 에너지 상태는 어떠신가요?")
                st.rerun()

# [Step 1~6] 채팅 및 선택형 인터페이스
else:
    st.title(f"💬 {st.session_state.user_name}님의 상담방")
    
    # 1. 지금까지의 대화 기록 화면에 출력
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 2. 버튼 클릭 시 다음 단계로 넘어가는 공통 함수
    def handle_choice(user_text, next_step, cause=None, stress=0, conf=0, stab=0, satis=0, bot_reply=""):
        add_msg("user", user_text)
        update_metrics(stress, conf, stab, satis)
        if cause:
            st.session_state.stress_cause = cause
        if bot_reply:
            add_msg("assistant", bot_reply)
        st.session_state.step = next_step
        st.rerun()

    # 3. 단계별 선택지 (동적 버튼 생성)
    if st.session_state.step == 1:
        st.write("---")
        if st.button("1. 에너지가 넘치고 기분이 아주 좋습니다."):
            reply = "[진단 2/6] 안정적인 편이시군요. 오늘 당신을 가장 편안하거나 즐겁게 만든 요인은 무엇인가요?"
            handle_choice("1. 에너지가 넘치고 기분이 아주 좋습니다.", 2, None, -15, 10, 10, 15, reply)
        if st.button("2. 특별한 일 없이 평범하고 무난하게 보냈습니다."):
            reply = "[진단 2/6] 무난한 하루였군요. 오늘 당신을 편안하게 만든 요인은 무엇인가요?"
            handle_choice("2. 특별한 일 없이 평범하고 무난하게 보냈습니다.", 2, None, 0, 0, 5, 5, reply)
        if st.button("3. 에너지가 소진되어 살짝 피곤하고 지칩니다."):
            reply = "[진단 2/6] 많이 지치셨군요. 오늘 당신의 에너지를 갉아먹은 주된 원인은 무엇인가요?"
            handle_choice("3. 에너지가 소진되어 살짝 피곤하고 지칩니다.", 3, None, 15, -5, -5, -10, reply)
        if st.button("4. 완전히 방전되었고 극심한 스트레스를 받습니다."):
            reply = "[진단 2/6] 세상에, 많이 힘드셨겠어요. 에너지를 가장 많이 갉아먹은 원인은 무엇인가요?"
            handle_choice("4. 완전히 방전되었고 극심한 스트레스를 받습니다.", 3, None, 30, -10, -15, -20, reply)

    elif st.session_state.step == 2: # 긍정적일 때의 원인
        st.write("---")
        def step2_good(txt, cause, stress, conf, stab, satis):
            reply = f"[진단 3/6] [{cause}] 요인이 컸군요.\n이런 긍정적인 상황일 때, 당신은 마음속으로 어떻게 생각하시나요?"
            handle_choice(txt, 4, cause, stress, conf, stab, satis, reply)
            
        if st.button("1. 소중한 사람들과 함께 즐거운 시간을 보냈습니다."): step2_good("1. 즐거운 대인관계", "좋은 인간관계", -10, 5, 10, 10)
        if st.button("2. 맡은 일이나 과제를 성공적으로 끝내서 뿌듯합니다."): step2_good("2. 성과 및 성취", "성취감", -10, 15, 5, 10)
        if st.button("3. 맛있는 음식을 먹고 집에서 푹 쉬면서 힐링했습니다."): step2_good("3. 맛있는 음식과 휴식", "충분한 휴식", -15, 0, 10, 5)
        if st.button("4. 평소 좋아하는 취미 생활에 푹 빠져 있었습니다."): step2_good("4. 즐거운 취미생활", "취미 생활", -10, 5, 5, 10)

    elif st.session_state.step == 3: # 부정적일 때의 원인
        st.write("---")
        def step3_bad(txt, cause, stress, conf, stab, satis):
            reply = f"[진단 3/6] [{cause}] 요인이 컸군요.\n이런 스트레스 상황이 발생했을 때, 당신은 어떻게 받아들이는 편인가요?"
            handle_choice(txt, 4, cause, stress, conf, stab, satis, reply)
            
        if st.button("1. 사람들 사이에서의 갈등이나 눈치 보는 상황 때문입니다."): step3_bad("1. 인간관계 갈등", "인간관계 갈등", 20, -5, -15, -10)
        if st.button("2. 과도한 업무량이나 학업 성적에 대한 압박감 때문입니다."): step3_bad("2. 업무/학업 압박", "과도한 업무/학업", 20, -10, -5, -10)
        if st.button("3. 해결되지 않는 미래에 대한 막막함과 불안감 때문입니다."): step3_bad("3. 미래에 대한 불안", "미래 불안감", 25, -15, -15, -15)
        if st.button("4. 수면 부족 등 체력적으로 너무 피곤하고 지쳐서 그렇습니다."): step3_bad("4. 체력 및 수면 부족", "수면 및 체력부족", 15, -5, -10, -5)

    elif st.session_state.step == 4:
        st.write("---")
        def step4(txt, stress, conf, stab, satis):
            reply = "[진단 4/6] 그렇군요.\n그렇다면 특정한 감정(스트레스 등)이 찾아왔을 때, 보통 그 감정은 얼마나 지속되나요?"
            handle_choice(txt, 5, None, stress, conf, stab, satis, reply)
            
        if st.button("1. '내가 부족해서 생긴 일이야'라며 스스로를 자책합니다."): step4("1. 주로 내 탓으로 돌림", 10, -20, -15, -5)
        if st.button("2. '상황이나 타인 때문에 어쩔 수 없었어'라고 외부로 돌립니다."): step4("2. 외부나 상황 탓으로 돌림", -5, 0, 10, 0)
        if st.button("3. '이 상황에서 내가 배울 점이나 고칠 점은 뭘까' 고민합니다."): step4("3. 해결책과 교훈을 찾음", 5, 15, 10, 5)
        if st.button("4. 깊게 생각하지 않고 '이 또한 지나가리라'하며 넘깁니다."): step4("4. 깊게 담아두지 않음", -10, 5, 15, 5)

    elif st.session_state.step == 5:
        st.write("---")
        def step5(txt, stress, conf, stab, satis):
            reply = "[진단 5/6] 감정의 회복 탄력성을 확인했습니다.\n이런 복잡한 감정들을 해소하기 위해 당신이 주로 취하는 행동은 무엇인가요?"
            handle_choice(txt, 6, None, stress, conf, stab, satis, reply)
            
        if st.button("1. 자고 일어나면 금방 훌훌 털어버리는 편입니다."): step5("1. 금방 털어버림", -15, 5, 20, 10)
        if st.button("2. 하루 이틀 정도는 마음 한구석에 잔상이 남습니다."): step5("2. 며칠 잔상이 남음", 5, 0, 0, 0)
        if st.button("3. 혼자 있을 때 계속 떠올라 며칠 동안 괴롭고 힘듭니다."): step5("3. 오래 지속되고 괴로움", 15, -10, -15, -10)
        if st.button("4. 누군가에게 위로를 받기 전까지는 계속 이어집니다."): step5("4. 타인의 위로가 필요함", 5, -5, -10, 0)

    elif st.session_state.step == 6: # E/I, T/F 분기
        st.write("---")
        def step6(txt, stress, conf, stab, satis):
            reply = "[마지막 진단] 당신만의 훌륭한 대처 방식이군요.\n오늘을 마무리하고 내일을 맞이하기 위해, 지금 당장 하고 싶은 행동은 무엇인가요?"
            handle_choice(txt, 7, None, stress, conf, stab, satis, reply)
            
        is_e = 'E' in st.session_state.user_mbti
        is_t = 'T' in st.session_state.user_mbti

        if is_e:
            if st.button("1. 친구나 지인을 만나 신나게 수다를 떨며 해소합니다."): step6("1. 지인과 수다", -10, 5, 5, 5)
            if st.button("2. 사람이 많은 곳이나 활기찬 모임에 나가 에너지를 얻습니다."): step6("2. 활기찬 모임 참석", -10, 5, 0, 5)
        else:
            if st.button("1. 누구와도 연락하지 않고 온전히 혼자만의 동굴에 들어갑니다."): step6("1. 혼자만의 동굴", -10, 0, 10, 5)
            if st.button("2. 조용히 집에서 좋아하는 영화를 보거나 음악을 들으며 쉽니다."): step6("2. 집에서 조용한 휴식", -10, 0, 10, 5)
            
        if is_t:
            if st.button("3. 이 감정의 근본적인 원인이 무엇인지 객관적으로 분석합니다."): step6("3. 객관적 원인 분석", 5, 10, 5, 0)
            if st.button("4. 지금 당장 내가 해결할 수 있는 대안을 찾아 실행합니다."): step6("4. 즉각적인 대안 실행", -5, 15, 10, 5)
        else:
            if st.button("3. 내 감정을 솔직하게 적으며 스스로를 따뜻하게 다독여줍니다."): step6("3. 일기 작성 및 다독임", -10, 0, 15, 5)
            if st.button("4. 내 마음을 가장 잘 알아주는 사람에게 털어놓고 공감 받습니다."): step6("4. 타인의 공감과 위로", -15, 5, 10, 5)

    elif st.session_state.step == 7: # J/P 분기 및 처방 완료 트리거
        st.write("---")
        def step7(txt):
            reply = "수고하셨습니다. 모든 심층 분석이 완료되었습니다. 아래에서 결과를 확인하세요!"
            handle_choice(txt, 8, None, 0, 5, 5, 10, reply)
            
        if 'J' in st.session_state.user_mbti:
            if st.button("1. 내일 해야 할 일 리스트(To-do)를 미리 작성해둡니다."): step7("1. To-do 리스트 작성")
            if st.button("2. 방 청소나 주변 정리를 하면서 주변 상황을 통제합니다."): step7("2. 주변 정리 및 청소")
            if st.button("3. 평소 매일 지키던 나만의 저녁 루틴(독서 등)을 수행합니다."): step7("3. 저녁 루틴 수행")
            if st.button("4. 내일 챙길 물건들을 가방에 미리 준비해둡니다."): step7("4. 내일 짐 챙기기")
        else:
            if st.button("1. 내일 일은 내일 생각하고, 당장 가장 끌리는 것을 합니다."): step7("1. 당장 끌리는 일 하기")
            if st.button("2. 계획 없이 유튜브나 넷플릭스 알고리즘에 몸을 맡깁니다."): step7("2. 알고리즘에 몸 맡기기")
            if st.button("3. 영감이 떠오르는 새로운 취미나 관심사를 찾아봅니다."): step7("3. 새로운 관심사 탐색")
            if st.button("4. 알람만 대충 맞춰두고 아무 생각 없이 푹 자면서 충전합니다."): step7("4. 푹 자면서 충전")

    elif st.session_state.step == 8: # 최종 처방전 및 그래프 화면
        st.success("🎉 분석이 완료되었습니다!")
        st.subheader("📊 4대 심리 지표 결과")
        
        # [폰트 경로 설정]
        font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
        font_prop = fm.FontProperties(fname=font_path)
        
        # 웹상에 그래프 그리기
        fig, ax = plt.subplots(figsize=(7, 4.5))
        categories = list(st.session_state.metrics.keys())
        scores = list(st.session_state.metrics.values())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        
        bars = ax.bar(categories, scores, color=colors, width=0.5)
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval}점', ha='center', va='bottom', fontweight='bold')

        ax.set_title(f"{st.session_state.user_name}({st.session_state.user_mbti})님의 심리 지표", pad=15)
        ax.set_ylabel("점수 (100점 만점)")
        ax.set_ylim(0, 110)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        
        st.pyplot(fig) # 웹 화면에 그래프 출력
        
        # 처방전 텍스트 생성
        txt_content = (
            f"==== {st.session_state.user_name}님을 위한 다차원 심층 심리 처방전 ====\n"
            f"▶ 성향(MBTI): {st.session_state.user_mbti}\n"
            f"▶ 핵심 분석 요인: [{st.session_state.stress_cause}]\n\n"
            f"[4대 심리 지표 결과]\n"
            f"- 스트레스: {scores[0]}점 | 자신감: {scores[1]}점 | 감정 안정성: {scores[2]}점 | 생활만족도: {scores[3]}점\n\n"
            "[전문가의 다차원 맞춤 처방]\n"
        )
        if scores[0] >= 60 or scores[2] <= 40:
            txt_content += f"현재 [{st.session_state.stress_cause}] 이슈로 다소 지쳐있습니다. {st.session_state.user_mbti} 성향의 책임감을 잠시 내려놓고 온전히 '나'를 위한 휴식을 취하세요."
        else:
            txt_content += f"4대 지표가 훌륭하게 균형을 이루고 있습니다. {st.session_state.user_mbti} 성향 특유의 장점을 살려 내일도 긍정적인 하루를 만들어가세요."
            
        st.info(txt_content)

        # 다운로드 버튼 (웹 앱의 하이라이트)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(label="📝 처방전 텍스트 다운로드", data=txt_content, file_name=f"처방전_{st.session_state.user_name}.txt", mime="text/plain")
        with col2:
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
            st.download_button(label="📉 그래프 이미지 다운로드", data=buf.getvalue(), file_name=f"그래프_{st.session_state.user_name}.png", mime="image/png")
        
        if st.button("🔄 처음부터 다시 하기"):
            st.session_state.clear()
            st.rerun()