import 'package:flutter/material.dart';
import 'screens/role_selection_screen.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Donation App',
      home: RoleSelectionScreen(),
    );
  }
}