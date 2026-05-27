import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/feedback_provider.dart';
import '../widgets/custom_textfield.dart';
import '../widgets/custom_button.dart';
import 'success_screen.dart';

class FeedbackScreen extends StatefulWidget {
  const FeedbackScreen({super.key});

  @override
  State<FeedbackScreen> createState() => _FeedbackScreenState();
}

class _FeedbackScreenState extends State<FeedbackScreen> {
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _feedbackController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _feedbackController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final provider = context.read<FeedbackProvider>();

    await provider.submitFeedback(
      name: _nameController.text.trim(),
      email: _emailController.text.trim(),
      message: _feedbackController.text.trim(),
    );

    if (!mounted) return;

    if (provider.status == FeedbackStatus.success) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => SuccessScreen(
            category: provider.predictedCategory ?? '',
          ),
        ),
      );
    } else if (provider.status == FeedbackStatus.error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(provider.errorMessage ?? 'Something went wrong'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = context.watch<FeedbackProvider>().status == FeedbackStatus.loading;

    return Scaffold(
      appBar: AppBar(title: const Text('Customer Feedback')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Share your thoughts',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 20),
              CustomTextField(
                label: 'Name',
                controller: _nameController,
              ),
              const SizedBox(height: 15),
              CustomTextField(
                label: 'Email',
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: 15),
              CustomTextField(
                label: 'Your Feedback',
                controller: _feedbackController,
                maxLines: 5,
              ),
              const SizedBox(height: 25),
              CustomButton(
                label: 'Submit Feedback',
                onPressed: _submit,
                isLoading: isLoading,
              ),

            ],
          ),
        ),
      ),
    );
  }
}
