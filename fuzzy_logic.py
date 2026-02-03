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

        self.stress = ctrl.Consequent(np.arange(0, 101, 1), 'stress')

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

        self.stress['low'] = fuzz.trimf(self.stress.universe, [0, 0, 40])
        self.stress['moderate'] = fuzz.trimf(self.stress.universe, [30, 50, 70])
        self.stress['high'] = fuzz.trimf(self.stress.universe, [60, 100, 100])

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

        self.stress_ctrl = ctrl.ControlSystem([
            self.rule1, self.rule2, self.rule3, 
            self.rule_st1, self.rule_st2, self.rule_st3,
            self.rule4, self.rule5, self.rule6, self.rule7, self.rule8
        ])
        self.stress_simulation = ctrl.ControlSystemSimulation(self.stress_ctrl)

    def compute_stress(self, sleep_hours, study_hours, mood=5, deadline_level=0, activity_level=0, screen_time_hours=0):
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

        self.stress_simulation.input['sleep'] = sleep_hours
        self.stress_simulation.input['study'] = study_hours
        self.stress_simulation.input['mood'] = mood
        self.stress_simulation.input['deadline'] = deadline_level
        self.stress_simulation.input['activity'] = activity_level
        self.stress_simulation.input['screen_time'] = screen_time_hours

        try:
            self.stress_simulation.compute()
            return self.stress_simulation.output['stress']
        except Exception as e:
            print(f"Error computing stress: {e}")
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

