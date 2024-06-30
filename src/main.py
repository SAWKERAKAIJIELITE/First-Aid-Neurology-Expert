from experta import *
from experta.utils import unfreeze
from schema import Schema, And, Use, Const, Or
from AbdominalPain import AbdominalPain
from AbsentOrDiminishedPulse import AbsentOrDiminishedPulse
from AcidBaseAnalysis import AcidBaseAnalysis
from AcuteFever import AcuteFever
from Anixety import Anixety
from Blindness import BLINDNESS
from ChestPain import ChestPain
from Headache import Headache
from Hematuria import Hematuria


class Question(Fact):
    subject = text = Field(str, True)
    Type = Field(Or('multiple', 'single', 'bool', 'int', 'words'), True)
    valid = Field(Or(list, int))


class Answer(Fact):
    subject = Field(str, True)
    text = Field(Or(str, bool, int, list), True)


class FirstAid(KnowledgeEngine):

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

            x = input()
            if len(x) == 1:
                return [question['valid'][int(x)-1]]
            else:
                q = []
                for item in x.split():
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
            subject="Sick complaint",
            Type="multiple",
            valid=[
                "Abdominal Pain",
                "Absent Or Diminished Pulse",
                "Acid Base Analysis",
                "Acute Fever",
                "Anixety",
                "Blindness",
                "Chest Pain",
                "Headache",
                "Hematuria"
            ],
            text="What is your Sick complaint?"
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
        NOT(Answer(subject='Sick complaint')),
        NOT(Fact(ask='Sick complaint'))
    )
    def ask_about_Sick_complaint(self):
        self.declare(Fact(ask="Sick complaint"))

    @Rule(Answer(subject='Sick complaint', text=MATCH.t))
    def sick_complaint(self, t):
        for item in t:
            if item == "Chest Pain":
                self.declare(Answer(subject="Chest Pain", text="Chest Pain"))

            if item == "Headache":
                self.declare(Answer(subject="Headache", text="Headache"))

            if item == "Abdominal Pain":
                self.declare(
                    Answer(subject="Abdominal Pain", text="Abdominal Pain")
                )

            if item == "Absent Or Diminished Pulse":
                self.declare(
                    Answer(subject="Absent Or Diminished Pulse", text="Absent Or Diminished Pulse"))

            if item == "Hematuria":
                self.declare(Answer(subject="Hematuria", text="Hematuria"))

            if item == "Blindness":
                self.declare(Answer(subject="Blindness", text="Blindness"))

            if item == "Anixety":
                self.declare(Answer(subject="Anixety", text="Anixety"))

            if item == "Acute Fever":
                self.declare(Answer(subject="Acute Fever", text="Acute Fever"))

            if item == "Acid Base Analysis":
                self.declare(
                    Answer(subject="Acid Base Analysis", text="Acid Base Analysis"))

    @Rule(Answer(subject='Anixety'))
    def ask_about_anixety(self):
        print("Anixety")
        anixety = Anixety()
        anixety.reset()
        anixety.run()

    @Rule(Answer(subject='Abdominal Pain'))
    def ask_about_Abdominal_Pain(self):
        print("Abdominal Pain")
        abdominal_pain = AbdominalPain()
        abdominal_pain.reset()
        abdominal_pain.run()

    @Rule(Answer(subject='Chest Pain'))
    def ask_about_Chest_Pain(self):
        print("Chest Pain")
        chest_pain = ChestPain()
        chest_pain.reset()
        chest_pain.run()

    @Rule(Answer(subject='Headache'))
    def ask_about_Headache(self):
        print("Headache")
        headache = Headache()
        headache.reset()
        headache.run()

    @Rule(Answer(subject='Absent Or Diminished Pulse'))
    def ask_about_extremities(self):
        print("Absent Or Diminished Pulse")
        pulse = AbsentOrDiminishedPulse()
        pulse.reset()
        pulse.run()

    @Rule(Answer(subject='Blindness'))
    def ask_about_blindness(self):
        print("Blindness")
        blindness = BLINDNESS()
        blindness.reset()
        blindness.run()

    @Rule(Answer(subject='Hematuria'))
    def ask_about_hematuria(self):
        print("Hematuria")
        hematuria = Hematuria()
        hematuria.reset()
        hematuria.run()
        # print(hematuria.get_activations())

    @Rule(Answer(subject='Acute Fever'))
    def ask_about_ACUTE_FEVER(self):
        print("ACUTE FEVER")
        acute_fever = AcuteFever()
        acute_fever.reset()
        acute_fever.run()
        # print("lldldl")

    @Rule(Answer(subject='Acid Base Analysis'))
    def ask_about_Acid_Base_Analysis(self):
        print("Acid Base Analysis")
        acid_base_analysis = AcidBaseAnalysis()
        acid_base_analysis.reset()
        acid_base_analysis.run()


# watch('AGENDA', 'ACTIVATIONS')
fa = FirstAid()
fa.reset()
fa.run()
