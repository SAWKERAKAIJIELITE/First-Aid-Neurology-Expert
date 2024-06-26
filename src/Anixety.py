from experta import *
from schema import Or


class Question(Fact):
    subject = text = Field(str, True)
    Type = Field(Or('multiple', 'single', 'bool', 'int', 'words'), True)
    valid = Field(Or(list, int))


class Answer(Fact):
    subject = Field(str, True)
    text = Field(Or(str, bool, int, list), True)


class Anixety(KnowledgeEngine):

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
            return bool(input())

        if question['Type'] == 'int':
            return int(input())

        if question['Type'] == 'words':
            return input()

    @DefFacts()
    def init(self):

        yield Question(
            subject="Anixety",
            Type="bool",
            text="Is Anixety Constant?"
        )
        yield Question(
            subject="Age",
            Type="int",
            text="How old are you?"
        )
        yield Question(
            subject="TACHYCARDIA",
            Type="bool",
            text="is there TACHYCARDIA?"
        )
        yield Question(
            subject="DISAPPEARING DURING SLEEP",
            Type="bool",
            text="Does it disappear during sleep?"
        )
        yield Question(
            subject="WEIGHT LOSS",
            Type="bool",
            text="Do you notice any WEIGHT LOSS?"
        )

    @Rule(
        NOT(Answer(subject='Anixety')),
        NOT(Fact(ask='Anixety'))
    )
    def ask_about_anixety(self):
        self.declare(Fact(ask="Anixety"))

    @Rule(
        AS.question << Question(subject=MATCH.subject),
        NOT(Answer(subject=MATCH.subject)),
        AS.ask << Fact(ask=MATCH.subject)
    )
    def ask_Question_by_subject(self, question, ask, subject):
        self.retract(ask)
        answer = self.ask_user(question)
        self.declare(Answer(subject=subject, text=answer))

    @Rule(Answer(subject='Anixety', text=False))
    def anixety_not_constant(self):
        self.considerations([
            'INSULINOMA', ' PHEOCHROMOCYTOMA PSYCHOMOTOR', 'EPILEPSY'
        ])
        self.halt()

    @Rule(Answer(subject='Anixety', text=True))
    def anixety_constant(self):
        self.declare(Fact(ask="Age"))

    @Rule(Answer(subject='Age', text=GE(60)))
    def older_than_sixty(self):
        self.considerations([
            'CEREBRAL ARTERIOSCLEROSIS', ' DEMENTIA', 'ANXIETY NEUROSIS', 'DEPRESSION'
        ])
        self.halt()

    @Rule(Answer(subject='Age', text=LT(60) & GT(12)))
    def younger_than_sixty(self):
        self.declare(Fact(ask="TACHYCARDIA"))

    @Rule(Answer(subject='TACHYCARDIA', text=False))
    def there_is_not_TACHYCARDIA(self):
        self.considerations(['ANXIETY NEUROSIS', 'DEPRESSION'])
        self.halt()

    @Rule(Answer(subject='TACHYCARDIA', text=True))
    def there_is_TACHYCARDIA(self):
        self.declare(Fact(ask="DISAPPEARING DURING SLEEP"))

    @Rule(Answer(subject='DISAPPEARING DURING SLEEP', text=True))
    def DISAPPEARING_DURING_SLEEP(self):
        self.considerations([
            'ANXIETY NEUROSIS', 'DEPRESSION', 'SCHIZOPHRENIA', "DACOSTA'S SYNDROME"
        ])
        self.halt()

    @Rule(Answer(subject='TACHYCARDIA', text=True))
    def APPEARING_DURING_SLEEP(self):
        self.declare(Fact(ask="WEIGHT LOSS"))

    @Rule(Answer(subject='WEIGHT LOSS', text=True))
    def WEIGHT_LOSS(self):
        self.considerations(['HYPERTHYROIDISM'])
        self.halt()

    @Rule(Answer(subject='WEIGHT LOSS', text=False))
    def WEIGHT_not_LOSS(self):
        self.considerations([
            'CAFFEINE OR OTHER DRUG INGESTION', 'CARDIAC ARRHYTHMIA'
        ])
        self.halt()
