# Intelligent Adaptive Stress Assessment System

An AI-assisted web application that helps users assess, monitor, and understand their stress levels through fuzzy logic, sentiment analysis, and personalized recommendations.

## Overview

This project combines rule-based reasoning and lightweight NLP to build a more human-friendly stress assessment experience. Instead of relying on a single score, the system evaluates multiple lifestyle and emotional factors such as sleep, exercise, workload, and user-written reflections to generate adaptive stress insights.

## Key Features

- Secure user registration and login
- Multi-factor stress evaluation using fuzzy logic
- Sentiment analysis on user input for emotional context
- Personalized recommendations based on current stress level
- Historical stress tracking over time
- Healing/worsening trend detection
- Goal setting and progress tracking
- Visual analytics for recovery trends and factor relationships

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite, Flask-SQLAlchemy
- **Authentication:** Flask-Login
- **AI / Logic:** scikit-fuzzy, TextBlob, NumPy
- **Visualization:** Matplotlib, NetworkX
- **Frontend:** HTML, CSS, Jinja2

## Screenshots

> Add your own screenshots in a `/screenshots` folder and update the paths below.

- Dashboard overview  
  `![Dashboard](./screenshots/dashboard.png)`
- Stress assessment form  
  `![Assessment](./screenshots/assessment.png)`
- Trend analytics  
  `![Analytics](./screenshots/analytics.png)`

## How It Works

1. The user logs in and submits stress-related inputs.
2. A fuzzy logic engine evaluates the combined effect of multiple factors.
3. Sentiment analysis adds emotional context from text responses.
4. The system generates a stress score and personalized recommendations.
5. Historical records are used to detect whether the user is improving or worsening over time.

## Run Locally

```bash
git clone https://github.com/minntayza/stress_tracker.git
cd stress_tracker
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
