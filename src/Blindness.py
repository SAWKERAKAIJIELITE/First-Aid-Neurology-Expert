from experta import *
from schema import Or


class Question(Fact):
    subject = text = Field(str, True)
    Type = Field(Or('multiple', 'single', 'bool', 'int', 'words'), True)
    valid = Field(Or(list, int))


class Answer(Fact):
    subject = Field(str, True)
    text = Field(Or(str, bool, int, list), True)


class BLINDNESS(KnowledgeEngine):

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
            subject="BLINDNESS",
            Type="single",
            valid=["BILATERAL", "UNILATERAL"],
            text="Is it ?"
        )
        yield Question(
            subject="sudden in onset",
            Type="bool",
            text="Is it sudden in onset?"
        )
        yield Question(
            subject="abnormalities",
            Type="bool",
            text="Are there abnormalities on ophthalmoscopic examination?"
        )
        yield Question(
            subject="transient",
            Type="bool",
            text="Is it transient?"
        )
        yield Question(
            subject="papilledema",
            Type="bool",
            text="Is there papilledema?"
        )

    @Rule(
        NOT(Answer(subject='BLINDNESS')),
        NOT(Fact(ask='BLINDNESS'))
    )
    def ask_about_blindness(self):
        self.declare(Fact(ask="BLINDNESS"))

    @Rule(
        AS.question << Question(subject=MATCH.subject),
        NOT(Answer(subject=MATCH.subject)),
        AS.ask << Fact(ask=MATCH.subject)
    )
    def ask_Question_by_subject(self, question, ask, subject):
        self.retract(ask)
        answer = self.ask_user(question)
        self.declare(Answer(subject=subject, text=answer))

    @Rule(Answer(subject='BLINDNESS', text=MATCH.t & "UNILATERAL"))
    def blindness_unilateral(self, t):
        self.declare(Fact(ask="sudden in onset"))
        self.declare(Fact(first=t))

    @Rule(Answer(subject='BLINDNESS', text=MATCH.t & "BILATERAL"))
    def blindness_bilateral(self, t):
        self.declare(Fact(ask="sudden in onset"))
        self.declare(Fact(first=t))

    @Rule(
        Answer(subject='sudden in onset', text=MATCH.t & True),
        AS.p << Fact(first="UNILATERAL")
    )
    def unilateral_suddenly(self, p, t):
        self.modify(p, second=t)
        self.declare(Fact(ask="transient"))

    @Rule(
        Answer(subject='sudden in onset', text=MATCH.t & False),
        AS.p << Fact(first="UNILATERAL")
    )
    def unilateral_not_suddenly(self, p, t):
        self.modify(p, second=t)
        self.declare(Fact(ask="abnormalities"))

    @Rule(
        Answer(subject='sudden in onset', text=MATCH.t & True),
        AS.p << Fact(first="BILATERAL")
    )
    def bilateral_suddenly(self, p, t):
        self.modify(p, second=t)
        self.declare(Fact(ask="abnormalities"))

    @Rule(
        Answer(subject='sudden in onset', text=False),
        Fact(first="BILATERAL")
    )
    def bilateral_not_suddenly(self):
        self.considerations([
            'glaucoma', 'Catarcatas', 'Pituitary Tumor', 'Toxic Amblyopia'
        ])
        self.halt()

    @Rule(Answer(subject='transient', text=True))
    def unilateral_suddenly_transient(self):
        self.considerations([
            'Transient ischemic attack', 'Epilepsy', 'Migarine', 'Hypertension'
        ])
        self.halt()

    @Rule(Answer(subject='transient', text=False))
    def unilateral_suddenly_not_transient(self):
        self.declare(Fact(ask="abnormalities"))

    @Rule(
        Answer(subject='abnormalities', text=False),
        Fact(first="UNILATERAL", second=True)
    )
    def unilateral_suddenly_not_transient_not_abnormalities(self):
        self.considerations([
            'carotid artery thrombosis', 'temporal arteritis', 'injury to the optic nerve', 'fractured skull'
        ])
        self.halt()

    @Rule(
        Answer(subject='abnormalities', text=True),
        Fact(first="UNILATERAL", second=True)
    )
    def unilateral_suddenly_not_transient_abnormalities(self):
        self.declare(Fact(ask="papilledema"))

    @Rule(
        Answer(subject='papilledema', text=True),
        Fact(first="UNILATERAL", second=True)
    )
    def unilateral_suddenly_not_transient_abnormalities_papilledema(self):
        self.considerations(['optic neuritis', 'retinal vein thrombosis'])
        self.halt()

    @Rule(
        Answer(subject='papilledema', text=False),
        Fact(first="UNILATERAL", second=True)
    )
    def unilateral_suddenly_not_transient_abnormalities_not_papilledema(self):
        self.considerations([
            'central retinal artery', 'vitreous hemorrhage', 'detached retina'
        ])
        self.halt()

    @Rule(
        Answer(subject='abnormalities', text=True),
        Fact(first="BILATERAL", second=True)
    )
    def bilateral_suddenly_abnormalities(self):
        self.declare(Fact(ask="papilledema"))

    @Rule(
        Answer(subject='papilledema', text=True),
        Fact(first="BILATERAL", second=True)
    )
    def bilateral_suddenly_abnormalities_papilledema(self):
        self.considerations([
            'space-occupying lesions of the brain', 'optic neuritis'
        ])
        self.halt()

    @Rule(
        Answer(subject='papilledema', text=False),
        Fact(first="BILATERAL", second=True)
    )
    def bilateral_suddenly_abnormalities_not_papilledema(self):
        self.considerations([
            'Acute glaucoma', 'Acute Iritis'
        ])
        self.halt()

    @Rule(
        Answer(subject='abnormalities', text=False),
        Fact(first="BILATERAL", second=True)
    )
    def bilateral_suddenly_not_abnormalities(self):
        self.considerations([
            'hysteria', 'multiple sclerosis', 'posterior cerebral artery occlusion'
        ])
        self.halt()

    @Rule(
        Answer(subject='abnormalities', text=True),
        Fact(first="UNILATERAL", second=False)
    )
    def unilateral_not_suddenly_abnormalities(self):
        self.considerations(['Glaucoma', 'Brain Tumor', 'Retinoblastoma'])
        self.halt()

    @Rule(
        Answer(subject='abnormalities', text=False),
        Fact(first="UNILATERAL", second=False)
    )
    def unilateral_not_suddenly_not_abnormalities(self):
        self.considerations(['Sphenoid Ridge Meningioma'])
        self.halt()
