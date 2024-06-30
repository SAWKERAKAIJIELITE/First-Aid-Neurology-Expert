from experta import *
from schema import Or


class Question(Fact):
    subject = text = Field(str, True)
    Type = Field(Or('multiple', 'single', 'bool', 'int', 'words'), True)
    valid = Field(Or(list, int))


class Answer(Fact):
    subject = Field(str, True)
    text = Field(Or(str, bool, int, list), True)


class AbsentOrDiminishedPulse(KnowledgeEngine):

    @staticmethod
    def recommend_action(action):
        print(f"I recommend you to {action}")

    @staticmethod
    def considerations(action):
        print(f"Consider to: {action}")

    @staticmethod
    def ask_user(question):
        print(question['text'])
        if question['Type'] == 'single':
            print("Valid answers are ")
            i = 0
            for item in question['valid']:
                i += 1
                print(f"    {i}. {item}")
            return question['valid'][int(input())-1]

        if question['Type'] == 'multiple':
            print("Valid answers are ")
            i = 0
            for item in question['valid']:
                i += 1
                print(f"    {i}. {item}")
            print("You can select multiple choice seperated by space")

            l = input().split()
            q = []
            for item in l:
                q.append(question['valid'][int(item)])
            return q

        if question['Type'] == 'bool':
            print("Press Enter to choose False or any other key to choose True")
            return bool(input())

        if question['Type'] == 'int':
            return int(input())

        if question['Type'] == 'words':
            return input()

    @DefFacts()
    def init(self):

        yield Question(
            subject="ABSENT OR DIMINISHED PULSE",
            Type="single",
            valid=["UPPER", "LOWER"],
            text="Is it in the ?"
        )
        yield Question(
            subject="UNILATERAL OR BILATERAL",
            Type="single",
            valid=["UNILATERAL", "BILATERAL"],
            text="Is it ?"
        )
        yield Question(
            subject="sudden in onset",
            Type="bool",
            text="Is it sudden in onset?"
        )

    @Rule(
        AS.question << Question(subject=MATCH.subject),
        NOT(Answer(subject=MATCH.subject)),
        AS.ask << Fact(ask=MATCH.subject)
    )
    def ask_Question_by_subject(self, question, ask, subject):
        self.retract(ask)
        answer = self.ask_user(question)
        self.declare(Answer(subject=subject, text=answer))

    @Rule(
        NOT(Answer(subject='ABSENT OR DIMINISHED PULSE')),
        NOT(Fact(ask='ABSENT OR DIMINISHED PULSE'))
    )
    def ask_about_extremities(self):
        self.declare(Fact(ask="ABSENT OR DIMINISHED PULSE"))

    @Rule(Answer(subject='ABSENT OR DIMINISHED PULSE', text=MATCH.t & "UPPER"))
    def upper_extremities(self, t):
        self.declare(Fact(ask="UNILATERAL OR BILATERAL"))
        self.declare(Fact(first=t))

    @Rule(Answer(subject='ABSENT OR DIMINISHED PULSE', text=MATCH.t & "LOWER"))
    def lower_extremities(self, t):
        self.declare(Fact(ask="UNILATERAL OR BILATERAL"))
        self.declare(Fact(first=t))

    @Rule(
        Answer(subject='UNILATERAL OR BILATERAL', text=MATCH.t & "UNILATERAL"),
        AS.p << Fact(first="UPPER")
    )
    def upper_unilateral(self, p, t):
        self.modify(p, second=t)
        self.declare(Fact(ask="sudden in onset"))

    @Rule(
        Answer(subject='UNILATERAL OR BILATERAL', text=MATCH.t & "UNILATERAL"),
        AS.p << Fact(first="LOWER")
    )
    def lower_unilateral(self, p, t):
        self.modify(p, second=t)
        self.declare(Fact(ask="sudden in onset"))

    @Rule(
        Answer(subject='UNILATERAL OR BILATERAL', text=MATCH.t & "BILATERAL"),
        AS.p << Fact(first="UPPER")
    )
    def upper_bilateral(self, p, t):
        self.modify(p, second=t)
        self.declare(Fact(ask="sudden in onset"))

    @Rule(
        Answer(subject='UNILATERAL OR BILATERAL', text=MATCH.t & "BILATERAL"),
        AS.p << Fact(first="LOWER")
    )
    def lower_bilateral(self, p, t):
        self.modify(p, second=t)
        self.declare(Fact(ask="sudden in onset"))

    @Rule(
        Answer(subject='sudden in onset', text=True),
        Fact(first="UPPER", second="UNILATERAL")
    )
    def upper_unilateral_suddenly(self):
        self.considerations([
            'Dissecting Aneurysm', 'Embolism', 'Fracture', 'Arteriovenous Fistula'
        ])
        self.halt()

    @Rule(
        Answer(subject='sudden in onset', text=True),
        Fact(first="LOWER", second="UNILATERAL")
    )
    def lower_unilateral_suddenly(self):
        self.considerations(['Embolism', 'fracture', 'arteriovenous fistula'])
        self.halt()

    @Rule(
        Answer(subject='sudden in onset', text=True),
        Fact(first="UPPER", second="BILATERAL")
    )
    def upper_bilateral_suddenly(self):
        self.considerations(['Shock'])
        self.halt()

    @Rule(
        Answer(subject='sudden in onset', text=True),
        Fact(first="LOWER", second="BILATERAL")
    )
    def lower_bilateral_suddenly(self):
        self.considerations([
            'Shock', 'saddle embolism', 'dissenting aneurysm'
        ])
        self.halt()

    @Rule(
        Answer(subject='sudden in onset', text=False),
        Fact(first="UPPER", second="UNILATERAL")
    )
    def upper_unilateral_not_suddenly(self):
        self.considerations([
            'Coarctation of aorta', 'Aortic Aneurysm', 'Thoracic outlet syndrome', 'Subclavian Steal'
        ])
        self.halt()

    @Rule(
        Answer(subject='sudden in onset', text=False),
        Fact(first="LOWER", second="UNILATERAL")
    )
    def lower_unilateral_not_suddenly(self):
        self.considerations(['Arteriosclerosis'])
        self.halt()

    @Rule(
        Answer(subject='sudden in onset', text=False),
        Fact(first="UPPER", second="BILATERAL")
    )
    def upper_bilateral_not_suddenly(self):
        self.considerations(['Arteriosclerosis', 'Constrictive Pericarditis'])
        self.halt()

    @Rule(
        Answer(subject='sudden in onset', text=False),
        Fact(first="LOWER", second="BILATERAL")
    )
    def lower_bilateral_not_suddenly(self):
        self.considerations([
            'Arteriosclerosis', "leriche's syndrome", 'coarctation of the aorta'
        ])
        self.halt()
