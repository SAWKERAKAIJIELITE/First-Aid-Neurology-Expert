from experta import *
from experta.utils import unfreeze
from schema import Schema, And, Use, Const, Or
from Anixety import Anixety
from AbsentOrDiminishedPulse import AbsentOrDiminishedPulse
from Blindness import BLINDNESS
from Hematuria import Hematuria
from AcuteFever import AcuteFever
from AcidBaseAnalysis import AcidBaseAnalysis


class Question(Fact):
    subject = text = Field(str, True)
    Type = Field(Or('multiple', 'single', 'bool', 'int', 'words'), True)
    valid = Field(Or(list, int))


class Answer(Fact):
    subject = Field(str, True)
    text = Field(Or(str, bool, int, list), True)


class FirstAid(KnowledgeEngine):

    # @staticmethod
    # def recommend_action(action):
    #     print(f"I recommend you to {action}")

    # @staticmethod
    # def considerations(action):
    #     print(f"Consider to: {action}")

    # @staticmethod
    # def ask_user(question):
    #     print(question['text'])
    #     if question['Type'] == 'single':
    #         print("Valid answers are ")
    #         i = 0
    #         for item in question['valid']:
    #             i += 1
    #             print(f"    {i}. {item}")
    #         return question['valid'][int(input())-1]

    #     if question['Type'] == 'multiple':
    #         print("Valid answers are ")
    #         i = 0
    #         for item in question['valid']:
    #             i += 1
    #             print(f"    {i}. {item}")
    #         print("You can select multiple choice seperated by space")

    #         l = input().split()
    #         q = []
    #         for item in l:
    #             q.append(question['valid'][int(item)])
    #         return q

    #     if question['Type'] == 'bool':
    #         return bool(input())

    #     if question['Type'] == 'int':
    #         return int(input())

    #     if question['Type'] == 'words':
    #         return input()

    # @DefFacts()
    # def init(self):
    #     pass

    # @Rule(
    #     NOT(Answer(subject='Anixety')),
    #     NOT(Fact(ask='Anixety'))
    # )
    # def ask_about_anixety(self):
    #     anixety = Anixety()
    #     anixety.reset()
    #     anixety.run()
    #     self.halt()

    # @Rule(
    #     NOT(Answer(subject='ABSENT OR DIMINISHED PULSE')),
    #     NOT(Fact(ask='ABSENT OR DIMINISHED PULSE'))
    # )
    # def ask_about_extremities(self):
    #     pulse = AbsentOrDiminishedPulse()
    #     pulse.reset()
    #     pulse.run()
    #     self.halt()

    @Rule(
        NOT(Answer(subject='BLINDNESS')),
        NOT(Fact(ask='BLINDNESS'))
    )
    def ask_about_blindness(self):
        blindness = BLINDNESS()
        blindness.reset()
        blindness.run()
        # self.halt()

    @Rule(
        NOT(Answer(subject='Hematuria')),
        NOT(Fact(ask='Hematuria'))
    )
    def ask_about_hematuria(self):
        hematuria = Hematuria()
        hematuria.reset()
        hematuria.run()
        # print(hematuria.get_activations())
        # self.halt()

    @Rule(
        NOT(Answer(subject='ACUTE FEVER')),
        NOT(Fact(ask='ACUTE FEVER'))
    )
    def ask_about_ACUTE_FEVER(self):
        acute_fever = AcuteFever()
        acute_fever.reset()
        acute_fever.run()
        # print("lldldl")
        # self.halt()

    # @Rule(
    #     NOT(Answer(subject='PH')),
    #     NOT(Fact(ask='PH'))
    # )
    # def ask_about_ph(self):
    #     acid_base_analysis = AcidBaseAnalysis()
    #     acid_base_analysis.reset()
    #     acid_base_analysis.run()
    #     self.halt()


watch('AGENDA', 'ACTIVATIONS')
fa = FirstAid()
fa.reset()
fa.run()
