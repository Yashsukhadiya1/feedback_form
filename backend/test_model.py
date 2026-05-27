from ml_model import predict_category

tests = [
    ("This app is terrible, it keeps crashing every time I open it", "Complaint"),
    ("I hate this app, nothing works at all", "Complaint"),
    ("The app is broken and very slow", "Complaint"),
    ("Very bad experience, worst app ever", "Complaint"),
    ("App crashes on startup, please fix this bug", "Complaint"),
    ("I love this app, great work team", "Compliment"),
    ("Fantastic experience, very smooth", "Compliment"),
    ("Please add dark mode feature", "Feature Request"),
    ("Would be nice to have export option", "Feature Request"),
]

print(f"{'Predicted':<20} {'Expected':<20} {'Match':<6} Input")
print("-" * 90)
correct = 0
for text, expected in tests:
    predicted = predict_category(text)
    match = predicted == expected
    if match:
        correct += 1
    print(f"{predicted:<20} {expected:<20} {'✓' if match else '✗':<6} {text}")

print(f"\nAccuracy: {correct}/{len(tests)} = {correct/len(tests)*100:.0f}%")
