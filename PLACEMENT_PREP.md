# Placement Preparation — Feedback Form Project

Interview questions and answers based on this project. Covers FastAPI, Firebase Firestore, networking, ML, and email — all explained simply and clearly.

---

## Section 1 — FastAPI

### Q1. What is FastAPI and why did you use it?

FastAPI is a Python web framework used to build REST APIs. I used it as the backend server for this project because:
- It is fast and easy to write
- It automatically validates request and response data using Pydantic models
- It supports async operations
- It auto-generates interactive API docs at `/docs`

In this project, FastAPI receives feedback from the Flutter app, runs the ML model, sends an email, and returns the predicted category.

---

### Q2. What is an API and what is a REST API?

An API (Application Programming Interface) is a way for two programs to talk to each other.

A REST API uses HTTP methods to communicate:
- `GET` — fetch data
- `POST` — send data
- `PUT` — update data
- `DELETE` — delete data

In this project, Flutter sends a `POST` request to FastAPI's `/predict` endpoint with the feedback data, and FastAPI responds with the predicted category.

---

### Q3. What is an endpoint?

An endpoint is a specific URL in the API that performs a specific action.

In this project:
- `POST /predict` — receives feedback, runs ML model, sends email, returns category
- `GET /health` — returns `{"status": "ok"}` to confirm the server is running

---

### Q4. What is Pydantic and how is it used here?

Pydantic is a Python library for data validation using type hints.

In `main.py`:
```python
class FeedbackRequest(BaseModel):
    name: str
    email: str
    message: str
```

When Flutter sends JSON to `/predict`, FastAPI automatically validates it against `FeedbackRequest`. If `name` is missing or not a string, FastAPI returns a 422 error automatically — no manual validation needed.

---

### Q5. What is CORS and why is it needed?

CORS (Cross-Origin Resource Sharing) is a browser security rule that blocks web pages from making requests to a different domain or port than the one they came from.

The Flutter web app runs on `localhost:58122` but FastAPI runs on `localhost:8000`. The browser sees these as different origins and blocks the request.

The fix in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This tells FastAPI to allow requests from any origin. CORS only applies to browsers — mobile apps and Postman are not affected.

---

### Q6. What is uvicorn?

Uvicorn is an ASGI (Asynchronous Server Gateway Interface) server that runs FastAPI applications.

FastAPI is just a framework — it defines the routes and logic. Uvicorn is the actual server that listens for HTTP requests and passes them to FastAPI.

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

- `main` — the Python file name (`main.py`)
- `app` — the FastAPI instance inside that file
- `--host 0.0.0.0` — listen on all network interfaces
- `--port 8000` — use port 8000
- `--reload` — restart automatically when code changes

---

## Section 2 — Networking (Port, Host, IP)

### Q7. What is a port?

A port is a number that identifies a specific service running on a computer. A computer has one IP address but can run many services, each on a different port.

Common ports:
- `80` — HTTP websites
- `443` — HTTPS websites
- `8000` — FastAPI (this project)
- `587` — Gmail SMTP email

When Flutter calls `http://10.76.206.243:8000/predict`, it means:
- Go to IP `10.76.206.243`
- Connect to port `8000`
- Call the `/predict` endpoint

---

### Q8. What is the difference between 127.0.0.1 and 0.0.0.0?

`127.0.0.1` (also called localhost) is a loopback address. It means "this machine only". Only the same computer can connect to a server running on `127.0.0.1`.

`0.0.0.0` means "all available network interfaces". A server running on `0.0.0.0` accepts connections from:
- The same machine (localhost)
- Other devices on the same WiFi/hotspot network
- Any device that can reach this machine's IP

In this project, running FastAPI with `--host 0.0.0.0` is what allows the phone to connect to the PC's server.

---

### Q9. Why did the phone get a "Connection timed out" error?

Three possible reasons:

1. FastAPI was running with `--host 127.0.0.1` (default) instead of `--host 0.0.0.0` — so it was not listening for phone connections
2. Windows Firewall was blocking incoming connections on port 8000
3. The phone and PC were not on the same network

The fix was:
- Run FastAPI with `--host 0.0.0.0`
- Add a Windows Firewall inbound rule to allow port 8000
- Connect PC to phone's hotspot so both are on the same network

---

### Q10. What is a local IP address?

A local IP (like `10.76.206.243` or `192.168.1.x`) is the address assigned to a device within a private network (home WiFi, hotspot). It is only reachable from within that same network.

