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


class AbdominalPain(KnowledgeEngine):

    @staticmethod
    def ensurance_actions(action):
        print(f"ensure by doing: {action}")

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
            print("Press Enter to choose False or any other key to choose True")
            return bool(input())

        if question['Type'] == 'int':
            return int(input())

        if question['Type'] == 'words':
            return input()

    @DefFacts()
    def init(self):

        yield Question(
            subject="Abdominal Pain",
            Type="multiple",
            valid=[
                "SWEET BREATH",
                "PRODUCTIVE Cough",
                "SHOCK AND SHORTNESS OF BREATH",
                "FAMIILY OR PERSONAL HISTORY OF EPILEPSY OR MIGRAINE",
                "BLACK ANCESTRY"
            ],
            text="Is there any of these?"
        )
        yield Question(
            subject="nature of the pain",
            Type="single",
            valid=["INTERMITTENT COLICKY", 'PERSISTENT'],
            text="What is the nature of the pain?"
        )
        yield Question(
            subject="Pain Location",
            Type="single",
            valid=[
                "GENERALIZED WITH REBOUND TENDERNESS",
                'LOWER QUADRANT',
                'RIGHT UPPER QUADRANT'
            ],
            text="Where is the Pain?"
        )
        yield Question(
            subject="Examination",
            Type="single",
            valid=[
                "FLANK or HEMATURIA",
                'HYPERACTIVE BOWEL SOUNDS and TYMPANY',
                'RIGHT UPPER QUADRANT'
            ],
            text="Choose the Following?"
        )

    @Rule(
        NOT(Answer(subject='Abdominal Pain')),
        NOT(Fact(ask='Abdominal Pain'))
    )
    def ask_about_Abdominal_Pain(self):
        self.declare(Fact(ask="Abdominal Pain"))

    @Rule(
        AS.question << Question(subject=MATCH.subject),
        NOT(Answer(subject=MATCH.subject)),
        AS.ask << Fact(ask=MATCH.subject)
    )
    def ask_Question_by_subject(self, question, ask, subject):
        self.retract(ask)
        answer = self.ask_user(question)
        self.declare(Answer(subject=subject, text=answer))

    @Rule(Answer(subject='Abdominal Pain', text=[]))
    def AbdominalPain(self):
        self.declare(Fact(ask="nature of the pain"))

    @Rule(
        Answer(subject='Abdominal Pain', text=MATCH.t),
        TEST(lambda t: len(t) != 0)
    )
    def pain_location(self, t):
        if "SWEET BREATH" in t:
            self.considerations(['DIABETIC ACIDOSIS'])
        if "PRODUCTIVE Cough" in t:
            self.considerations(['PNEUMONIA'])
            self.ensurance_actions([
                " SPUTUM SMEAR EKG AND CULTURE", "CHEST X-RAY"
            ])
        if "SHOCK AND SHORTNESS OF BREATH" in t:
            self.considerations(['MYOCARDIAL INFARCTION'])
            self.ensurance_actions(["EKG SERIAL", "CARDIAC ENZYMES"])
        if "FAMIILY OR PERSONAL HISTORY OF EPILEPSY OR MIGRAINE" in t:
            self.considerations(['EPILEPSY', 'MIGRAINE', 'ANEMIA'])
            self.ensurance_actions(["EEG"])
        if "BLACK ANCESTRY" in t:
            self.considerations(['SICKLE CELL'])
        self.halt()

    @ Rule(Answer(subject='nature of the pain', text="PERSISTENT"))
    def PERSISTENT(self):
        self.declare(Fact(ask="Pain Location"))

    @ Rule(Answer(subject='nature of the pain', text="INTERMITTENT COLICKY"))
    def INTERMITTENT_COLICKY(self):
        self.declare(Fact(ask="Examination"))

    @ Rule(Answer(subject='Pain Location', text="LOWER QUADRANT"))
    def LOWER_QUADRANT(self):
        self.considerations([
            'APPENDICITIS SALPINGITIS', 'ECTOPIC PREGNANCY', 'DIVERTICULITIS'
        ])
        self.halt()

    @ Rule(Answer(subject='Pain Location', text="RIGHT UPPER QUADRANT"))
    def RIGHT_UPPER_QUADRANT(self):
        self.considerations(['ACUTE CHOLECYSTITIS'])
        self.ensurance_actions(["ULTRASOUND", "HIDASCAN"])
        self.halt()

    @ Rule(Answer(subject='Pain Location', text="GENERALIZED WITH REBOUND TENDERNESS"))
    def GENERALIZED_WITH_REBOUND_TENDERNESS(self):
        self.considerations(['SHOCK'])
        self.ensurance_actions(["SERUM AMYLASE"])
        self.halt()

    @ Rule(Answer(subject='Examination', text="FLANK or HEMATURIA"))
    def FLANK_or_HEMATURIA(self):
        self.considerations(['NEPHROLITHIASIS'])
        self.ensurance_actions(["INTRAVENOUS PYELOGRAM", "CTSCAN"])
        self.halt()

    @ Rule(Answer(subject='Examination', text="HYPERACTIVE BOWEL SOUNDS and TYMPANY"))
    def HYPERACTIVE_BOWEL_SOUNDS_and_TYMPANY(self):
        self.considerations(['INTESTINAL OBSTRUCTION'])
        self.ensurance_actions(["FLAT PLATE OF ABDOMEN"])
        self.halt()

    @ Rule(Answer(subject='Examination', text="RIGHT UPPER QUADRANT"))
    def RIGHT_UPPER_QUADRANT_examination(self):
        self.considerations(['CHOLELITHIASIS', 'CHOLEDOCHOLITHIASIS'])
        self.ensurance_actions(["ULTRASOUND OF GALLBLADDER", "HIDA SCAN"])
        self.halt()

# ap = AbdominalPain()
# ap.reset()
# ap.run()
