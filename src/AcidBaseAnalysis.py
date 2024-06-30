from experta import *
from schema import Or


class Question(Fact):
    subject = text = Field(str, True)
    Type = Field(Or('multiple', 'single', 'bool', 'int', 'words'), True)
    valid = Field(Or(list, int))
    certainity_factor = Field(float)


class Answer(Fact):
    subject = Field(str, True)
    text = Field(Or(str, bool, int, float, list), True)
    certainity_factor = Field(float)


class AcidBaseAnalysis(KnowledgeEngine):

    @staticmethod
    def recommend_action(action):
        print(f"I recommend you to {action}")

    @staticmethod
    def considerations(action, certainity_factor: float = 0):
        print(f"Consider to: {action}", end='')
        if certainity_factor != 0:
            print(f" with probability factor of {certainity_factor}")

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
                q.append(question['valid'][int(item)])
            return q

        if question['Type'] == 'bool':
            print("Press Enter to choose False or any other key to choose True")
            return bool(input())

        if question['Type'] == 'int':
            return float(input())

        if question['Type'] == 'words':
            return input()

    @DefFacts()
    def init(self):

        yield Question(
            subject="PH",
            Type="int",
            text="Enter PH"
        )
        yield Question(
            subject="HCO3",
            Type="int",
            text="Enter HCO3"
        )
        yield Question(
            subject="PCO2",
            Type="int",
            text="Enter PCO2"
        )
        yield Question(
            subject="Na",
            Type="int",
            text="Enter Na (Sodieum)"
        )
        yield Question(
            subject="Cl",
            Type="int",
            text="Enter Cl (Cloride)"
        )
        yield Question(
            subject="Albumin",
            Type="int",
            text="Enter Albumin"
        )

    @Rule(
        NOT(Answer(subject='PH')),
        NOT(Fact(ask='PH'))
    )
    def ask_about_CHEST_PAIN(self):
        self.declare(Fact(ask='PH'))

    @Rule(
        AS.question << Question(subject=MATCH.subject),
        NOT(Answer(subject=MATCH.subject)),
        AS.ask << Fact(ask=MATCH.subject)
    )
    def ask_Question_by_subject(self, question, ask, subject):
        self.retract(ask)
        answer = self.ask_user(question)
        self.declare(Answer(subject=subject, text=answer))

    @Rule(Answer(subject='PH', text=~BETWEEN(6, 8.5)))
    def not_valid_ph(self):
        raise ValueError("PH is out of range")

    @Rule(Answer(subject='PH', text=BETWEEN(6, 8.5)))
    def valid_ph(self):
        self.declare(*[
            Fact(ask=a)for a in ['HCO3', 'PCO2', 'Na', 'Cl', 'Albumin']
        ])

    @Rule(
        Answer(subject='PH', text=BETWEEN(7.35, 7.45)),
        Answer(subject='HCO3', text=BETWEEN(22, 26)),
        Answer(subject='PCO2', text=BETWEEN(35, 45)),
    )
    def healthy_ph_hco3_pco2(self):
        print("Your are healthy")
        self.halt()

    @Rule(
        Answer(subject='PH', text=BETWEEN(7.35, 7.45)),
        Answer(subject='HCO3', text=LT(22)),
        Answer(subject='PCO2', text=BETWEEN(35, 45)),
    )
    def healthy_ph_lt_hco3_pco2(self):
        self.considerations(['Metabolic Acidemia'])
        self.halt()

    @Rule(
        Answer(subject='PH', text=BETWEEN(7.35, 7.45)),
        Answer(subject='HCO3', text=GT(26)),
        Answer(subject='PCO2', text=BETWEEN(35, 45)),
    )
    def healthy_ph_gt_hco3_pco2(self):
        self.considerations(['Metabolic Alkalemia'])
        self.halt()

    @Rule(
        Answer(subject='PH', text=BETWEEN(7.35, 7.45)),
        Answer(subject='HCO3', text=BETWEEN(22, 26)),
        Answer(subject='PCO2', text=LT(35))
    )
    def healthy_ph_hco3_lt_pco2(self):
        self.considerations(['Respiratory Alkalemia'])
        self.halt()

    @Rule(
        Answer(subject='PH', text=BETWEEN(7.35, 7.45)),
        Answer(subject='HCO3', text=BETWEEN(22, 26)),
        Answer(subject='PCO2', text=GT(45))
    )
    def healthy_ph_hco3_gt_pco2(self):
        self.considerations(['Respiratory Acidemia'])
        self.halt()

    @Rule(
        Answer(subject='PH', text=BETWEEN(7.35, 7.45)),
        Answer(subject='HCO3', text=LT(22)),
        Answer(subject='PCO2', text=LT(45))
    )
    def acidemia(self):
        self.considerations(['Metabolic Acidemia AND Respiratory Acidemia'])
        self.halt()

    @Rule(
        Answer(subject='PH', text=BETWEEN(7.35, 7.45)),
        Answer(subject='HCO3', text=GT(26)),
        Answer(subject='PCO2', text=GT(35))
    )
    def alkalemia(self):
        self.considerations(['Metabolic Alkalemia AND Respiratory Alkalemia'])
        self.halt()

    @Rule(
        Answer(subject='PH', text=LT(7.35)),
        Answer(subject='HCO3', text=MATCH.h & LT(22)),
        Answer(subject='PCO2', text=BETWEEN(35, 45)),
        Answer(subject='Na', text=MATCH.na),
        Answer(subject='Cl', text=MATCH.cl),
        Answer(subject='Albumin', text=MATCH.albumin),
    )
    def lt_ph_lt_hco3_pco2(self, h, na, cl, albumin):
        self.considerations(['Metabolic Acidosis'])
        self.declare(Fact(HCO3=h, Na=na, Cl=cl, Albumin=albumin))
        # self.halt()

    @Rule(
        Answer(subject='PH', text=LT(7.35)),
        Answer(subject='HCO3', text=BETWEEN(22, 26)),
        Answer(subject='PCO2', text=MATCH.p & GT(45)),
    )
    def lt_ph_hco3_gt_pco2(self, p):
        self.considerations(['Respiratory Acidosis'])
        self.considerations(['COPD', 'Asthama', 'Medications'])
        self.declare(Fact(Respiratory=True, value=p))
        self.halt()

    @Rule(
        Answer(subject='PH', text=LT(7.35)),
        Answer(subject='HCO3', text=MATCH.h & LT(22)),
        Answer(subject='PCO2', text=MATCH.p & GT(45)),
        Answer(subject='Na', text=MATCH.na),
        Answer(subject='Cl', text=MATCH.cl),
        Answer(subject='Albumin', text=MATCH.albumin),
    )
    def lt_ph_lt_hco3_gt_pco2(self, h, p, na, cl, albumin):
        self.considerations(['Metabolic Acidosis AND Respiratory Acidosis'])
        self.considerations(['COPD', 'Asthama', 'Medications'])
        self.declare(Fact(HCO3=h, Na=na, Cl=cl, Albumin=albumin))
        self.declare(Fact(Respiratory=True, value=p))
        self.halt()

    @Rule(
        Answer(subject='PH', text=LT(7.35)),
        Answer(subject='HCO3', text=MATCH.h & LT(22)),
        Answer(subject='PCO2', text=MATCH.p & LT(35)),
        Answer(subject='Na', text=MATCH.na),
        Answer(subject='Cl', text=MATCH.cl),
        Answer(subject='Albumin', text=MATCH.albumin),

    )
    def lt_ph_lt_hco3_lt_pco2(self, h, p, na, cl, albumin):
        self.considerations([
            'Metabolic Acidosis WITH Respiratory Compensation'
        ])
        self.declare(Fact(HCO3=h, Na=na, Cl=cl, Albumin=albumin))
        self.declare(Fact(HCO3=h, PCO2=p))
        self.halt()

    @Rule(
        Answer(subject='PH', text=LT(7.35)),
        Answer(subject='HCO3', text=GT(26)),
        Answer(subject='PCO2', text=MATCH.p & GT(45)),
    )
    def lt_ph_gt_hco3_gt_pco2(self, p):
        self.considerations([
            'Respiratory Acidosis WITH Metabolic Compensation'
        ])
        self.considerations(['COPD', 'Asthama', 'Medications'])
        self.declare(Fact(Respiratory=True, value=p))
        self.halt()

    @Rule(
        Answer(subject='PH', text=GT(7.45)),
        Answer(subject='HCO3', text=MATCH.h & GT(26)),
        Answer(subject='PCO2', text=MATCH.p & GT(45)),
        Answer(subject='Na', text=MATCH.na),
        Answer(subject='Cl', text=MATCH.cl),
        Answer(subject='Albumin', text=MATCH.albumin),
    )
    def gt_ph_gt_hco3_gt_pco2(self, h, p, na, cl, albumin):
        self.considerations([
            'Metabolic Alkalosis WITH Respiratory Compensation'
        ])
        self.declare(Fact(HCO3=h, PCO2=p))
        self.considerations([
            'Laxative', 'Vomitting', 'Diarrhea', ' Post-hypercapnea', ' Licorice', 'Alkali Ingestion'
        ])
        self.declare(Fact(HCO3=h, Na=na, Cl=cl, Albumin=albumin))
        self.halt()

    @Rule(
        Answer(subject='PH', text=GT(7.45)),
        Answer(subject='HCO3', text=LT(22)),
        Answer(subject='PCO2', text=MATCH.p & LT(35)),
    )
    def gt_ph_lt_hco3_lt_pco2(self, p):
        self.considerations([
            'Respiratory Alkalosis WITH Metabolic Compensation'
        ])
        self.considerations(['Hypoxemia, Hepatic enceph, Pregnancy'])
        self.declare(Fact(Respiratory=True, value=p))
        self.halt()

    @Rule(
        Answer(subject='PH', text=GT(7.45)),
        Answer(subject='HCO3', text=MATCH.h & GT(26)),
        Answer(subject='PCO2', text=MATCH.p & LT(35)),
        Answer(subject='Na', text=MATCH.na),
        Answer(subject='Cl', text=MATCH.cl),
        Answer(subject='Albumin', text=MATCH.albumin),
    )
    def gt_ph_gt_hco3_lt_pco2(self, h, p, na, cl, albumin):
        self.considerations(['Respiratory Alkalosis AND Metabolic Alkalosis'])
        self.considerations(['Hypoxemia, Hepatic enceph, Pregnancy'])
        self.considerations([
            'Laxative', 'Vomitting', 'Diarrhea', ' Post-hypercapnea', ' Licorice', 'Alkali Ingestion'
        ])
        self.declare(Fact(HCO3=h, Na=na, Cl=cl, Albumin=albumin))
        self.declare(Fact(Respiratory=True, value=p))
        self.halt()

    @Rule(
        Answer(subject='PH', text=GT(7.45)),
        Answer(subject='HCO3', text=MATCH.h & GT(26)),
        Answer(subject='PCO2', text=BETWEEN(35, 45)),
        Answer(subject='Na', text=MATCH.na),
        Answer(subject='Cl', text=MATCH.cl),
        Answer(subject='Albumin', text=MATCH.albumin),

    )
    def gt_ph_gt_hco3_pco2(self, h, na, cl, albumin):
        self.considerations(['Metabolic Alkalosis'])
        self.considerations([
            'Laxative', 'Vomitting', 'Diarrhea', ' Post-hypercapnea', ' Licorice', 'Alkali Ingestion'
        ])
        self.declare(Fact(HCO3=h, Na=na, Cl=cl, Albumin=albumin))
        self.halt()

    @Rule(
        Answer(subject='PH', text=GT(7.45)),
        Answer(subject='HCO3', text=BETWEEN(22, 26)),
        Answer(subject='PCO2', text=MATCH.p & LT(35)),
    )
    def gt_ph_hco3_lt_pco2(self, p):
        self.considerations(['Respiratory Alkalosis'])
        self.considerations(['Hypoxemia, Hepatic enceph, Pregnancy'])
        self.declare(Fact(Respiratory=True, value=p))
        self.halt()

    @Rule(Fact(Respiratory=True, value=MATCH.p))
    def acute_or_chronic(self, p):
        a = 10*abs(p-40)/0.08
        c = 10*abs(p-40)/0.03
        result = "Acute" if p-a >= p-c else "Chronic"
        print(result)

    @Rule(Fact(HCO3=MATCH.h, PCO2=MATCH.p))
    def appropriate_respiratory_compensation(self, h, p):
        x = 1.5*h+8
        if not x-2 < p < x+2:
            print("this Respiratory Compensation is not Appropriate")
            print("Respiratory derangement")

    @Rule(Fact(HCO3=MATCH.h, Na=MATCH.na, Cl=MATCH.cl, Albumin=MATCH.albumin))
    def test_anion_gap(self, h, na, cl, albumin):
        AG = abs(na-(cl+h))
        EXP_AG = 2.5*albumin
        if AG > EXP_AG:
            self.declare(Fact(anion_gap=True))
        elif AG < EXP_AG:
            self.considerations([
                'Bromide or Iodine intoxication', ' Measure Aditional Cation(Ca, Mg, Li)'
            ])
        else:
            self.declare(Fact(anion_gap=False))
        x = abs(AG-EXP_AG)
        y = abs(h-24)
        z = x/y
        if z > 1.5:
            self.considerations(["Superimposed Metabolic Alkalosis"])
        elif z < 0.8:
            self.considerations([
                "Salicylate poisoning ", "DKA with Deyhadration"
            ])
        else:
            pass

    @Rule(Fact(anion_gap=True))
    def anion_gap(self):
        self.considerations([
            'Glycols', 'Oxoproline', 'Lactic Acid', 'Methanol'
        ])

    @Rule(Fact(anion_gap=False))
    def not_anion_gap(self):
        self.considerations(['Endocrine', 'Saline'])


# watch('AGENDA', 'ACTIVATIONS')
# aba = AcidBaseAnalysis()
# aba.reset()
# aba.run()
