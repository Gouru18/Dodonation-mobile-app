import 'package:flutter/material.dart';
import '../utils/constants.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  Widget inputField(String hint, TextEditingController controller,
      {bool obscure = false}) {
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

  void login() async {
    var response = await ApiService.login(
      emailController.text,
      passwordController.text,
    );

    
    if (response['success'] == true) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Login successful")),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(response['message'] ?? "Login failed")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,

      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text("Login"),
      ),

      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Card(
            elevation: 6,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [

                  Text(
                    "Welcome Back",
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: AppColors.primary,
                    ),
                  ),

                  SizedBox(height: 10),

                  Text("Login to continue"),

                  SizedBox(height: 20),

                  inputField("Email", emailController),
                  inputField("Password", passwordController, obscure: true),

                  SizedBox(height: 20),

                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      minimumSize: Size(double.infinity, 50),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    onPressed: login,
                    child: Text(
                      "Login",
                      style: TextStyle(
                        color: Colors.white, 
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),

                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}