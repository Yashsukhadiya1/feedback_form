import 'dart:convert';
import 'package:http/http.dart' as http;
import '../utils/constants.dart';

class ApiService {
  /// Sends feedback to FastAPI ML endpoint.
  /// Returns the predicted category string e.g. 'Complaint', 'Compliment', 'Feature Request'
  Future<String> predictCategory({
    required String name,
    required String email,
    required String message,
  }) async {
    final uri = Uri.parse('${AppConstants.apiBaseUrl}/predict');

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'email': email,
        'message': message,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      // Expected response: { "category": "Complaint" }
      return data['category'] as String;
    } else {
      throw Exception('Failed to get prediction: ${response.statusCode}');
    }
  }
}
