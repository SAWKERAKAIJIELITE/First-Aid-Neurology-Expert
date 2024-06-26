from experta import *
from schema import Or


class Question(Fact):
    subject = text = Field(str, True)
    Type = Field(Or('multiple', 'single', 'bool', 'int', 'words'), True)
    valid = Field(Or(list, int))
    certainity_factor = Field(float)


class Answer(Fact):
    subject = Field(str, True)
    text = Field(Or(str, bool, int, list), True)
    certainity_factor = Field(float)


class Headache(KnowledgeEngine):

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
            subject="Headache",
            Type="bool",
            text="Is there a history of drug?"
        )
        yield Question(
            subject="Alcohol?",
            Type="bool",
            text="Is there a History of Alcohol?"
        )
        yield Question(
            subject="Caffeine?",
            Type="bool",
            text="Is there a history Caffeine??"
        )
        yield Question(
            subject="Trauma?",
            Type="bool",
            text="Is there a history of Trauma?"
        )
        yield Question(
            subject="Acute Or Chronic",
            Type="single",
            valid=["Acute", "Chronic"],
            text="Is it ?"
        )
        yield Question(
            subject="rigidity",
            Type="bool",
            text="Is there nuchal rigidity?"
        )
        yield Question(
            subject="fever",
            Type="bool",
            text="Is there fever?"
        )
        yield Question(
            subject="sinuses",
            Type="bool",
            text="Do the sinuses transilluminate well?"
        )
        yield Question(
            subject="focal neurologic signs",
            Type="bool",
            text="Are there focal neurologic signs?"
        )
        yield Question(
            subject="Neurological examintion",
            Type="bool",
            text="Is it Healthy?"
        )
        yield Question(
            subject="papilledema",
            Type="bool",
            text="Is there papilledema or are there focal neurologic signs?"
        )
        yield Question(
            subject="tenderness",
            Type="bool",
            text="Is there tenderness of the superficial temporal artery?"
        )
        yield Question(
            subject="headache relieved",
            Type="bool",
            text="Is the headache relieved?"
        )

    @Rule(
        NOT(Answer(subject='Headache')),
        NOT(Fact(ask='Headache'))
    )
    def ask_about_Headache(self):
        self.declare(Fact(ask="Headache"))

    @Rule(
        AS.question << Question(subject=MATCH.subject),
        NOT(Answer(subject=MATCH.subject)),
        AS.ask << Fact(ask=MATCH.subject)
    )
    def ask_Question_by_subject(self, question, ask, subject):
        self.retract(ask)
        answer = self.ask_user(question)
        self.declare(Answer(subject=subject, text=answer))

    @Rule(Answer(subject='Headache', text=True))
    def drug(self):
        self.considerations(['Chronic Aspirin Intoxication', 'Cinchonism'])
        self.halt()

    @Rule(Answer(subject='Headache', text=False))
    def not_drug(self):
        self.declare(Fact(ask="Alcohol"))

    @Rule(Answer(subject='Alcohol', text=True))
    def Alcohol(self):
        self.considerations(['Alcoholism'])
        self.halt()

    @Rule(Answer(subject='Alcohol', text=False))
    def not_Alcohol(self):
        self.declare(Fact(ask="Caffeine"))

    @Rule(Answer(subject='Caffeine', text=True))
    def Caffeine(self):
        self.considerations(['Caffeine withdrawal headaches'])
        self.halt()

    @Rule(Answer(subject='Caffeine', text=False))
    def not_Caffeine(self):
        self.declare(Fact(ask="Trauma"))

    @Rule(Answer(subject='Trauma', text=True))
    def Trauma(self):
        self.considerations([
            'Intracranial hematoma', 'concussion', 'postconcussion'
        ])
        self.halt()

    @Rule(Answer(subject='Trauma', text=False))
    def not_Trauma(self):
        self.declare(Fact(ask="Acute Or Chronic"))

    @Rule(Answer(subject='Acute Or Chronic', text="Acute"))
    def acute(self):
        self.declare(Fact(ask="rigidity"))

    @Rule(Answer(subject='Acute Or Chronic', text="Chronic"))
    def chronic(self):
        print("Perform a complete Neurological examintion")
        self.declare(Fact(ask="Neurological examintion"))

    @Rule(Answer(subject='rigidity', text=MATCH.t & True))
    def rigidity(self, t):
        self.declare(Fact(ask="fever"))
        self.declare(Fact(first=t))

    @Rule(Answer(subject='rigidity', text=MATCH.t & False))
    def not_rigidity(self, t):
        self.declare(Fact(ask="fever"))
        self.declare(Fact(first=t))

    @Rule(
        Answer(subject='fever', text=True),
        Fact(first=True)
    )
    def rigidity_fever(self):
        self.declare(Fact(ask="focal neurologic signs"))

    @Rule(
        Answer(subject='fever', text=False),
        Fact(first=True)
    )
    def rigidity_not_fever(self):
        self.considerations(['Subarachnoid Hemorrhage'])
        self.halt()

    @Rule(
        Answer(subject='fever', text=True),
        Fact(first=False)
    )
    def not_rigidity_fever(self):
        self.declare(Fact(ask="sinuses"))

    @Rule(
        Answer(subject='fever', text=False),
        Fact(first=False)
    )
    def not_rigidity_not_fever(self):
        self.considerations([
            'migraine', 'temporal arteritis', 'Cluster Headache'
        ])
        self.halt()

    @Rule(Answer(subject='focal neurologic signs', text=True))
    def focal_neurologic_signs(self):
        self.considerations(['Cerebral Abscess', 'Cerebral Hemorrhage'])
        self.halt()

    @Rule(Answer(subject='focal neurologic signs', text=False))
    def not_focal_neurologic_signs(self):
        self.considerations(['Subarachnoid Hemorrhage', 'Meningitis'])
        self.halt()

    @Rule(Answer(subject='sinuses', text=True))
    def sinuses(self):
        self.considerations(['Acute Sinusitis'])
        self.halt()

    @Rule(Answer(subject='sinuses', text=False))
    def not_sinuses(self):
        self.considerations(['Encephalitis'])
        self.halt()

    @Rule(Answer(subject='Neurological examintion', text=True))
    def neurological_examintion_alright(self):
        self.declare(Fact(ask="tenderness"))

    @Rule(Answer(subject='Neurological examintion', text=False))
    def neurological_examintion_not_alright(self):
        self.declare(Fact(ask="papilledema"))

    @Rule(Answer(subject='papilledema', text=True))
    def papilledema(self):
        self.considerations(['space-occupying lesion'])
        self.halt()

    @Rule(Answer(subject='papilledema', text=False))
    def not_papilledema(self):
        self.considerations([
            'Hypertension', 'Pseudotumor Cerebri', 'early space-occupying lesion'
        ])
        self.halt()

    @Rule(Answer(subject='tenderness', text=True))
    def tenderness(self):
        self.considerations(['temporal arteritis'])
        self.halt()

    @Rule(Answer(subject='tenderness', text=False))
    def not_tenderness(self):
        print("Compress superficial temporal artery")
        self.declare(Fact(ask="headache relieved"))

    @Rule(Answer(subject='headache relieved', text=True))
    def headache_relieved(self):
        self.considerations(['classical or common migraine'])
        self.halt()

    @Rule(Answer(subject='headache relieved', text=False))
    def headache_not_relieved(self):
        self.considerations([
            'occipital migraine', 'tension headaches', 'cervical spondylosis', 'Eye Strain'
        ])
        self.halt()
