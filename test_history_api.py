from app import app, db, User
from stress_history import StressHistory
import json

with app.app_context():
    user = User.query.first()
    history_manager = StressHistory(user_id=user.id)
    history_data = history_manager.load_history()
    print(json.dumps(history_data[:3], indent=2))
