import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

class StressVisualizer:
    def __init__(self):
        pass

    def generate_recovery_arc(self, history_data):
        """
        Generate a line plot of stress scores over time.
        :param history_data: list of dicts from StressHistory
        :return: base64 string of the image
        """
        if not history_data:
            return None

        dates = []
        scores = []

        for entry in history_data:
            try:
                dt = datetime.strptime(entry['date'], "%Y-%m-%d %H:%M:%S")
                # Format for display (e.g., month/day hour:min)
                dates.append(dt.strftime("%m/%d %H:%M"))
                scores.append(entry['stress_score'])
            except (ValueError, KeyError):
                continue

        if not dates:
            return None

        plt.figure(figsize=(10, 5))
        plt.plot(dates, scores, marker='o', linestyle='-', color='#4a90e2')
        plt.title('Stress Recovery Arc')
        plt.xlabel('Date')
        plt.ylabel('Stress Score')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save to BytesIO
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()

        # Encode to base64
        return base64.b64encode(img.getvalue()).decode('utf-8')
