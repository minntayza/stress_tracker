from textblob import TextBlob

class HybridEngine:
    # Stress-related words TextBlob's lexicon misses or underweights
    NEGATIVE_STRESS_WORDS = {
        'drained': -0.6, 'overwhelmed': -0.7, 'burned out': -0.8, 'burnout': -0.8,
        'overloaded': -0.6, 'suffocated': -0.7, 'numb': -0.5, 'hopeless': -0.8,
        'helpless': -0.7, 'worthless': -0.8, 'crushed': -0.7, 'paralyzed': -0.6,
        'drowning': -0.7, 'trapped': -0.7, 'broken': -0.6, 'shattered': -0.7,
        'unmotivated': -0.5, 'restless': -0.4, 'anxious': -0.6, 'panicking': -0.8,
        'panic': -0.7, 'insomnia': -0.5, 'sleepless': -0.5, 'fatigued': -0.5,
        'exhausting': -0.6, 'miserable': -0.8, 'frustrated': -0.6, 'irritated': -0.5,
        'agitated': -0.5, 'tense': -0.4, 'pressured': -0.5, 'struggling': -0.5,
        'suffering': -0.7, 'crying': -0.6, 'lonely': -0.6, 'isolated': -0.5,
        'depressed': -0.8, 'suicidal': -1.0, 'self-harm': -1.0, 'destroyed': -0.7,
    }
    POSITIVE_STRESS_WORDS = {
        'relieved': 0.6, 'refreshed': 0.5, 'energized': 0.6, 'motivated': 0.5,
        'peaceful': 0.6, 'calm': 0.5, 'relaxed': 0.5, 'grateful': 0.6,
        'hopeful': 0.6, 'resilient': 0.5, 'focused': 0.4, 'productive': 0.5,
        'confident': 0.5, 'optimistic': 0.6, 'inspired': 0.5, 'rested': 0.5,
        'balanced': 0.4, 'healed': 0.5, 'recovered': 0.5, 'thriving': 0.7,
    }

    def __init__(self):
        pass

    def _custom_polarity_boost(self, text):
        """
        Scan text for stress-related keywords the base TextBlob lexicon
        misses and return an additive polarity adjustment.
        """
        lower = text.lower()
        adjustments = []
        for word, score in self.NEGATIVE_STRESS_WORDS.items():
            if word in lower:
                adjustments.append(score)
        for word, score in self.POSITIVE_STRESS_WORDS.items():
            if word in lower:
                adjustments.append(score)
        if not adjustments:
            return 0.0
        return sum(adjustments) / len(adjustments)

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of the given text.
        Returns dict with polarity, subjectivity, labels, noun phrases,
        and per-sentence breakdown.
        """
        if not text:
            return {
                'polarity': 0.0,
                'subjectivity': 0.0,
                'polarity_label': 'Neutral',
                'subjectivity_label': 'Balanced',
                'noun_phrases': [],
                'sentences': [],
            }

        blob = TextBlob(text)
        base_polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # Blend TextBlob polarity with custom stress-word boost
        # Custom dictionary gets higher weight (70%) since TextBlob often
        # misclassifies stress-specific vocabulary
        custom_boost = self._custom_polarity_boost(text)
        if custom_boost != 0.0:
            polarity = max(-1.0, min(1.0, base_polarity * 0.3 + custom_boost * 0.7))
        else:
            polarity = base_polarity

        # --- Polarity label ---
        if polarity > 0.25:
            polarity_label = 'Positive'
        elif polarity < -0.2:
            polarity_label = 'Negative'
        else:
            polarity_label = 'Neutral'

        # --- Subjectivity label ---
        if subjectivity > 0.6:
            subjectivity_label = 'Mostly Subjective'
        elif subjectivity < 0.4:
            subjectivity_label = 'Mostly Objective'
        else:
            subjectivity_label = 'Balanced'

        # --- Noun-phrase extraction (stress keyword tags) ---
        noun_phrases = list(dict.fromkeys(blob.noun_phrases))  # deduplicate, preserve order

        # --- Per-sentence sentiment breakdown ---
        sentences = []
        for sent in blob.sentences:
            sent_text = str(sent)
            sent_base = sent.sentiment.polarity
            sent_boost = self._custom_polarity_boost(sent_text)
            if sent_boost != 0.0:
                sent_polarity = max(-1.0, min(1.0, sent_base * 0.3 + sent_boost * 0.7))
            else:
                sent_polarity = sent_base
            sentences.append({
                'text': sent_text,
                'polarity': round(sent_polarity, 2),
                'label': 'Positive' if sent_polarity > 0.25
                         else 'Negative' if sent_polarity < -0.2
                         else 'Neutral',
            })

        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'polarity_label': polarity_label,
            'subjectivity_label': subjectivity_label,
            'noun_phrases': noun_phrases,
            'sentences': sentences,
        }

    def compute_hybrid_stress(self, fuzzy_score, sentiment):
        """
        Combine the fuzzy-logic base stress score with NLP sentiment analysis
        to produce a final hybrid stress score.

        - Negative journal polarity  → increases stress  (up to +10 pts)
        - Positive journal polarity  → decreases stress  (up to -10 pts)
        - High subjectivity amplifies the adjustment (emotional language = stronger signal)
        - No sentiment / no journal  → returns the fuzzy score unchanged.

        :param fuzzy_score: float (0-100) from fuzzy logic system
        :param sentiment:   dict with 'polarity' and 'subjectivity', or None
        :return:            float (0-100) adjusted hybrid score
        """
        if not sentiment:
            return fuzzy_score

        polarity = float(sentiment.get('polarity', 0.0))
        subjectivity = float(sentiment.get('subjectivity', 0.0))

        # Base adjustment: negative polarity pushes score UP, positive pulls DOWN
        # Scale: polarity ∈ [-1, 1] → raw adjustment ∈ [-10, +10]
        raw_adjustment = -polarity * 10.0

        # Amplify when language is highly subjective (emotional writing)
        # subjectivity ∈ [0, 1] → multiplier ∈ [0.5, 1.5]
        subjectivity_multiplier = 0.5 + subjectivity

        adjustment = raw_adjustment * subjectivity_multiplier

        hybrid_score = max(0.0, min(100.0, fuzzy_score + adjustment))
        return hybrid_score


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
        result = engine.analyze_sentiment(text)
        print(f"\nInput: '{text}'")
        print(f"  Polarity: {result['polarity']:.2f} ({result['polarity_label']})")
        print(f"  Subjectivity: {result['subjectivity']:.2f} ({result['subjectivity_label']})")
        print(f"  Noun phrases: {result['noun_phrases']}")
        for s in result['sentences']:
            print(f"  Sentence: \"{s['text']}\" → {s['label']} ({s['polarity']})")

    # --- Hybrid stress score demo ---
    print("\n--- Hybrid Stress Score Demo (base fuzzy = 50.0) ---")
    base = 50.0
    for text in test_inputs:
        sentiment = engine.analyze_sentiment(text)
        hybrid = engine.compute_hybrid_stress(base, sentiment)
        diff = hybrid - base
        print(f"  \"{text}\"")
        print(f"    Fuzzy: {base} → Hybrid: {hybrid:.1f} ({'+' if diff >= 0 else ''}{diff:.1f} pts)")
    print(f"\n  No journal → Hybrid: {engine.compute_hybrid_stress(base, None):.1f} (unchanged)")

