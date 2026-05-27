import 'package:flutter/material.dart';
import '../models/feedback_model.dart';
import '../services/api_service.dart';
import '../services/firebase_service.dart';

enum FeedbackStatus { idle, loading, success, error }

class FeedbackProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  final FirebaseService _firebaseService = FirebaseService();

  FeedbackStatus status = FeedbackStatus.idle;
  String? errorMessage;
  String? predictedCategory;

  Future<void> submitFeedback({
    required String name,
    required String email,
    required String message,
  }) async {
    status = FeedbackStatus.loading;
    errorMessage = null;
    notifyListeners();

    try {
      // Step 1: Send to FastAPI → get ML prediction
      final category = await _apiService.predictCategory(
        name: name,
        email: email,
        message: message,
      );
      predictedCategory = category;

      // Step 2: Save to Firestore in the correct collection
      final feedback = FeedbackModel(
        name: name,
        email: email,
        message: message,
        category: category,
        timestamp: DateTime.now(),
      );
      await _firebaseService.saveFeedback(feedback);

      status = FeedbackStatus.success;
    } catch (e) {
      status = FeedbackStatus.error;
      errorMessage = e.toString();
    }

    notifyListeners();
  }

  void reset() {
    status = FeedbackStatus.idle;
    errorMessage = null;
    predictedCategory = null;
    notifyListeners();
  }
}
