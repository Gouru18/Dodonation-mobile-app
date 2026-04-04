import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = "http://10.0.2.2:8000/api";

  static Future register(Map data) async {
    final response = await http.post(
      Uri.parse("$baseUrl/register/"),
      body: jsonEncode(data),
      headers: {"Content-Type": "application/json"},
    );
    return jsonDecode(response.body);
  }

  static Future login(String email, String password) async {
    final response = await http.post(
      Uri.parse("$baseUrl/login/"),
      body: jsonEncode({
        "email": email,
        "password": password
      }),
      headers: {"Content-Type": "application/json"},
    );
    return jsonDecode(response.body);
  }

  static Future verifyOtp(String email, String otp) async {
    final response = await http.post(
      Uri.parse("$baseUrl/verify-otp/"),
      body: jsonEncode({
        "email": email,
        "otp": otp
      }),
      headers: {"Content-Type": "application/json"},
    );
    return jsonDecode(response.body);
  }
}