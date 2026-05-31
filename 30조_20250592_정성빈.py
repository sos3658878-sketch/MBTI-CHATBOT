"""
====================================================================
프로젝트명 : MBTI 기반 심리상담 챗봇 (Streamlit Web App)
제출자     : 30조 20250592 정성빈
====================================================================
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform
import io
from datetime import datetime

# ================= 1. 초기 환경 및 폰트 설정 ================= #
st.set_page_config(page_title="MBTI 기반 심리상담 챗봇", page_icon="🤖", layout="centered")

# OS별 한글 폰트 동적 할당 (Windows, Mac, Linux/Streamlit Cloud 대응)
if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
elif platform.system() == 'Darwin': 
    plt.rcParams['font.family'] = 'AppleGothic'
else: 
    plt.rcParams['font.family'] = 'NanumGothic'

plt.rcParams['axes.unicode_minus'] = False

# ================= 2. 상태 관리 (Session State) 초기화 ================= #
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.user_name = ""
    st.session_state.user_mbti = ""
    st.session_state.stress_cause = "없음"
    st.session_state.metrics = {'스트레스': 40, '자신감': 60, '감정 안정성': 60, '생활만족도': 60}
    st.session_state.chat_history = [] 

def add_msg(role, content):
    """대화 기록을 세션 상태에 저장하는 헬퍼 함수"""
    st.session_state.chat_history.append({"role": role, "content": content})

def update_metrics(stress, conf, stab, satis):
    """4대 심리 지표 점수를 업데이트하고 0~100 사이로 유지하는 헬퍼 함수"""
    st.session_state.metrics['스트레스'] = max(0, min(100, st.session_state.metrics['스트레스'] + stress))
    st.session_state.metrics['자신감'] = max(0, min(100, st.session_state.metrics['자신감'] + conf))
    st.session_state.metrics['감정 안정성'] = max(0, min(100, st.session_state.metrics['감정 안정성'] + stab))
    st.session_state.metrics['생활만족도'] = max(0, min(100, st.session_state.metrics['생활만족도'] + satis))

# ================= 3. 메인 UI 및 시나리오 로직 ================= #

# [Step 0] 초기 로그인 및 정보 입력 화면
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

# [Step 1~10] 대화형 상담 인터페이스
else:
    st.title(f"💬 {st.session_state.user_name}님의 상담방")
    
    # 누적된 대화 기록 출력
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    def handle_choice(user_text, next_step, cause=None, stress=0, conf=0, stab=0, satis=0, bot_reply=""):
        """사용자의 선택을 처리하고 다음 단계로 라우팅하는 통합 제어 함수"""
        add_msg("user", user_text)
        update_metrics(stress, conf, stab, satis)
        if cause:
            st.session_state.stress_cause = cause
        if bot_reply:
            add_msg("assistant", bot_reply)
        st.session_state.step = next_step
        st.rerun()

    # ----------------------------------------------------------------------
    # 단계별 분기 처리 로직 (10단계 심층 분석)
    # ----------------------------------------------------------------------
    if st.session_state.step == 1:
        st.write("---")
        if st.button("1. 에너지가 넘치고 기분이 아주 좋습니다."):
            reply = "[진단 2/10] 안정적인 편이시군요. 오늘 당신을 가장 편안하거나 즐겁게 만든 요인은 무엇인가요?"
            handle_choice("1. 에너지가 넘치고 기분이 아주 좋습니다.", 2, None, -15, 10, 10, 15, reply)
        if st.button("2. 특별한 일 없이 평범하고 무난하게 보냈습니다."):
            reply = "[진단 2/10] 무난한 하루였군요. 오늘 당신을 편안하게 만든 요인은 무엇인가요?"
            handle_choice("2. 특별한 일 없이 평범하고 무난하게 보냈습니다.", 2, None, 0, 0, 5, 5, reply)
        if st.button("3. 에너지가 소진되어 살짝 피곤하고 지칩니다."):
            reply = "[진단 2/10] 많이 지치셨군요. 오늘 당신의 에너지를 갉아먹은 주된 원인은 무엇인가요?"
            handle_choice("3. 에너지가 소진되어 살짝 피곤하고 지칩니다.", 3, None, 15, -5, -5, -10, reply)
        if st.button("4. 완전히 방전되었고 극심한 스트레스를 받습니다."):
            reply = "[진단 2/10] 세상에, 많이 힘드셨겠어요. 에너지를 가장 많이 갉아먹은 원인은 무엇인가요?"
            handle_choice("4. 완전히 방전되었고 극심한 스트레스를 받습니다.", 3, None, 30, -10, -15, -20, reply)

    elif st.session_state.step == 2:
        # S(현실주의) vs N(이상주의) 분기
        st.write("---")
        def step2_choice(txt, cause, stress, conf, stab, satis):
            handle_choice(txt, 3, cause, stress, conf, stab, satis, f"[진단 3/10] '{cause}' 요인이 컸군요. 그렇다면...")
            
        if 'S' in st.session_state.user_mbti: 
            st.markdown("💬 **[질문 2] 최근 당신의 일상 속에서 구체적으로 해결해야 할 현실적인 문제 때문에 스트레스를 받으셨나요?**")
            if st.button("1. 예상치 못한 지출이나 팍팍한 재정적 문제 때문입니다."): step2_choice("재정 및 현실 문제", "현실적 압박", 20, -10, -10, -15)
            if st.button("2. 끝이 없는 집안일이나 반복되는 업무에 지쳤습니다."): step2_choice("반복되는 업무/집안일", "일상의 피로", 15, -5, -5, -10)
            if st.button("3. 건강이 안 좋아지거나 체력적인 한계를 느꼈습니다."): step2_choice("건강/체력 저하", "체력 방전", 25, -15, -15, -10)
            if st.button("4. 꼼꼼하게 챙겨야 할 서류나 디테일이 너무 많아 머리가 아픕니다."): step2_choice("과도한 디테일 업무", "과업 스트레스", 15, 0, -10, -5)
        else: 
            st.markdown("💬 **[질문 2] 최근 당신의 가치관이나 미래에 대한 고민, 삶의 의미에 대해 깊이 생각하게 만든 순간이 있었나요?**")
            if st.button("1. 내 미래가 불투명하게 느껴지고 방향성을 잃은 것 같습니다."): step2_choice("미래에 대한 막막함", "미래 불안감", 25, -15, -15, -10)
            if st.button("2. 지금 내가 매일 하고 있는 일의 의미나 가치를 찾지 못하겠습니다."): step2_choice("삶의 의미 상실", "가치관 혼란", 20, -10, -20, -15)
            if st.button("3. 타인이나 조직의 가치관이 나와 너무 강하게 충돌했습니다."): step2_choice("가치관의 충돌", "신념의 갈등", 20, 5, -15, -10)
            if st.button("4. 새로운 영감이나 아이디어가 떠오르지 않아 정체된 기분입니다."): step2_choice("영감의 고갈", "성장 정체", 15, -10, -5, -5)

    elif st.session_state.step == 3:
        # T(사고) vs F(감정) 분기
        st.write("---")
        def step3_choice(txt, stress, conf, stab, satis):
            handle_choice(txt, 4, None, stress, conf, stab, satis, "[진단 4/10] 상황을 해석하는 당신만의 방식이 확인되었습니다. 그렇다면 조금 더 내면으로 들어가 볼까요?")
            
        if 'T' in st.session_state.user_mbti: 
            st.markdown("💬 **[질문 3] 상황이 계획대로 흘러가지 않거나 비효율적일 때, 당신을 가장 답답하게 만드는 것은 무엇인가요?**")
            if st.button("1. 논리는 없고 감정적으로만 호소하며 억지를 부리는 사람을 볼 때"): step3_choice("비논리적인 사람과의 대화", 20, 10, -15, -5)
            if st.button("2. 명확한 해결책이나 결론 없이 의미 없는 회의나 대화가 길어질 때"): step3_choice("비효율적인 상황", 15, 5, -10, -10)
            if st.button("3. 합의된 원칙과 규칙이 누군가에 의해 무시되는 환경에 처할 때"): step3_choice("원칙이 무너진 환경", 20, 0, -20, -10)
            if st.button("4. 내 능력을 제대로 발휘할 수 없는 비합리적인 구조 안에 있을 때"): step3_choice("불합리한 시스템", 25, -10, -10, -15)
        else: 
            st.markdown("💬 **[질문 3] 사람들과의 관계 속에서 당신의 마음을 가장 무겁게 하거나 상처받게 하는 상황은 언제인가요?**")
            if st.button("1. 나의 진심 어린 배려나 호의가 오해받거나 무시당했다고 느낄 때"): step3_choice("진심이 무시당함", 25, -15, -20, -10)
            if st.button("2. 주변 사람들 사이에 갈등이나 불화가 생겨 분위기가 불편할 때"): step3_choice("주변의 갈등 상황", 20, -5, -15, -5)
            if st.button("3. 누군가 나에게 차갑고 사무적으로만 대할 때 소외감을 느낍니다."): step3_choice("차가운 태도와 소외감", 15, -10, -10, -10)
            if st.button("4. 내 의도와 달리 내가 누군가에게 상처를 주었다는 죄책감이 들 때"): step3_choice("타인에게 상처를 줬다는 자책", 25, -20, -25, -10)

    elif st.session_state.step == 4:
        # 4대 기질별(NF, NT, SJ, SP) 초개인화 심층 진단
        st.write("---")
        def step4_choice(txt, stress, conf, stab, satis):
            handle_choice(txt, 5, None, stress, conf, stab, satis, "[진단 5/10] 당신의 깊은 내면을 이해했습니다. 이런 복잡한 감정들을 해소하기 위해...")
            
        mbti = st.session_state.user_mbti
        
        if 'N' in mbti and 'F' in mbti: 
            st.markdown("💬 **[질문 4] 진정성과 의미를 중요하게 생각하는 당신, 최근 내면을 가장 지치게 했던 감정은 무엇인가요?**")
            if st.button("1. 현실의 벽에 부딪혀 내가 꿈꾸던 이상이 꺾이는 느낌"): step4_choice("이상이 꺾인 좌절감", 20, -15, -15, -15)
            if st.button("2. 진짜 내 모습을 숨기고 세상이 원하는 가면을 써야 하는 답답함"): step4_choice("자아 억눌림", 15, -10, -20, -10)
            if st.button("3. 아무도 내 깊고 복잡한 감정을 온전히 이해해주지 못한다는 고립감"): step4_choice("내면적 고립감", 25, -5, -25, -10)
            if st.button("4. 타인의 기대에 부응하고 챙기느라 정작 '나'를 잃어버린 느낌"): step4_choice("타인 중심의 피로", 20, -15, -15, -20)
            
        elif 'N' in mbti and 'T' in mbti:
            st.markdown("💬 **[질문 4] 논리와 지적 성장을 중시하는 당신, 최근 머릿속을 가장 복잡하게 만든 요인은 무엇인가요?**")
            if st.button("1. 지적으로 아무런 자극이 없는 지루하고 반복적인 환경"): step4_choice("지적 자극 결핍", 15, -5, -10, -20)
            if st.button("2. 무능력한 리더나 비합리적인 의사결정으로 돌아가는 시스템"): step4_choice("비합리성에 대한 분노", 25, 10, -20, -10)
            if st.button("3. 내 완벽한 계획과 통제를 완전히 벗어난 예상치 못한 변수"): step4_choice("통제력 상실", 20, -10, -15, -5)
            if st.button("4. 명확한 결론이 나지 않고 모순만 가득한 복잡한 딜레마 상황"): step4_choice("해결되지 않는 딜레마", 20, -5, -15, -10)
            
        elif 'S' in mbti and 'J' in mbti:
            st.markdown("💬 **[질문 4] 책임감이 강하고 안정을 추구하는 당신, 최근 어깨를 가장 무겁게 짓누른 짐은 무엇인가요?**")
            if st.button("1. 나 혼자서만 이 모든 상황을 책임지고 감당해야 한다는 압박감"): step4_choice("과도한 책임감", 25, -15, -20, -15)
            if st.button("2. 예측할 수 없는 갑작스러운 변화로 인해 깨져버린 일상의 평화"): step4_choice("일상의 붕괴", 20, -10, -25, -10)
            if st.button("3. 누군가 자신이 마땅히 해야 할 기본 도리나 역할을 다하지 않을 때"): step4_choice("타인의 무책임함", 20, 5, -15, -10)
            if st.button("4. 남들을 챙기고 배려하느라 정작 내 시간과 건강은 돌보지 못한 피로감"): step4_choice("자기 희생적 피로", 15, -10, -10, -20)
            
        else: 
            st.markdown("💬 **[질문 4] 현재의 즐거움과 자유를 사랑하는 당신, 최근 에너지를 가장 답답하게 묶어둔 것은 무엇인가요?**")
            if st.button("1. 납득할 수 없는 융통성 없는 규율과 틀에 억지로 맞춰야 할 때"): step4_choice("규율에 대한 답답함", 20, 5, -15, -15)
            if st.button("2. 새로운 자극이나 이벤트 없이 쳇바퀴처럼 굴러가는 지루한 일상"): step4_choice("자극 없는 지루함", 15, -5, -10, -20)
            if st.button("3. 내 행동, 시간, 선택을 지나치게 통제하고 간섭하려는 사람들"): step4_choice("간섭과 통제", 25, 0, -20, -10)
            if st.button("4. 몸을 움직이거나 새로운 것을 경험할 수 없는 꽉 막힌 환경"): step4_choice("행동의 제약", 15, -10, -15, -15)

    elif st.session_state.step == 5:
        # E(외향) vs I(내향) 분기 : 스트레스 행동 발현
        st.write("---")
        def step5_choice(txt, stress, conf, stab, satis):
            handle_choice(txt, 6, None, stress, conf, stab, satis, "[진단 6/10] 마음의 상태가 행동으로도 나타나고 있군요. 이런 상황에서 당신의 머릿속을 맴도는 생각은 무엇인가요?")
            
        if 'E' in st.session_state.user_mbti:
            st.markdown("💬 **[질문 5] 스트레스가 극에 달했을 때, 당신의 겉모습이나 행동은 어떻게 변하나요?**")
            if st.button("1. 평소보다 말이 많아지거나 목소리가 커지고 예민해집니다."): step5_choice("예민함과 다변", 15, 0, -15, -5)
            if st.button("2. 충동적으로 돈을 쓰거나 맵고 단 음식을 폭식합니다."): step5_choice("충동적 소비/폭식", 20, -5, -20, -10)
            if st.button("3. 가만히 있지 못하고 끊임없이 약속을 잡아 사람들을 만납니다."): step5_choice("강박적 관계 추구", 10, -5, -10, -5)
            if st.button("4. 주변 사람들에게 짜증을 내거나 불만을 털어놓게 됩니다."): step5_choice("짜증과 불만 표출", 20, -10, -15, -10)
        else:
            st.markdown("💬 **[질문 5] 스트레스가 극에 달했을 때, 당신의 겉모습이나 행동은 어떻게 변하나요?**")
            if st.button("1. 식욕이 뚝 떨어지고 온몸에 기운이 빠져 무기력해집니다."): step5_choice("식욕 저하 및 무기력", 20, -10, -20, -10)
            if st.button("2. 모든 연락을 차단하고 누구와도 말하고 싶지 않아집니다."): step5_choice("연락 두절 및 고립", 15, -5, -15, -5)
            if st.button("3. 생각만 꼬리를 물고 이어질 뿐, 하루 종일 잠만 자고 싶습니다."): step5_choice("과수면과 생각 과잉", 20, -10, -15, -10)
            if st.button("4. 겉으로는 평온해 보이지만 표정이 굳고 말이 극단적으로 없어집니다."): step5_choice("감정 억압 및 침묵", 15, -5, -20, -5)

    elif st.session_state.step == 6:
        # 인지적 오류 분석 분기
        st.write("---")
        def step6_choice(txt, stress, conf, stab, satis):
            handle_choice(txt, 7, None, stress, conf, stab, satis, "[진단 7/10] 스스로에게 조금 가혹하신 편이군요. 지금 당신에게 가장 필요한 것은 무엇일까요?")
            
        if 'T' in st.session_state.user_mbti:
            st.markdown("💬 **[질문 6] 상황이 힘들 때, 당신이 무의식적으로 스스로를 괴롭히는 생각은 무엇인가요?**")
            if st.button("1. '내 능력이 부족해서 이런 일도 해결 못하는구나'라는 자책"): step6_choice("능력에 대한 자책", 15, -20, -10, -10)
            if st.button("2. '처음부터 플랜 B를 완벽하게 세웠어야 했어'라는 후회"): step6_choice("완벽주의적 후회", 10, -10, -15, -5)
            if st.button("3. '왜 세상 사람들은 이렇게 비합리적이고 비효율적일까?'라는 냉소"): step6_choice("타인에 대한 냉소", 15, 5, -20, -10)
            if st.button("4. '이 감정에 휘둘려서 이성적으로 판단하지 못하는 내가 싫다'"): step6_choice("감정 동요에 대한 혐오", 20, -15, -15, -10)
        else:
            st.markdown("💬 **[질문 6] 상황이 힘들 때, 당신이 무의식적으로 스스로를 괴롭히는 생각은 무엇인가요?**")
            if st.button("1. '나 때문에 다른 사람들이 피해를 보거나 실망하면 어쩌지?'"): step6_choice("타인에 대한 죄책감", 20, -15, -15, -10)
            if st.button("2. '결국 아무도 내 진짜 마음이나 상처를 알아주지 않을 거야'"): step6_choice("깊은 고립감과 소외감", 25, -10, -25, -15)
            if st.button("3. '내가 더 참아내고 희생하면 언젠가는 모든 게 괜찮아지겠지'"): step6_choice("자기 희생적 합리화", 15, -5, -10, -20)
            if st.button("4. '나는 결국 사랑받지 못하거나 버려질지도 모른다'는 불안감"): step6_choice("애정 결핍적 불안", 25, -20, -25, -15)

    elif st.session_state.step == 7:
        # 이상적 지지 형태 확인 (공통)
        st.write("---")
        def step7_choice(txt, stress, conf, stab, satis):
            handle_choice(txt, 8, None, stress, conf, stab, satis, "[진단 8/10] 당신이 진정으로 원하는 위로를 알겠습니다. 그렇다면 이런 특정한 감정이 찾아왔을 때...")
            
        st.markdown("💬 **[질문 7] 지금 당장, 당신의 마음을 가장 편안하게 만들어 줄 수 있는 위로는 무엇인가요?**")
        if st.button("1. '다 괜찮다, 네 잘못이 아니다'라고 말해주는 따뜻한 포옹과 공감"): step7_choice("따뜻한 공감과 포옹", -15, 10, 20, 10)
        if st.button("2. 지금의 꼬인 상황을 풀어낼 수 있는 명확하고 현실적인 해결책 제시"): step7_choice("명확한 해결책", -10, 15, 10, 10)
        if st.button("3. 굳이 내게 뭘 묻지 않고, 맛있는 것을 먹으며 곁에 묵묵히 있어주는 것"): step7_choice("조용한 동행", -15, 5, 15, 15)
        if st.button("4. 그 누구의 간섭이나 연락도 받지 않는, 완벽하고 절대적인 혼자만의 시간"): step7_choice("완벽한 고립과 휴식", -10, 5, 15, 10)

    elif st.session_state.step == 8:
        # 감정 회복 탄력성 평가 (공통)
        st.write("---")
        def step8_choice(txt, stress, conf, stab, satis):
            handle_choice(txt, 9, None, stress, conf, stab, satis, "[진단 9/10] 감정의 지속성을 확인했습니다. 이제 이 엉킨 마음을 직접 풀어볼 시간입니다.")
            
        st.markdown("💬 **[질문 8] 보통 스트레스나 우울감이 한 번 찾아오면, 그 감정은 얼마나 지속되나요?**")
        if st.button("1. 자고 일어나거나 밥을 먹고 나면 금방 훌훌 털어버리는 편입니다."): step8_choice("금방 털어버림", -15, 5, 20, 10)
        if st.button("2. 하루 이틀 정도는 마음 한구석에 무거운 잔상이 남습니다."): step8_choice("며칠 잔상이 남음", 5, 0, 0, 0)
        if st.button("3. 혼자 있을 때 계속 그 상황이 떠올라 며칠 동안 괴롭고 힘듭니다."): step8_choice("오래 지속되고 괴로움", 15, -10, -15, -10)
        if st.button("4. 누군가에게 위로를 받거나 상황이 완전히 해결되기 전까진 이어집니다."): step8_choice("타인/상황 의존적", 5, -5, -10, 0)

    elif st.session_state.step == 9:
        # 감정 주도적 해소 방식 분석
        st.write("---")
        def step9_choice(txt, stress, conf, stab, satis):
            handle_choice(txt, 10, None, stress, conf, stab, satis, "[마지막 진단 10/10] 훌륭한 대처 방식이군요. 드디어 마지막 질문입니다.")
            
        st.markdown("💬 **[질문 9] 이 복잡한 감정들을 스스로 해소하기 위해 당신이 '주로 직접 취하는 행동'은 무엇인가요?**")
        is_e, is_t = 'E' in st.session_state.user_mbti, 'T' in st.session_state.user_mbti

        if is_e:
            if st.button("1. 친구나 지인을 만나 신나게 수다를 떨며 스트레스를 날려버립니다."): step9_choice("지인과 수다", -10, 5, 5, 5)
            if st.button("2. 사람이 많은 곳이나 활기찬 모임, 활동적인 스포츠를 즐깁니다."): step9_choice("활동적 모임/스포츠", -10, 5, 0, 5)
        else:
            if st.button("1. 누구와도 연락하지 않고 온전히 혼자만의 동굴에 깊숙이 들어갑니다."): step9_choice("혼자만의 동굴", -10, 0, 10, 5)
            if st.button("2. 조용히 집에서 좋아하는 영화나 음악을 감상하며 에너지를 채웁니다."): step9_choice("집에서 조용한 휴식", -10, 0, 10, 5)
            
        if is_t:
            if st.button("3. 이 감정의 근본적인 원인이 무엇인지 객관적으로 분석하고 정리합니다."): step9_choice("객관적 원인 분석", 5, 10, 5, 0)
            if st.button("4. 감정에 빠져있기보다, 지금 당장 내가 실행할 수 있는 대안을 찾습니다."): step9_choice("즉각적인 대안 실행", -5, 15, 10, 5)
        else:
            if st.button("3. 내 감정을 일기에 솔직하게 적어 내려가며 스스로를 따뜻하게 다독입니다."): step9_choice("일기 작성 및 다독임", -10, 0, 15, 5)
            if st.button("4. 내 마음을 가장 잘 알아주는 사람에게 모든 것을 털어놓고 공감 받습니다."): step9_choice("타인의 공감과 위로", -15, 5, 10, 5)

    elif st.session_state.step == 10: 
        # J(판단) vs P(인식) 분기 : 내일을 위한 준비 방식
        st.write("---")
        def step10_choice(txt):
            handle_choice(txt, 11, None, 0, 5, 5, 10, "수고하셨습니다. 총 10단계의 심층 분석이 모두 완료되었습니다. 아래에서 결과를 확인하세요!")
            
        st.markdown("💬 **[질문 10] 오늘을 잘 마무리하고 새로운 내일을 맞이하기 위해, 오늘 밤 당장 하고 싶은 행동은 무엇인가요?**")
        if 'J' in st.session_state.user_mbti:
            if st.button("1. 내일 해야 할 일 리스트(To-do)를 꼼꼼하게 미리 작성해둡니다."): step10_choice("To-do 리스트 작성")
            if st.button("2. 방 청소나 주변 정리를 하면서 눈앞의 상황부터 통제합니다."): step10_choice("주변 정리 및 청소")
            if st.button("3. 평소 매일 지키던 나만의 저녁 루틴(독서, 스트레칭 등)을 수행합니다."): step10_choice("저녁 루틴 수행")
            if st.button("4. 내일 입을 옷이나 챙길 물건들을 가방에 미리 다 준비해둡니다."): step10_choice("내일 짐 미리 챙기기")
        else:
            if st.button("1. 내일 일은 내일 생각하고, 지금 당장 내 마음이 가장 끌리는 것을 합니다."): step10_choice("당장 끌리는 일 하기")
            if st.button("2. 아무런 계획 없이 유튜브나 넷플릭스 알고리즘에 내 몸을 맡깁니다."): step10_choice("알고리즘에 몸 맡기기")
            if st.button("3. 갑자기 영감이 떠오르는 새로운 관심사나 정보를 검색해 봅니다."): step10_choice("새로운 관심사 탐색")
            if st.button("4. 알람만 대충 맞춰두고 복잡한 생각 없이 일단 푹 자면서 충전합니다."): step10_choice("푹 자면서 충전")

    # ==============================================================================
    # [Step 11] 최종 결과 도출 (그래프 시각화 및 맞춤형 처방전 렌더링)
    # ==============================================================================
    elif st.session_state.step == 11: 
        st.success("🎉 10단계 심층 분석이 완료되었습니다!")
        st.subheader("📊 4대 심리 지표 결과")
        
        # --- 그래프 생성 및 폰트 경로 매핑 ---
        if platform.system() == 'Windows': font_path = 'C:/Windows/Fonts/malgun.ttf'
        elif platform.system() == 'Darwin': font_path = '/System/Library/Fonts/AppleGothic.ttf'
        else: font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
            
        if os.path.exists(font_path): font_prop = fm.FontProperties(fname=font_path)
        else: font_prop = fm.FontProperties()
            
        fig, ax = plt.subplots(figsize=(7, 4.5))
        categories = list(st.session_state.metrics.keys())
        scores = list(st.session_state.metrics.values())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        
        bars = ax.bar(categories, scores, color=colors, width=0.5)
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval}점', 
                    ha='center', va='bottom', fontweight='bold', fontproperties=font_prop)

        ax.set_title(f"{st.session_state.user_name}({st.session_state.user_mbti})님의 심리 지표", pad=15, fontproperties=font_prop)
        ax.set_ylabel("점수 (100점 만점)", fontproperties=font_prop)
        ax.set_ylim(0, 110)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, fontproperties=font_prop)
        
        st.pyplot(fig)
        
        # --- 맞춤형 처방전 텍스트 알고리즘 ---
        mbti = st.session_state.user_mbti
        cause = st.session_state.stress_cause
        stress_score = scores[0]
        stab_score = scores[2]
        
        txt_content = (
            f"==== {st.session_state.user_name}님을 위한 심리 분석 보고서 ====\n"
            f"▶ 성향(MBTI): {mbti}\n"
            f"▶ 핵심 심리 자극 요인: [{cause}]\n\n"
            f"[4대 심리 지표 결과]\n"
            f"- 스트레스: {scores[0]}점 | 자신감: {scores[1]}점 | 감정 안정성: {scores[2]}점 | 생활만족도: {scores[3]}점\n\n"
        )

        txt_content += "[👨‍⚕️ 전문 심리상담가의 종합 소견 및 처방]\n"
        txt_content += f"안녕하세요 {st.session_state.user_name}님. 오늘 남겨주신 마음의 흔적들을 주의 깊게 살펴보았습니다.\n\n"

        if stress_score >= 60 or stab_score <= 40:
            txt_content += f"현재 '{cause}'(으)로 인해 심리적 피로감이 상당히 누적된 상태이시군요. "
            txt_content += "우리는 이렇게 스트레스가 높아질 때, 상황을 실제보다 더 부정적으로 해석하게 만드는 '자동적 사고(Automatic Thoughts)'가 스위치처럼 켜지곤 합니다.\n\n"

            if 'T' in mbti:
                txt_content += f"특히 {mbti} 성향을 가지신 분들은 이럴 때 통제할 수 없는 변수나 비합리적인 상황을 마주하면, '이걸 완벽하게 해결해야만 해'라는 생각의 틀(인지적 오류)에 스스로를 옭아매기 쉽습니다. "
            else:
                txt_content += f"특히 {mbti} 성향을 가지신 분들은 주변의 분위기나 타인의 감정에 민감하여, '이 상황이 나 때문에 벌어진 것은 아닐까?' 하고 책임을 내면화하는 인지적 오류에 빠지기 쉽습니다. "
            
            txt_content += "지금 느끼는 답답함과 무력감은 당신이 부족해서가 아닙니다. 그만큼 당신이 이 상황을 책임감 있게 잘 해내고 싶어 한다는 반증이라는 점을 꼭 기억해 주셨으면 합니다.\n\n"
            
            txt_content += "💡 [오늘 밤을 위한 구체적 행동 처방]\n"
            txt_content += "지금 당장 거창한 해결책을 찾으려 애쓰지 마세요. 팽팽하게 당겨진 활시위를 잠시 늦춰야 할 때입니다.\n"
            
            if 'E' in mbti:
                txt_content += "▶ 에너지의 환기: 묵혀둔 감정을 밖으로 꺼내야 합니다. 가벼운 산책을 하거나, 편안한 사람과 일상적인 대화를 나누며 내면의 압력을 외부로 덜어내 보세요.\n"
            else:
                txt_content += "▶ 감각의 차단: 외부의 자극을 최소화하고 시각과 청각을 쉬게 해주세요. 조용한 공간에서 복잡한 생각들을 일기에 적어 내려가며, 내 감정을 한 걸음 떨어져서 객관적으로 바라보는 시간이 필요합니다.\n"
                
            if 'J' in mbti:
                txt_content += "▶ 통제감 내려놓기: 내일의 계획표에서 가장 '덜 중요한' 한 가지를 과감히 지워보세요. 100% 완벽하지 않아도, 일상은 생각보다 안전하게 흘러간다는 것을 뇌에 알려주어야 합니다.\n"
            else:
                txt_content += "▶ 작은 통제감 회복: 내일은 거창한 계획 대신 '아침에 물 한 잔 마시기' 같은 아주 작은 목표를 세우고 달성해 보세요. 소소한 성취감이 무너진 내면의 질서를 회복시켜 줄 것입니다.\n"

        else:
            txt_content += f"현재 '{cause}' 요인이 있었음에도 불구하고, {st.session_state.user_name}님의 4대 심리 지표는 매우 건강한 균형을 유지하고 있습니다.\n"
            txt_content += f"{mbti} 성향 특유의 장점을 발휘하여 스트레스 상황을 자신만의 방식으로 지혜롭게 소화해 내고 계신 모습이 무척 인상 깊습니다.\n\n"
            txt_content += "마치 단단하게 뿌리내린 나무처럼, 외부의 거센 바람 앞에서도 내면의 중심을 잃지 않고 상황을 유연하게 재해석하는 훌륭한 '회복 탄력성'을 지니고 계시네요.\n\n"
            txt_content += "💡 [앞으로를 위한 지지 메시지]\n"
            txt_content += "지금처럼 당신의 마음이 보내는 신호에 귀 기울이고, 스스로를 다독일 줄 아는 건강한 루틴을 계속 유지해 주시기 바랍니다. 때로는 흔들릴 날도 있겠지만, 지금의 단단한 마음 근육이 당신을 든든하게 지켜줄 것입니다.\n"

        txt_content += "\n당신의 모든 내일을 진심으로 응원합니다. - 심리상담 챗봇 올림 -"
        
        # --- UI 전용 렌더링 (마크다운 적용) ---
        ui_text = txt_content.replace('\n', '<br>')
        ui_text = ui_text.replace(
            f"==== {st.session_state.user_name}님을 위한 심층 심리 분석 보고서 ====<br>",
            f"<div style='text-align: center; font-weight: bold; font-size: 1.1em; color: #1E88E5; margin-bottom: 15px;'>"
            f"==== {st.session_state.user_name}님을 위한 심층 심리 분석 보고서 ====</div>"
        )
        
        st.markdown(f"""
        <div style="background-color: rgba(30, 136, 229, 0.05); padding: 20px; border-radius: 10px; border-left: 5px solid #1E88E5; line-height: 1.6;">
            {ui_text}
        </div>
        """, unsafe_allow_html=True)

        # --- 산출물 다운로드 모듈 ---
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📝 처방전 텍스트 다운로드", 
                data=txt_content, 
                file_name=f"처방전_{st.session_state.user_name}_{timestamp}.txt", 
                mime="text/plain"
            )
        with col2:
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
            st.download_button(
                label="📉 그래프 이미지 다운로드", 
                data=buf.getvalue(), 
                file_name=f"그래프_{st.session_state.user_name}_{timestamp}.png", 
                mime="image/png"
            )
        
        if st.button("🔄 처음부터 다시 하기"):
            st.session_state.clear()
            st.rerun()