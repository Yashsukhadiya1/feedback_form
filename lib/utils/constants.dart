import 'package:flutter/foundation.dart';

class AppConstants {
  static const String appName = 'Feedback Form';

  // Automatically uses correct URL based on platform:
  // - Web (Chrome): 127.0.0.1 (same machine)
  // - Android phone: 10.76.206.243 (PC's local IP on hotspot)
  static String get apiBaseUrl {
    if (kIsWeb) {
      return 'http://127.0.0.1:8000';
    }
    return 'http://10.76.206.243:8000';
  }

  // Firestore collections
  static const String complaintsCollection = 'complaints';
  static const String complimentsCollection = 'compliments';
  static const String featureRequestsCollection = 'feature_requests';
}
