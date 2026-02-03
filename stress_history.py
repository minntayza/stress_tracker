import json
import os
from datetime import datetime

class StressHistory:
    def __init__(self, user_id=None, history_file=None):
        """
        Initialize StressHistory with user-specific or custom history file.
        
        Args:
            user_id: User ID for multi-user support. If provided, file will be history_{user_id}.json
            history_file: Custom history file path. Overrides user_id if both provided.
        """
        if history_file:
            self.history_file = history_file
        elif user_id:
            self.history_file = f'history_{user_id}.json'
        else:
            self.history_file = 'history.json'  # Fallback for backward compatibility
        
        self.history = self.load_history()

    def load_history(self):
        """Load history from JSON file. Create if not exists."""
        if not os.path.exists(self.history_file):
            return []
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def save_entry(self, stress_score, recommendation, status="Unknown"):
        """
        Save a new entry to the history.
        :param stress_score: float
        :param recommendation: str
        :param status: str (e.g. "Healing Phase", "Relapse", "Initial")
        """
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stress_score": float(stress_score),
            "recommendation": recommendation,
            "status": status
        }
        self.history.append(entry)
        self.save_history()

    def save_history(self):
        """Write current history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def check_healing_status(self, current_score):
        """
        Compare current score with the last entry to determine status.
        Returns: "Healing Phase", "Relapse", "Stagnant", or "Initial"
        """
        if not self.history:
            return "Initial"

        last_entry = self.history[-1]
        previous_score = last_entry.get("stress_score", 0)
        
        # Determine status
        if current_score < previous_score:
            return "Healing Phase"
        elif current_score > previous_score:
            return "Relapse"
        else:
            return "Stagnant"

    def get_last_recommendation(self):
        if not self.history:
            return None
        return self.history[-1].get("recommendation")

    def find_effective_strategies(self):
        """
        Identify strategies that led to a Healing Phase.
        Returns: str (most recent effective strategy) or None
        """
        if len(self.history) < 2:
            return None

        # Iterate backwards to find the most recent success first
        for i in range(len(self.history) - 1, 0, -1):
            entry = self.history[i]
            prev_entry = self.history[i-1]
            
            if entry.get("status") == "Healing Phase":
                # The recommendation from the PREVIOUS entry is what helped
                return prev_entry.get("recommendation")
        
        return None

if __name__ == "__main__":
    # Test script
    print("Initializing StressHistory...")
    # Use a temp file for testing to avoid messing up real history if it existed
    history_manager = StressHistory("test_history.json")
    
    # Clear test file
    if os.path.exists("test_history.json"):
        os.remove("test_history.json")
        history_manager = StressHistory("test_history.json")

    print("- Test 1: No history")
    status = history_manager.check_healing_status(85)
    print(f"  Status: {status} (Expected: Initial)")
    history_manager.save_entry(85, "Sleep More", status)

    print("- Test 2: Improvement (85 -> 55)")
    status = history_manager.check_healing_status(55)
    print(f"  Status: {status} (Expected: Healing Phase)")
    history_manager.save_entry(55, "Continue Sleeping", status)

    print("- Test 3: Relapse (55 -> 70)")
    status = history_manager.check_healing_status(70)
    print(f"  Status: {status} (Expected: Relapse)")
    history_manager.save_entry(70, "Reduce Study Load", status)
    
    # Clean up
    if os.path.exists("test_history.json"):
        os.remove("test_history.json")
    print("\nTests Completed.")
