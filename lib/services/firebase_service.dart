import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/feedback_model.dart';
import '../utils/constants.dart';

class FirebaseService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  /// Saves feedback to the appropriate Firestore collection based on category.
  Future<void> saveFeedback(FeedbackModel feedback) async {
    final collection = _collectionFor(feedback.category ?? '');

    await _firestore.collection(collection).add({
      'name': feedback.name,
      'email': feedback.email,
      'message': feedback.message,
      'category': feedback.category,
      'timestamp': FieldValue.serverTimestamp(),
    });
  }

  String _collectionFor(String category) {
    switch (category) {
      case 'Complaint':
        return AppConstants.complaintsCollection;
      case 'Compliment':
        return AppConstants.complimentsCollection;
      case 'Feature Request':
        return AppConstants.featureRequestsCollection;
      default:
        return AppConstants.complaintsCollection;
    }
  }
}
