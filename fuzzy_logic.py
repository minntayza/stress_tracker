import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class StressFuzzySystem:
    def __init__(self):
        self.sleep = ctrl.Antecedent(np.arange(0, 13, 1), 'sleep')
        self.study = ctrl.Antecedent(np.arange(0, 17, 1), 'study')
        # New Antecedents
        self.screen_time = ctrl.Antecedent(np.arange(0, 25, 1), 'screen_time') # 0-24 hours
        self.mood = ctrl.Antecedent(np.arange(1, 11, 1), 'mood')
        self.deadline = ctrl.Antecedent(np.arange(0, 11, 1), 'deadline') # 0-10 scale
        self.activity = ctrl.Antecedent(np.arange(0, 11, 1), 'activity') # 0-10 scale
        self.social = ctrl.Antecedent(np.arange(0, 11, 1), 'social') # 0-10 scale
        self.procrastination = ctrl.Antecedent(np.arange(0, 11, 1), 'procrastination') # 0-10 scale
        self.financial = ctrl.Antecedent(np.arange(0, 11, 1), 'financial') # 0-10 scale
        self.age = ctrl.Antecedent(np.arange(10, 81, 1), 'age') # 10-80 years
        self.quiz = ctrl.Antecedent(np.arange(0, 101, 1), 'quiz') # 0-100 stress quiz score

        self.stress = ctrl.Consequent(np.arange(0, 101, 1), 'stress')
        self.instability = ctrl.Consequent(np.arange(0, 101, 1), 'instability')

        # Define membership functions
        # Sleep
        self.sleep['poor'] = fuzz.trimf(self.sleep.universe, [0, 0, 6])
        self.sleep['average'] = fuzz.trimf(self.sleep.universe, [4, 7, 9])
        self.sleep['good'] = fuzz.trimf(self.sleep.universe, [7, 12, 12])

        # Study
        self.study['low'] = fuzz.trimf(self.study.universe, [0, 0, 5])
        self.study['moderate'] = fuzz.trimf(self.study.universe, [4, 8, 12])
        self.study['high'] = fuzz.trimf(self.study.universe, [10, 16, 16])

        # Screen Time (0-24)
        self.screen_time['low'] = fuzz.trimf(self.screen_time.universe, [0, 0, 4])
        self.screen_time['moderate'] = fuzz.trimf(self.screen_time.universe, [3, 6, 9])
        self.screen_time['high'] = fuzz.trimf(self.screen_time.universe, [7, 24, 24])

        # Mood (1=Sad, 10=Happy)
        self.mood['low'] = fuzz.trimf(self.mood.universe, [1, 1, 4])
        self.mood['neutral'] = fuzz.trimf(self.mood.universe, [3, 5, 8])
        self.mood['high'] = fuzz.trimf(self.mood.universe, [6, 10, 10])

        # Deadline (0=None, 5=Upcoming, 10=Urgent)
        self.deadline['none'] = fuzz.trimf(self.deadline.universe, [0, 0, 3])
        self.deadline['upcoming'] = fuzz.trimf(self.deadline.universe, [2, 5, 8])
        self.deadline['urgent'] = fuzz.trimf(self.deadline.universe, [7, 10, 10])

        # Activity (0=Sedentary, 5=Moderate, 10=Intense)
        self.activity['low'] = fuzz.trimf(self.activity.universe, [0, 0, 4])
        self.activity['moderate'] = fuzz.trimf(self.activity.universe, [3, 6, 9])
        self.activity['high'] = fuzz.trimf(self.activity.universe, [7, 10, 10])

        # Social Interaction (0=Isolated, 10=Very Social)
        self.social['low'] = fuzz.trimf(self.social.universe, [0, 0, 4])
        self.social['moderate'] = fuzz.trimf(self.social.universe, [3, 5, 7])
        self.social['high'] = fuzz.trimf(self.social.universe, [6, 10, 10])

        # Procrastination (0=Low, 10=High)
        self.procrastination['low'] = fuzz.trimf(self.procrastination.universe, [0, 0, 4])
        self.procrastination['medium'] = fuzz.trimf(self.procrastination.universe, [3, 5, 7])
        self.procrastination['high'] = fuzz.trimf(self.procrastination.universe, [6, 10, 10])

        # Financial Stress (0=None, 10=Severe)
        self.financial['low'] = fuzz.trimf(self.financial.universe, [0, 0, 4])
        self.financial['moderate'] = fuzz.trimf(self.financial.universe, [3, 5, 7])
        self.financial['high'] = fuzz.trimf(self.financial.universe, [6, 10, 10])

        # Age (10-80)
        self.age['young'] = fuzz.trimf(self.age.universe, [10, 10, 25])
        self.age['adult'] = fuzz.trimf(self.age.universe, [20, 35, 50])
        self.age['older'] = fuzz.trimf(self.age.universe, [45, 80, 80])

        self.stress['low'] = fuzz.trimf(self.stress.universe, [0, 0, 40])
        self.stress['moderate'] = fuzz.trimf(self.stress.universe, [30, 50, 70])
        self.stress['high'] = fuzz.trimf(self.stress.universe, [60, 100, 100])

        self.instability['low'] = fuzz.trimf(self.instability.universe, [0, 0, 40])
        self.instability['moderate'] = fuzz.trimf(self.instability.universe, [30, 50, 70])
        self.instability['high'] = fuzz.trimf(self.instability.universe, [60, 100, 100])

        self.quiz['low'] = fuzz.trimf(self.quiz.universe, [0, 0, 40])
        self.quiz['moderate'] = fuzz.trimf(self.quiz.universe, [30, 50, 70])
        self.quiz['high'] = fuzz.trimf(self.quiz.universe, [60, 100, 100])

        # Define rules
        # 1. Base Rules
        self.rule1 = ctrl.Rule(self.sleep['poor'] | self.study['high'], self.stress['high'])
        self.rule2 = ctrl.Rule(self.sleep['good'] & self.study['low'], self.stress['low'])
        self.rule3 = ctrl.Rule(self.sleep['average'] & self.study['moderate'], self.stress['moderate'])

        # 2. New Factor Rules
        # Screen Time Rules
        self.rule_st1 = ctrl.Rule(self.screen_time['high'], self.stress['high']) # High screen time increases stress
        self.rule_st2 = ctrl.Rule(self.screen_time['high'] & self.sleep['poor'], self.stress['high']) # Dual impact
        self.rule_st3 = ctrl.Rule(self.screen_time['low'], self.stress['low']) # Low screen time helps

        # Urgent deadline significantly increases stress
        self.rule4 = ctrl.Rule(self.deadline['urgent'], self.stress['high'])
        
        # Low mood increases stress perception
        self.rule5 = ctrl.Rule(self.mood['low'], self.stress['high'])
        
        # High activity helps reduce stress even if study is moderate
        self.rule6 = ctrl.Rule(self.activity['high'] & self.study['moderate'], self.stress['low'])

        # Good mood and moderate activity can buffer stress
        self.rule7 = ctrl.Rule(self.mood['high'] & self.activity['moderate'], self.stress['low'])
        
        # Combined Negative: Low mood + Urgent deadline = High Stress
        self.rule8 = ctrl.Rule(self.mood['low'] & self.deadline['upcoming'], self.stress['high'])

        # New Factor Rules
        self.rule9 = ctrl.Rule(self.social['low'] | self.financial['high'] | self.procrastination['high'], self.stress['high'])
        self.rule10 = ctrl.Rule(self.social['high'] & self.financial['low'] & self.procrastination['low'], self.stress['low'])
        self.rule11 = ctrl.Rule(self.financial['moderate'] & self.procrastination['medium'], self.stress['moderate'])
        self.rule12 = ctrl.Rule(self.age['young'] & self.study['high'], self.stress['high'])
        self.rule13 = ctrl.Rule(self.age['older'] & self.deadline['urgent'], self.stress['high'])
        self.rule14 = ctrl.Rule(self.quiz['high'], self.stress['high'])
        self.rule15 = ctrl.Rule(self.quiz['low'], self.stress['low'])
        self.rule16 = ctrl.Rule(self.quiz['moderate'], self.stress['moderate'])
        self.rule17 = ctrl.Rule(self.quiz['high'] & self.sleep['poor'], self.stress['high'])

        self.stress_ctrl = ctrl.ControlSystem([
            self.rule1, self.rule2, self.rule3, 
            self.rule_st1, self.rule_st2, self.rule_st3,
            self.rule4, self.rule5, self.rule6, self.rule7, self.rule8,
            self.rule9, self.rule10, self.rule11, self.rule12, self.rule13,
            self.rule14, self.rule15, self.rule16, self.rule17
        ])
        self.stress_simulation = ctrl.ControlSystemSimulation(self.stress_ctrl)

        # Lifestyle Instability Rules (Output C)
        self.inst_rule1 = ctrl.Rule(self.financial['high'] | self.procrastination['high'] | self.social['low'], self.instability['high'])
        self.inst_rule2 = ctrl.Rule(self.financial['moderate'] & self.procrastination['medium'], self.instability['moderate'])
        self.inst_rule3 = ctrl.Rule(self.financial['low'] & self.procrastination['low'] & self.social['high'], self.instability['low'])
        self.inst_rule4 = ctrl.Rule(self.financial['high'] & self.social['low'], self.instability['high'])
        self.inst_rule5 = ctrl.Rule(self.procrastination['high'] & self.social['low'], self.instability['high'])
        self.inst_rule6 = ctrl.Rule(self.age['young'] & self.procrastination['high'], self.instability['high'])

        self.instability_ctrl = ctrl.ControlSystem([
            self.inst_rule1, self.inst_rule2, self.inst_rule3,
            self.inst_rule4, self.inst_rule5, self.inst_rule6
        ])
        self.instability_simulation = ctrl.ControlSystemSimulation(self.instability_ctrl)

    def compute_stress(self, sleep_hours, study_hours, mood=5, deadline_level=0, activity_level=0, screen_time_hours=0,
                       social_interaction=5, procrastination_level=5, financial_stress=5, age=30, quiz_score=50):
        """
        Compute stress level based on all factors.
        """
        # Clamp inputs
        sleep_hours = max(0, min(12, sleep_hours))
        study_hours = max(0, min(16, study_hours))
        mood = max(1, min(10, mood))
        deadline_level = max(0, min(10, deadline_level))
        activity_level = max(0, min(10, activity_level))
        screen_time_hours = max(0, min(24, screen_time_hours))
        social_interaction = max(0, min(10, social_interaction))
        procrastination_level = max(0, min(10, procrastination_level))
        financial_stress = max(0, min(10, financial_stress))
        age = max(10, min(80, age))
        quiz_score = max(0, min(100, quiz_score))

        self.stress_simulation.input['sleep'] = sleep_hours
        self.stress_simulation.input['study'] = study_hours
        self.stress_simulation.input['mood'] = mood
        self.stress_simulation.input['deadline'] = deadline_level
        self.stress_simulation.input['activity'] = activity_level
        self.stress_simulation.input['screen_time'] = screen_time_hours
        self.stress_simulation.input['social'] = social_interaction
        self.stress_simulation.input['procrastination'] = procrastination_level
        self.stress_simulation.input['financial'] = financial_stress
        self.stress_simulation.input['age'] = age
        self.stress_simulation.input['quiz'] = quiz_score

        try:
            self.stress_simulation.compute()
            return self.stress_simulation.output['stress']
        except Exception as e:
            print(f"Error computing stress: {e}")
            return 50.0

    def compute_instability(self, social_interaction=5, procrastination_level=5, financial_stress=5, age=30):
        """
        Compute lifestyle instability (Output C) based on lifestyle factors.
        """
        social_interaction = max(0, min(10, social_interaction))
        procrastination_level = max(0, min(10, procrastination_level))
        financial_stress = max(0, min(10, financial_stress))
        age = max(10, min(80, age))

        self.instability_simulation.input['social'] = social_interaction
        self.instability_simulation.input['procrastination'] = procrastination_level
        self.instability_simulation.input['financial'] = financial_stress
        self.instability_simulation.input['age'] = age

        try:
            self.instability_simulation.compute()
            return self.instability_simulation.output['instability']
        except Exception as e:
            print(f"Error computing instability: {e}")
            return 50.0

if __name__ == "__main__":
    # Simple verification
    system = StressFuzzySystem()
    
    test_cases = [
        (4, 10),  # Poor Sleep, High Study -> Expect High
        (9, 3),   # Good Sleep, Low Study -> Expect Low
        (7, 8),   # Average Sleep, Moderate Study -> Expect Moderate/Low
        (2, 2),   # Poor Sleep, Low Study -> Expect High (due to sleep)
        (10, 14)  # Good Sleep, High Study -> Expect High (due to study)
    ]
    
    print("Verifying Intelligent Adaptive Stress System (Phase 1)...")
    for sleep, study in test_cases:
        stress = system.compute_stress(sleep, study)
        print(f"Sleep: {sleep}h, Study: {study}h -> Stress: {stress:.2f}")
