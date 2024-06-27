from experta import *
from schema import Or


class Question(Fact):
    subject = text = Field(str, True)
    Type = Field(Or(
        'multiple', 'single', 'bool', 'int', 'float', 'words'
    ), True)
    valid = Field(Or(list, int))
    certainity_factor = Field(float)


class Answer(Fact):
    subject = Field(str, True)
    text = Field(Or(str, bool, int, float, list), True)
    certainity_factor = Field(float)


class ChestPain(KnowledgeEngine):

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
        
        if question['Type'] == 'float':
            return float(input())

        if question['Type'] == 'words':
            return input()

    @DefFacts()
    def init(self):

        yield Question(
            subject="CHEST PAIN",
            Type="bool",
            text="Is the pain constant?"
        )
        yield Question(
            subject="BREATHING",
            Type="bool",
            text="Does the pain PRECIPITATED OR INCREASED BY BREATHING?"
        )
        yield Question(
            subject="Duration",
            Type="float",
            text="How long minutes does it last?"
        )
        yield Question(
            subject="HYPERTENSION",
            Type="bool",
            text="Is the pain WITH SIGNIFICANT HYPERTENSION?"
        )
        yield Question(
            subject="ANTACID",
            Type="bool",
            text="Does the pain RELIEF BY ANTACID?"
        )
        yield Question(
            subject="HEMOPTYSIS",
            Type="bool",
            text="Is the pain WITH HEMOPTYSIS?"
        )
        yield Question(
            subject="FEVER AND SPUTUM",
            Type="bool",
            text="Is the pain WITH FEVER AND PURULENT SPUTUM?"
        )
        yield Question(
            subject="MOVEMENT",
            Type="bool",
            text="Does the pain AGGRAVATE BY MOVEMENT?"
        )

    @Rule(
        NOT(Answer(subject='CHEST PAIN')),
        NOT(Fact(ask='CHEST PAIN'))
    )
    def ask_about_CHEST_PAIN(self):
        self.declare(Fact(ask="CHEST PAIN"))

    @Rule(
        AS.question << Question(subject=MATCH.subject),
        NOT(Answer(subject=MATCH.subject)),
        AS.ask << Fact(ask=MATCH.subject)
    )
    def ask_Question_by_subject(self, question, ask, subject):
        self.retract(ask)
        answer = self.ask_user(question)
        self.declare(Answer(subject=subject, text=answer))

    @Rule(Answer(subject='CHEST PAIN', text=True))
    def constant(self):
        self.declare(Fact(ask="HYPERTENSION"))

    @Rule(Answer(subject='CHEST PAIN', text=False))
    def not_constant(self):
        self.declare(Fact(ask="BREATHING"))

    @Rule(Answer(subject='BREATHING', text=True))
    def BREATHING(self):
        self.considerations([
            'PLEURISY', 'FRACTURED RIB', 'COSTOCHONDRITIS PNEUMOTHORAX',
        ])
        self.halt()

    @Rule(Answer(subject='BREATHING', text=False))
    def not_BREATHING(self):
        self.declare(Fact(ask="Duration"))

    @Rule(Answer(subject='Duration', text=LE(2)))
    def short_duration(self):
        self.considerations(['ANGINA PECTORIS'])
        self.halt()

    @Rule(Answer(subject='Duration', text=GT(2)))
    def long_duration(self):
        self.considerations(['CORONARY INSUFFICIENCY'])
        self.halt()

    @Rule(Answer(subject='HYPERTENSION', text=True))
    def HYPERTENSION(self):
        self.considerations([
            'DISSECTING ANEURYSM', 'MYOCARDIAL INFARCTION', 'COCAINE USE'
        ])
        self.halt()

    @Rule(Answer(subject='HYPERTENSION', text=False))
    def not_HYPERTENSION(self):
        self.declare(Fact(ask="ANTACID"))

    @Rule(Answer(subject='ANTACID', text=True))
    def ANTACID(self):
        self.considerations(['ESOPHAGITIS AND HIATAL HERNIA'])
        self.halt()

    @Rule(Answer(subject='ANTACID', text=False))
    def not_ANTACID(self):
        self.declare(Fact(ask="HEMOPTYSIS"))

    @Rule(Answer(subject='HEMOPTYSIS', text=True))
    def HEMOPTYSIS(self):
        self.considerations(['PULMONARY EMBOLISM'])
        self.halt()

    @Rule(Answer(subject='HEMOPTYSIS', text=False))
    def not_HEMOPTYSIS(self):
        self.declare(Fact(ask="FEVER AND SPUTUM"))

    @Rule(Answer(subject='FEVER AND SPUTUM', text=True))
    def FEVER_AND_SPUTUM(self):
        self.considerations(['PNEUMONIA'])
        self.halt()

    @Rule(Answer(subject='FEVER AND SPUTUM', text=False))
    def not_FEVER_AND_SPUTUM(self):
        self.declare(Fact(ask="MOVEMENT"))

    @Rule(Answer(subject='MOVEMENT', text=True))
    def MOVEMENT(self):
        self.considerations(['PERICARDITIS'])
        self.halt()

    @Rule(Answer(subject='MOVEMENT', text=False))
    def not_MOVEMENT(self):
        self.considerations([
            'PANIC DISORDER', 'MYOCARDIAL INFARCTION', 'HYPERVENTILATION SYNDROME'
        ])
        self.halt()