When the phone and PC are on the same hotspot, the phone can reach the PC using its local IP. This is how the Flutter app on the phone calls the FastAPI server on the PC.

---

## Section 3 — Firebase & Firestore

### Q11. What is Firebase?

Firebase is Google's Backend-as-a-Service (BaaS) platform. It provides:
- Firestore (NoSQL database)
- Authentication
- Cloud Storage
- Hosting
- Cloud Functions

It removes the need to build and manage your own backend infrastructure. In this project, Firebase is used only for Firestore database storage.

---

### Q12. What is Firestore and how is it different from a SQL database?

Firestore is a NoSQL cloud database. Data is stored as collections and documents instead of tables and rows.

| SQL | Firestore |
|---|---|
| Table | Collection |
| Row | Document |
| Column | Field |
| JOIN | Subcollection or denormalization |

In this project, three collections are used:
- `complaints` — stores complaint feedback
- `compliments` — stores compliment feedback
- `feature_requests` — stores feature request feedback

Each document looks like:
```json
{
  "name": "Yash",
  "email": "yash@gmail.com",
  "message": "App keeps crashing",
  "category": "Complaint",
  "timestamp": "2026-05-22T11:00:00Z"
}
```

---

### Q13. How does Flutter connect to Firestore?

Flutter connects to Firestore using the `cloud_firestore` package. Firebase is initialized at app startup in `main.dart` using credentials from `firebase_options.dart` (generated by FlutterFire CLI).

```dart
await Firebase.initializeApp(
  options: DefaultFirebaseOptions.currentPlatform,
);
```

After that, anywhere in the app:
```dart
await FirebaseFirestore.instance.collection('complaints').add({...});
```

This sends data directly from the Flutter app to Google's Firestore servers over the internet — no custom backend needed for this part.

---

### Q14. What is FieldValue.serverTimestamp()?

Instead of using the device's clock (`DateTime.now()`), `FieldValue.serverTimestamp()` tells Firestore to use the server's time when the document is written.

This is more reliable because:
- Device clocks can be wrong or in different timezones
- Server timestamp is consistent across all devices

---

### Q15. How are the three Firestore collections decided?

In `firebase_service.dart`, a switch statement maps the ML-predicted category to the correct collection name:

```dart
switch (category) {
  case 'Complaint': return 'complaints';
  case 'Compliment': return 'compliments';
  case 'Feature Request': return 'feature_requests';
}
```

The collection is created automatically by Firestore the first time a document is added to it — no manual setup needed.

---

## Section 4 — ML Model

### Q16. What ML algorithm is used and why?

TF-IDF + Logistic Regression.

- **TF-IDF** converts text into numbers. It gives higher scores to words that are important in one category but rare in others.
- **Logistic Regression** is a classification algorithm that learns from labeled examples and predicts which class a new input belongs to.

This combination is chosen because:
- It works well for text classification
- It is fast to train and predict
- It is interpretable (you can understand why it made a decision)
- It does not need a GPU

---

### Q17. What is the dataset and how is it used?

File: `large_feedback_dataset.csv`
- 9,000 rows, 3,000 per category
- Two columns: `feedback` (text) and `category` (label)

The model is trained on this data the first time the server starts. It learns patterns like which words appear in complaints vs compliments. After training, the model is saved as `model.pkl` so it does not retrain on every restart.

---

### Q18. Why was the model giving wrong predictions initially?

The dataset had noisy data — some compliment rows contained complaint-like phrases such as "please fix" or "it should be resolved". The model learned these mixed patterns and got confused.

The fix was adding a `SentimentFeatures` class — a custom feature extractor that counts strong sentiment keywords (like "hate", "crash", "broken" for complaints) and adds those counts as extra features alongside TF-IDF. This gave the model a stronger signal to override the noise.

---

### Q19. What is model.pkl?

`model.pkl` is the trained ML model saved to disk using Python's `pickle` library.

The entire pipeline (TF-IDF + SentimentFeatures + Logistic Regression) is serialized into this file. When the server restarts, it loads from `model.pkl` instead of retraining from scratch — making startup fast.

To force a retrain, delete `model.pkl` and restart the server.

---

## Section 5 — Email System

### Q20. How does the email system work step by step?

1. User submits feedback from Flutter
2. Flutter sends name, email, message to FastAPI `/predict`
3. FastAPI calls `predict_category(message)` → gets category
4. FastAPI calls `send_thank_you_email(to_email, name, category)`
5. `email_service.py` connects to Gmail's SMTP server at `smtp.gmail.com:587`
6. It starts TLS encryption using `starttls()`
7. It logs in using the Gmail address and App Password from `.env`
8. It sends an HTML-formatted email to the user's email address
9. If email fails, the error is caught and the API still returns the category to Flutter (email failure does not break the app)

