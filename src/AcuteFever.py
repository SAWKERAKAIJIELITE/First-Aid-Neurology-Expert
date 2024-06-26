from experta import *
from schema import Or
from ChestPain import ChestPain
from Headache import Headache
from AbdominalPain import AbdominalPain


class Question(Fact):
    subject = text = Field(str, True)
    Type = Field(Or('multiple', 'single', 'bool', 'int', 'words'), True)
    valid = Field(Or(list, int))
    certainity_factor = Field(float)


class Answer(Fact):
    subject = Field(str, True)
    text = Field(Or(str, bool, int, list), True)
    certainity_factor = Field(float)


class AcuteFever(KnowledgeEngine):

    @staticmethod
    def recommend_action(action):
        print(f"I recommend you to {action}")

    @staticmethod
    def considerations(action, certainity_factor: float = 0):
        if certainity_factor == 0:
            print(f"Consider to: {action}")
        else:
            print(
                f"Consider to: {action} with probability factor of {certainity_factor}")

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
            print("You can select multiple choices seperated by space")

            l = input().split()
            q = []
            for item in l:
                q.append(question['valid'][int(item)-1])
            return q

        if question['Type'] == 'bool':
            return bool(input())

        if question['Type'] == 'int':
            return int(input())

        if question['Type'] == 'words':
            return input()

    @DefFacts()
    def init(self):

        yield Question(
            subject="ACUTE FEVER",
            Type="bool",
            text="Is there a history of drug ingestion or injection?"
        )
        yield Question(
            subject="Rash",
            Type="bool",
            text="Is there a rash?"
        )
        yield Question(
            subject="Pain",
            Type="bool",
            text="Do you feel pain?"
        )
        yield Question(
            subject="UPPER RESPIRATORY SYMPTOMS",
            Type="bool",
            text="Do you have UPPER RESPIRATORY SYMPTOMS ?"
        )
        yield Question(
            subject="FREQUENCY OR BURNING ON URINATION",
            Type="bool",
            text="Do you have FREQUENCY OR BURNING when you urinate?"
        )
        yield Question(
            subject="Pain Location",
            Type="multiple",
            valid=[
                "SORE THROAT",
                "EARACHE",
                "CHEST PAIN",
                "HEADACHE",
                "ABDOMINAL Pain"
            ],
            text="Where is the Pain?"
        )

    @Rule(
        NOT(Answer(subject='ACUTE FEVER')),
        NOT(Fact(ask='ACUTE FEVER'))
    )
    def ask_about_ACUTE_FEVER(self):
        self.declare(Fact(ask="ACUTE FEVER"))

    @Rule(
        AS.question << Question(subject=MATCH.subject),
        NOT(Answer(subject=MATCH.subject)),
        AS.ask << Fact(ask=MATCH.subject)
    )
    def ask_Question_by_subject(self, question, ask, subject):
        self.retract(ask)
        answer = self.ask_user(question)
        self.declare(Answer(subject=subject, text=answer))

    @Rule(Answer(subject='ACUTE FEVER', text=True))
    def ACUTE_FEVER(self):
        self.considerations(['DRUG REACTION', 'SERUM SICKNESS'], 0.4)
        self.halt()

    @Rule(Answer(subject='ACUTE FEVER', text=False))
    def not_ACUTE_FEVER(self):
        self.declare(Fact(ask="Rash"))

    @Rule(Answer(subject='Rash', text=True))
    def Rash(self):
        self.considerations([
            'MENINGOCOCCEMIA',
            'DRUG REACTION',
            'EXANTHEMA',
            'SUBACUTE BACTERIAL ENDOCARDITIS'
        ])
        self.halt()

    @Rule(Answer(subject='Rash', text=False))
    def not_Rash(self):
        self.declare(Fact(ask="Pain"))

    @Rule(Answer(subject='Pain', text=True))
    def PAIN(self):
        self.declare(Fact(ask="Pain Location"))

    @Rule(Answer(subject='Pain', text=False))
    def not_PAIN(self):
        self.declare(Fact(ask="UPPER RESPIRATORY SYMPTOMS"))

    @Rule(Answer(subject='UPPER RESPIRATORY SYMPTOMS', text=True))
    def UPPER_RESPIRATORY_SYMPTOMS(self):
        self.considerations([
            'VIRAL UPPER RESPIRATORY INFECTION',
            'INFECTIOUS MONONUCLEOSIS',
            'STREPTOCOCCAL PHARYNGITIS'
        ])
        self.halt()

    @Rule(Answer(subject='UPPER RESPIRATORY SYMPTOMS', text=False))
    def not_UPPER_RESPIRATORY_SYMPTOMS(self):
        self.declare(Fact(ask="FREQUENCY OR BURNING ON URINATION"))

    @Rule(Answer(subject='FREQUENCY OR BURNING ON URINATION', text=False))
    def not_FREQUENCY_OR_BURNING_ON_URINATION(self):
        self.considerations(['DRUG REACTION', 'VIREMIA', 'BACTEREMIA'])
        self.halt()

    @Rule(Answer(subject='FREQUENCY OR BURNING ON URINATION', text=True))
    def FREQUENCY_OR_BURNING_ON_URINATION(self):
        self.considerations(['ACUTE PROSTATITIS', 'PYELONEPHRITIS'])
        self.halt()

    @Rule(Answer(subject='Pain Location', text=MATCH.t))
    def pain_location(self, t):
        ks_list = []
        for item in t:
            if item == "SORE THROAT":
                self.considerations([
                    'STREPTOCOCCAL PHARYNGITIS', 'VIRAL UPPER RESPIRATORY INFECTION'
                ])
            if item == "EARACHE":
                self.considerations(['OTITIS MEDIA'])
            if item == "CHEST PAIN":
                cp = ChestPain()
                cp.reset()
                ks_list.append(cp)
                cp.run()
            if item == "HEADACHE":
                h = Headache()
                h.reset()
                ks_list.append(h)
                h.run()
            if item == "ABDOMINAL Pain":
                ap = AbdominalPain()
                ap.reset()
                ks_list.append(ap)
                ap.run()

        # for item in ks_list:
        #     if item.running:
        #         pass

            self.halt()
