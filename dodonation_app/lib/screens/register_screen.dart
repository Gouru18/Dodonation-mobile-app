import 'package:flutter/material.dart';
import '../utils/constants.dart';
import '../services/api_service.dart';
import 'otp_screen.dart';

class RegisterScreen extends StatefulWidget {
  final String role;

  RegisterScreen({required this.role});

  @override
  _RegisterScreenState createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  Widget inputField(String hint, TextEditingController controller, {bool obscure = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: TextField(
        controller: controller,
        obscureText: obscure,
        decoration: InputDecoration(
          hintText: hint,
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }

  void register() async {
    await ApiService.register({
      "email": emailController.text,
      "password": passwordController.text,
      "role": widget.role,
    });

    Navigator.push(context,
      MaterialPageRoute(builder: (_) => OTPScreen(email: emailController.text)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text("Register (${widget.role})"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [

            inputField("Email", emailController),
            inputField("Password", passwordController, obscure: true),

            SizedBox(height: 20),

            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                minimumSize: Size(double.infinity, 50),
              ),
              onPressed: register,
              child: Text(
                "Register",
                style: TextStyle(color: Colors.white),
              ),
            )
          ],
        ),
      ),
    );
  }
}