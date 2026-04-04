import 'dart:async';
import 'package:flutter/material.dart';
import '../utils/constants.dart';
import 'role_selection_screen.dart';

class SplashScreen extends StatefulWidget {
  @override
  _SplashScreenState createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {

  @override
  void initState() {
    super.initState();

    Timer(Duration(seconds: 3), () {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => RoleSelectionScreen()),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.primary,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [

            Icon(Icons.volunteer_activism, size: 80, color: Colors.white),

            SizedBox(height: 20),

            Text(
              "Donation App",
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),

            SizedBox(height: 10),

            Text(
              "Helping communities connect",
              style: TextStyle(color: Colors.white70),
            ),

            SizedBox(height: 40),

            CircularProgressIndicator(color: Colors.white)
          ],
        ),
      ),
    );
  }
}