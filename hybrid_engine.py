from textblob import TextBlob

class HybridEngine:
    def __init__(self):
        pass

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of the given text.
        :param text: str
        :return: dict with 'polarity' (-1 to 1) and 'subjectivity' (0 to 1)
        """
        if not text:
            return {'polarity': 0.0, 'subjectivity': 0.0}
        
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }

if __name__ == "__main__":
    # Test script
    print("Initializing HybridEngine (Phase 3)...")
    engine = HybridEngine()

    test_inputs = [
        "I am feeling great today and very productive!",
        "I am so stressed and tired, I can't sleep.",
        "It was an okay day, nothing special.",
        "I hate this, it's the worst day ever."
    ]

    for text in test_inputs:
        sentiment = engine.analyze_sentiment(text)
        print(f"Input: '{text}'\n  -> Polarity: {sentiment['polarity']:.2f}, Subjectivity: {sentiment['subjectivity']:.2f}")

