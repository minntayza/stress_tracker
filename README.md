# 🧠 Intelligent Adaptive Stress Assessment System

A comprehensive web application for stress assessment and management using fuzzy logic, sentiment analysis, and personalized goal tracking. The system learns from user patterns over time to provide adaptive recommendations for stress reduction.

## 🌟 Features

### **Multi-User Authentication**
- Secure user registration and login system
- Password hashing for data security
- Individual user profiles with isolated data

### **Intelligent Stress Analysis**
- **Fuzzy Logic Engine**: Analyzes multiple stress factors including:
  - Sleep quality and duration
  - Exercise frequency
  - Workload intensity
  - Social interaction levels
- **Hybrid ML/NLP**: Sentiment analysis using TextBlob to detect emotional nuances
- Real-time stress score calculation with personalized recommendations

### **Self-Improvement Tracking**
- **Healing Phase Detection**: Automatically identifies if stress levels are improving
- **Historical Analysis**: Compares current stress with previous assessments
- **Trend Monitoring**: Tracks whether users are in "Healing" or "Worsening" phases
- Delta calculations to validate if recommendations are working

### **Goal Management System**
- Set personalized stress reduction goals
- Track progress automatically based on stress assessments
- Visual progress indicators
- Achievement tracking and milestones

### **Visual Analytics**
- Recovery arc visualization (stress over time)
- Historical stress trend graphs
- Interactive charts and data visualization
- Network diagrams for stress factor relationships

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLite with Flask-SQLAlchemy
- **Authentication**: Flask-Login
- **ML/AI Components**:
  - scikit-fuzzy for fuzzy logic inference
  - TextBlob for sentiment analysis
  - NumPy for numerical computations
- **Visualization**: Matplotlib, NetworkX
- **Frontend**: HTML, CSS, Jinja2 templates

## 📋 Requirements

```
scikit-fuzzy
numpy
textblob
flask
matplotlib
networkx
scipy
packaging
Flask-Login
Flask-SQLAlchemy
email-validator
```

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd folder
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .env
   source .env/bin/activate  # On Windows: .env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:5001`

## 📖 Usage

1. **Sign Up**: Create a new account with your email and password
2. **Login**: Access your personal dashboard
3. **Stress Assessment**: Input your current stress factors:
   - Sleep quality (1-10)
   - Exercise frequency (1-10)
   - Workload level (1-10)
   - Social interaction quality (1-10)
4. **View Results**: Get your stress score and personalized recommendations
5. **Set Goals**: Create stress reduction goals and track progress
6. **Monitor History**: View your stress trends and healing phases over time

## 🏗️ Project Structure

```
.
├── app.py                  # Main Flask application with routes
├── fuzzy_logic.py         # Fuzzy logic inference system
├── stress_history.py      # History tracking and healing phase detection
├── hybrid_engine.py       # Sentiment analysis engine
├── visual_analytics.py    # Data visualization components
├── database.py            # Database models (User, Goal, StressHistory)
├── auth.py                # Authentication utilities
├── templates/             # HTML templates
│   ├── index.html        # Assessment form
│   ├── result.html       # Results display
│   ├── history.html      # Historical trends
│   ├── goals.html        # Goal management
│   ├── login.html        # Login page
│   └── signup.html       # Registration page
├── static/
│   └── style.css         # Application styles
└── requirements.txt      # Python dependencies
```

## 🧪 System Architecture

The system follows a **5-Phase Implementation**:

1. **Phase 1**: Core Knowledge Engine (Fuzzy Logic)
2. **Phase 2**: Self-Improvement Loop (History Tracking)
3. **Phase 3**: Hybrid ML & NLP (Sentiment Analysis)
4. **Phase 4**: Web Interface (Flask Application)
5. **Phase 5**: Visual Analytics (Trend Visualization)

### How the "Healing Loop" Works

1. **Initial Assessment**: User reports high stress (e.g., Score: 85)
2. **System Recommendation**: "Increase Sleep"
3. **Time Gap**: User implements the recommendation
4. **Follow-up Assessment**: User returns after a week
5. **Improvement Calculation**: Delta = Previous (85) - Current (55) = +30 improvement
6. **System Decision**: "User is in Healing Phase"
7. **Adaptive Learning**: System reinforces the "Sleep" strategy for future recommendations

## 🎯 Key Algorithms

### Fuzzy Logic Inference
- Uses triangular membership functions
- Analyzes multiple input variables simultaneously
- Produces interpretable stress scores (0-100)

### Healing Phase Detection
```python
if current_stress < previous_stress:
    status = "Healing Phase"
else:
    status = "Intervention Needed"
```

### Sentiment Analysis
- Analyzes user text input for emotional state
- Enhances stress assessment accuracy
- Detects nuances beyond numerical inputs

## 🔐 Security Features

- Password hashing with Werkzeug
- Session management with Flask-Login
- User data isolation in database
- Secure authentication flows

## 📊 Testing

The project includes test files for various components:
- `test_app.py`: Flask application tests
- `test_adaptive.py`: Adaptive learning tests
- `test_phase5.py`: Visual analytics tests

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Built as part of an intelligent stress management system project.

## 🙏 Acknowledgments

- Fuzzy logic implementation inspired by stress assessment research
- Self-improvement loop based on behavioral analysis principles
- UI/UX designed for accessibility and ease of use

---

**Note**: This application is for educational and personal use. It is not a substitute for professional mental health care. If you're experiencing severe stress or mental health issues, please consult a healthcare professional.
