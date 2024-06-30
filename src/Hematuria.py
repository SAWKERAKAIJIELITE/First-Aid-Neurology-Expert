from experta import *
from schema import Or


class Question(Fact):
    subject = text = Field(str, True)
    Type = Field(Or('multiple', 'single', 'bool', 'int', 'words'), True)
    valid = Field(Or(list, int))


class Answer(Fact):
    subject = Field(str, True)
    text = Field(Or(str, bool, int, list), True)


class Hematuria(KnowledgeEngine):

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
            subject="Hematuria",
            Type="bool",
            text="Is there ABDOMINAL PAIN?"
        )
        yield Question(
            subject="DYSURIA",
            Type="bool",
            text="Is there DYSURIA OR FREQUENCY?"
        )
        yield Question(
            subject="FLANK MASS",
            Type="bool",
            text="Is there FLANK MASS?"
        )
        yield Question(
            subject="FEVER",
            Type="bool",
            text="Is there FEVER?"
        )
        yield Question(
            subject="HYPERTENSION",
            Type="bool",
            text="Is there HYPERTENSION?"
        )
        yield Question(
            subject="SYSTEMIC SIGNS AND SYMPTOMS",
            Type="bool",
            text="Is there Fever, jaundice, Edema?"
        )
        yield Question(
            subject="U OR B",
            Type="single",
            valid=["BILATERAL", "UNILATERAL"],
            text="Is it ?"
        )

    @Rule(
        NOT(Answer(subject='Hematuria')),
        NOT(Fact(ask='Hematuria'))
    )
    def ask_about_hematuria(self):
        self.declare(Fact(ask="Hematuria"))

    @Rule(
        AS.question << Question(subject=MATCH.subject),
        NOT(Answer(subject=MATCH.subject)),
        AS.ask << Fact(ask=MATCH.subject)
    )
    def ask_Question_by_subject(self, question, ask, subject):
        self.retract(ask)
        answer = self.ask_user(question)
        self.declare(Answer(subject=subject, text=answer))

    @Rule(Answer(subject='Hematuria', text=True))
    def ABDOMINAL_PAIN(self):
        self.considerations([
            'RENAL CALCULUS', 'RENAL EMBOLISM', 'RENAL CONTUSION OR LACERATION'
        ])
        print(self.get_activations())
        self.halt()

    @Rule(Answer(subject='Hematuria', text=False))
    def not_ABDOMINAL_PAIN(self):
        self.declare(Fact(ask="DYSURIA"))

    @Rule(Answer(subject='DYSURIA', text=True))
    def not_ABDOMINAL_PAIN_DYSURIA(self):
        self.declare(Fact(ask="FEVER"))

    @Rule(Answer(subject='DYSURIA', text=False))
    def not_ABDOMINAL_PAIN_not_DYSURIA(self):
        self.declare(Fact(ask="FLANK MASS"))

    @Rule(Answer(subject='FLANK MASS', text=True))
    def not_ABDOMINAL_PAIN_not_DYSURIA_FLANK_MASS(self):
        self.declare(Fact(ask="U OR B"))

    @Rule(Answer(subject='U OR B', text="BILATERAL"))
    def BILATERAL(self):
        self.considerations(['POLYCYSTIC KIDNEY', 'HYDRONEPHROSIS'])
        self.halt()

    @Rule(Answer(subject='U OR B', text="UNILATERAL"))
    def UNILATERAL(self):
        self.considerations([
            'HYPERNEPHROMA', 'HYDRONEPHROSIS', 'SOLITARY CYST', 'RENAL VEIN THROMBOSIS'
        ])
        self.halt()

    @Rule(Answer(subject='FLANK MASS', text=False))
    def not_ABDOMINAL_PAIN_not_DYSURIA_not_FLANK_MASS(self):
        self.declare(Fact(ask="HYPERTENSION"))

    @Rule(Answer(subject='FEVER', text=True))
    def not_ABDOMINAL_PAIN_DYSURIA_Fever(self):
        self.considerations(['PYELONEPHRITIS'])
        self.halt()

    @Rule(Answer(subject='FEVER', text=False))
    def not_ABDOMINAL_PAIN_DYSURIA_not_Fever(self):
        self.considerations(['CYSTITIS', 'BLADDER STONE', 'PROSTATE DISEASE'])
        self.halt()

    @Rule(Answer(subject='HYPERTENSION', text=False))
    def not_ABDOMINAL_PAIN_not_DYSURIA_not_FLANK_MASS_not_HYPERTENSION(self):
        self.declare(Fact(ask="SYSTEMIC SIGNS AND SYMPTOMS"))

    @Rule(Answer(subject='HYPERTENSION', text=True))
    def not_ABDOMINAL_PAIN_not_DYSURIA_not_FLANK_MASS_HYPERTENSION(self):
        self.considerations([
            'GLOMERULONEPHRITIS', 'COLLAGEN DISEASE', 'RENAL ARTERY STENOSIS'
        ])
        self.halt()

    @Rule(Answer(subject='SYSTEMIC SIGNS AND SYMPTOMS', text=True))
    def not_ABDOMINAL_PAIN_not_DYSURIA_not_FLANK_MASS_not_HYPERTENSION_SYSTEMIC_SIGNS_AND_SYMPTOMS(self):
        self.considerations([
            'COLLAGEN DISEASE', 'COAGULATION DISORDER', 'LEUKEMIA', 'SICKLE CELL ANEMIA'
        ])
        self.halt()

    @Rule(Answer(subject='SYSTEMIC SIGNS AND SYMPTOMS', text=False))
    def not_ABDOMINAL_PAIN_not_DYSURIA_not_FLANK_MASS_not_HYPERTENSION_not_SYSTEMIC_SIGNS_AND_SYMPTOMS(self):
        self.considerations([
            'BENIGN OR MALIGNANT TUMOR OF THE BLADDER', 'TUBERCULOSIS OR PARASITES'
        ])
        self.halt()
