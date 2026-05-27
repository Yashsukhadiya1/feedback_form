from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ml_model import predict_category
from email_service import send_thank_you_email

app = FastAPI(title="Feedback API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class FeedbackRequest(BaseModel):
    name: str
    email: str
    message: str


class PredictionResponse(BaseModel):
    category: str


@app.post("/predict", response_model=PredictionResponse)
async def predict(feedback: FeedbackRequest):
    category = predict_category(feedback.message)

    # Send thank-you email asynchronously (fire and forget)
    try:
        send_thank_you_email(
            to_email=feedback.email,
            name=feedback.name,
            category=category,
        )
    except Exception:
        pass  # Don't fail the request if email fails

    return PredictionResponse(category=category)


@app.get("/health")
def health():
    return {"status": "ok"}
