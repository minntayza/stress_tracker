
import json
import os
from stress_history import StressHistory

# 1. Clear existing history
if os.path.exists('stress_history.json'):
    os.remove('stress_history.json')

history = StressHistory()

# 2. Add Entry 1: High Stress
history.save_entry(85, "High stress. RECOMMENDATION_A: Go for a run.", "Relapse")
print("Added Entry 1: High Stress")

# 3. Add Entry 2: Low Stress (Healing Phase)
# The logic checks if Current < Previous by 10 points. 50 < 85, so it's Healing.
# This means RECOMMENDATION_A was effective.
history.save_entry(50, "Low stress.", "Healing Phase")
print("Added Entry 2: Healing Phase")

# 4. Verify find_effective_strategies
effective = history.find_effective_strategies()
print(f"Effective Strategy Found: {effective}")

assert effective == "High stress. RECOMMENDATION_A: Go for a run."
print("TEST PASSED: Correctly identified effective strategy.")
