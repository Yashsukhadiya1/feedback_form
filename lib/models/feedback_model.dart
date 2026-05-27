class FeedbackModel {
  final String name;
  final String email;
  final String message;
  final String? category; // 'Complaint' | 'Compliment' | 'Feature Request'
  final DateTime? timestamp;

  FeedbackModel({
    required this.name,
    required this.email,
    required this.message,
    this.category,
    this.timestamp,
  });

  Map<String, dynamic> toJson() => {
        'name': name,
        'email': email,
        'message': message,
        if (category != null) 'category': category,
        if (timestamp != null) 'timestamp': timestamp!.toIso8601String(),
      };
}
