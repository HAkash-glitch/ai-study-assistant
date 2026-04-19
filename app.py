import streamlit as st
from ai_engine import generate_explanation, generate_quiz
from tracker import QuizTracker
from database import register, login, save_score, get_history

# -------- UI STYLE -------- #
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #0f172a, #1e293b, #2563eb, #7c3aed);
    background-size: 400% 400%;
    animation: gradient 12s ease infinite;
    color: white;
}
@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
.stButton>button {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("📚 AI Study Assistant")

# -------- LOGIN -------- #
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.subheader("🔐 Login / Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if login(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")

        if st.button("Register"):
            if register(u, p):
                st.success("Account created!")
            else:
                st.error("User exists")

    st.stop()

# -------- SIDEBAR -------- #
st.sidebar.success(f"👤 {st.session_state.user}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.sidebar.subheader("📜 History")
history = get_history(st.session_state.user)

for h in history[::-1]:
    st.sidebar.write(f"{h[0]} → {h[1]}/10")

# -------- INPUT -------- #
topic = st.text_input("Enter topic")
difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

col1, col2 = st.columns(2)

# -------- BUTTONS -------- #
if col1.button("📖 Explain"):
    if topic:
        st.session_state.explanation = generate_explanation(topic)
        st.session_state.mode = "explain"

if col2.button("📝 Quiz"):
    if topic:
        quiz = generate_quiz(topic, difficulty)

        for q in quiz:
            q["correct_answer"] = q["answer"]
            del q["answer"]

        st.session_state.tracker = QuizTracker(quiz)
        st.session_state.topic = topic
        st.session_state.mode = "quiz"

# -------- MODE -------- #
if "mode" not in st.session_state:
    st.session_state.mode = "home"

elif st.session_state.mode == "explain":
    st.subheader("📖 Explanation")
    st.write(st.session_state.explanation)

elif st.session_state.mode == "quiz":

    tracker = st.session_state.tracker
    q = tracker.get_current_question()

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

            save_score(st.session_state.user, topic, correct)