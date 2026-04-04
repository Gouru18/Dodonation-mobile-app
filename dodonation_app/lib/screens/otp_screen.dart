import 'package:flutter/material.dart';
import '../utils/constants.dart';
import '../services/api_service.dart';

class OTPScreen extends StatefulWidget {
  final String email;

  OTPScreen({required this.email});

  @override
  _OTPScreenState createState() => _OTPScreenState();
}

class _OTPScreenState extends State<OTPScreen> {
  final otpController = TextEditingController();

  void verify() async {
    await ApiService.verifyOtp(widget.email, otpController.text);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text("Verify OTP"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [

            Text("Enter OTP sent to your email"),

            SizedBox(height: 20),

            TextField(
              controller: otpController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                hintText: "Enter OTP",
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),

            SizedBox(height: 20),

            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                minimumSize: Size(double.infinity, 50),
              ),
              onPressed: verify,
              child: Text(
                "Verify",
                style: TextStyle(color: Colors.white),
              ),
            )
          ],
        ),
      ),
    );
  }
}