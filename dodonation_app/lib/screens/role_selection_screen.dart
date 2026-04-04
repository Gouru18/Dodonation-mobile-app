import 'package:flutter/material.dart';
import '../utils/constants.dart';
import 'register_screen.dart';
import 'login_screen.dart';

class RoleSelectionScreen extends StatelessWidget {
  Widget buildButton(BuildContext context, String text, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: ElevatedButton(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          minimumSize: Size(double.infinity, 50),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        onPressed: onTap,
        child: Text(
          text,
            style: TextStyle(
            fontSize: 16,
            color: Colors.white, // FIX
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
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
                    "Welcome",
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: AppColors.primary,
                    ),
                  ),

                  SizedBox(height: 10),

                  Text("Choose how you want to continue"),

                  SizedBox(height: 20),

                  buildButton(context, "Register as Donor", () {
                    Navigator.push(context,
                        MaterialPageRoute(builder: (_) => RegisterScreen(role: "donor")));
                  }),

                  buildButton(context, "Register as NGO", () {
                    Navigator.push(context,
                        MaterialPageRoute(builder: (_) => RegisterScreen(role: "ngo")));
                  }),

                  Divider(height: 30),

                  buildButton(context, "Login", () {
                    Navigator.push(context,
                        MaterialPageRoute(builder: (_) => LoginScreen()));
                  }),

                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}