---

### Q21. What is SMTP?

SMTP (Simple Mail Transfer Protocol) is the standard protocol for sending emails over the internet.

Gmail provides an SMTP server at `smtp.gmail.com` on port `587`. Any application can use it to send emails by logging in with a Gmail account.

In this project, `smtplib` (Python's built-in library) is used to connect to Gmail's SMTP server and send the thank-you email.

---

### Q22. What is a Gmail App Password and why is it needed?

Google does not allow regular Gmail passwords to be used in third-party apps for security reasons. Instead, you generate an App Password — a 16-character password specifically for one app.

Steps:
1. Enable 2-Step Verification on Google account
2. Go to myaccount.google.com → Security → App Passwords
3. Generate password for "Mail"
4. Use that 16-character password in `.env` as `SMTP_PASS`

---

### Q23. What is TLS and why is starttls() used?

TLS (Transport Layer Security) encrypts the connection between the app and the email server so the password and email content cannot be intercepted.

`starttls()` upgrades a plain connection to an encrypted one. It must be called before `login()` — otherwise the password would be sent in plain text over the network.

---

### Q24. Why are credentials stored in a .env file?

Hardcoding credentials (email, password) directly in code is a security risk — anyone who sees the code can steal them.

A `.env` file stores them separately and is added to `.gitignore` so it is never committed to Git. The `python-dotenv` library loads these values at runtime using `load_dotenv()`.

---

## Section 6 — Full System Connection (Step by Step)

### Q25. Explain the complete flow of the app from start to finish.

```
Step 1 — App starts
  main.dart initializes Firebase using firebase_options.dart
  FeedbackProvider is created and provided to the widget tree
  SplashScreen is shown for 2 seconds

Step 2 — User opens Feedback Screen
  FeedbackScreen shows Name, Email, Feedback fields

Step 3 — User fills form and taps Submit
  FeedbackScreen calls FeedbackProvider.submitFeedback()
  Status changes to loading → button shows spinner

Step 4 — Flutter calls FastAPI
  ApiService sends POST request to http://PC_IP:8000/predict
  Body: { "name": "Yash", "email": "...", "message": "App crashes" }

Step 5 — FastAPI receives request
  Pydantic validates the incoming JSON
  predict_category("App crashes") is called

Step 6 — ML Model predicts
  Text is cleaned (lowercase, remove punctuation)
  TF-IDF converts text to numbers
  SentimentFeatures counts keyword matches
  Logistic Regression predicts: "Complaint"

Step 7 — FastAPI sends email
  send_thank_you_email("yash@gmail.com", "Yash", "Complaint") is called
  Connects to smtp.gmail.com:587
  Sends HTML thank-you email to user

Step 8 — FastAPI returns response
  { "category": "Complaint" } is sent back to Flutter

Step 9 — Flutter saves to Firestore
  FirebaseService.saveFeedback() is called
  Document is saved to the "complaints" collection in Firestore
  Fields: name, email, message, category, timestamp

Step 10 — Success Screen
  FeedbackProvider status = success
  FeedbackScreen navigates to SuccessScreen
  SuccessScreen shows: warning icon, "Complaint" badge, thank you message
```

---

## Section 7 — Quick Revision Questions

| Question | Answer |
|---|---|
| What framework is the frontend built in? | Flutter (Dart) |
| What framework is the backend built in? | FastAPI (Python) |
| What database is used? | Firebase Firestore (NoSQL) |
| What ML algorithm is used? | TF-IDF + Logistic Regression |
| How many categories does the model predict? | 3 — Complaint, Compliment, Feature Request |
| How many rows in the dataset? | 9,000 (3,000 per category) |
| What port does FastAPI run on? | 8000 |
| What does --host 0.0.0.0 do? | Makes server accessible from other devices on the network |
| What is model.pkl? | Saved trained ML pipeline |
| What protocol is used for email? | SMTP (Gmail, port 587) |
| What is CORS? | Browser security rule — allows cross-origin API calls |
| What is FieldValue.serverTimestamp()? | Uses Firestore server time instead of device clock |
| What state management is used in Flutter? | Provider (ChangeNotifier) |
| Where are email credentials stored? | backend/.env (not committed to Git) |
| What is TLS? | Encryption for network connections |
