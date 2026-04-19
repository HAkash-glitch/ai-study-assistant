class QuizTracker:
    def __init__(self, quiz):
        self.quiz = quiz
        self.current_q = 0
        self.answers = [None] * len(quiz)

    def get_current_question(self):
        return self.quiz[self.current_q]

    def answer_current(self, ans):
        self.answers[self.current_q] = ans

    def next_question(self):
        if self.current_q < len(self.quiz) - 1:
            self.current_q += 1

    def prev_question(self):
        if self.current_q > 0:
            self.current_q -= 1

    def is_finished(self):
        return None not in self.answers