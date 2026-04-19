import streamlit as st
from ai_engine import generate_explanation, generate_quiz
from tracker import QuizTracker
from database import register, login, save_score, get_history

# -------- UI STYLE -------- #
st.markdown("""
<style>

/* ===== BACKGROUND ===== */
.stApp {
    background: radial-gradient(circle at 10% 20%, #1e3a8a, transparent),
                radial-gradient(circle at 90% 80%, #7c3aed, transparent),
                linear-gradient(135deg, #020617, #0f172a);
    background-attachment: fixed;
    color: white;
}

/* ===== NAVBAR ===== */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 25px;
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    margin-bottom: 20px;
}

/* Logo */
.logo {
    font-size: 22px;
    font-weight: bold;
}

/* ===== CARD ===== */
.card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(15px);
    padding: 25px;
    border-radius: 20px;
    margin-top: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

/* ===== BUTTONS ===== */
.stButton>button {
    border-radius: 10px;
    padding: 10px;
    font-weight: 600;
    background: linear-gradient(45deg, #2563eb, #7c3aed);
    color: white;
    border: none;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 12px #7c3aed;
}

/* ===== PROGRESS ===== */
.stProgress > div > div {
    background: linear-gradient(90deg, #2563eb, #7c3aed);
}

</style>
""", unsafe_allow_html=True)

# -------- LOGIN SYSTEM -------- #
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.title("🔐 Login / Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            if login(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("New Username", key="reg_user")
        p = st.text_input("New Password", type="password", key="reg_pass")

        if st.button("Register"):
            if register(u, p):
                st.success("Account created!")
            else:
                st.error("User already exists")

    st.stop()

# -------- NAVBAR -------- #
st.markdown(f"""
<div class="navbar">
    <div class="logo">📚 AI Study Assistant</div>
    <div>👤 {st.session_state.user}</div>
</div>
""", unsafe_allow_html=True)

# -------- SIDEBAR -------- #
st.sidebar.success(f"👤 {st.session_state.user}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.sidebar.subheader("📜 History")

history = get_history(st.session_state.user)

if history:
    for h in history[::-1]:
        st.sidebar.write(f"{h[0]} → {h[1]}/10")
else:
    st.sidebar.write("No history yet")

# -------- INPUT SECTION -------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown("### 🎯 Choose what you want to do")

topic = st.text_input("Enter topic")
difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

col1, col2 = st.columns(2)

if col1.button("📖 Explain"):
    if topic:
        st.session_state.explanation = generate_explanation(topic)
        st.session_state.mode = "explain"
    else:
        st.warning("Enter topic!")

if col2.button("📝 Quiz"):
    if topic:
        quiz = generate_quiz(topic, difficulty)

        for q in quiz:
            q["correct_answer"] = q["answer"]
            del q["answer"]

        st.session_state.tracker = QuizTracker(quiz)
        st.session_state.topic = topic
        st.session_state.mode = "quiz"
    else:
        st.warning("Enter topic!")

st.markdown('</div>', unsafe_allow_html=True)

# -------- MODE -------- #
if "mode" not in st.session_state:
    st.session_state.mode = "home"

# -------- EXPLAIN -------- #
elif st.session_state.mode == "explain":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📖 Explanation")
    st.write(st.session_state.explanation)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- QUIZ -------- #
elif st.session_state.mode == "quiz":

    tracker = st.session_state.tracker
    q = tracker.get_current_question()

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader(f"Question {tracker.current_q + 1}/10")
    st.write(q["question"])

    choice = st.radio(
        "Select answer",
        q["options"],
        index=None,
        key=f"q{tracker.current_q}"
    )

    if choice:
        tracker.answer_current(choice[0])

    col1, col2 = st.columns(2)

    if col1.button("⬅ Prev", disabled=(tracker.current_q == 0)):
        tracker.prev_question()
        st.rerun()

    if col2.button("Next ➡", disabled=(tracker.answers[tracker.current_q] is None)):
        tracker.next_question()
        st.rerun()

    st.progress((tracker.current_q + 1) / 10)

    # -------- SUBMIT -------- #
    if tracker.current_q == 9 and tracker.is_finished():
        if st.button("Submit"):
            correct = 0

            st.subheader("📊 Result")

            for i, q in enumerate(tracker.quiz):
                user = tracker.answers[i]
                correct_ans = q["correct_answer"]

                if user == correct_ans:
                    correct += 1
                    st.success(f"Q{i+1}: Correct")
                else:
                    st.error(f"Q{i+1}: Wrong (Correct: {correct_ans})")

            st.write(f"Score: {correct}/10")

            save_score(st.session_state.user, st.session_state.topic, correct)

    st.markdown('</div>', unsafe_allow_html=True)
