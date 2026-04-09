import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'dart:io';

class NGOPermitScreen extends StatefulWidget {
  @override
  _NGOPermitScreenState createState() => _NGOPermitScreenState();
}

class _NGOPermitScreenState extends State<NGOPermitScreen> {
  File? _selectedFile;
  bool _isUploading = false;

  Future<void> pickFile() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.any);
    if (result != null) {
      setState(() {
        _selectedFile = File(result.files.single.path!);
      });
    }
  }

  Future<void> uploadFile() async {
    if (_selectedFile == null) return;

    setState(() => _isUploading = true);

    final request = http.MultipartRequest(
      'POST',
      Uri.parse('http://127.0.0.1:8000/ngo/upload-permit/'), // your backend endpoint
    );
    request.files.add(await http.MultipartFile.fromPath('permit_file', _selectedFile!.path));

    final response = await request.send();
    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Permit uploaded successfully!')));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Upload failed.')));
    }

    setState(() => _isUploading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Upload NGO Permit')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            ElevatedButton(
              onPressed: pickFile,
              child: Text(_selectedFile == null ? 'Select File' : 'Change File'),
            ),
            if (_selectedFile != null) Text('Selected: ${_selectedFile!.path.split('/').last}'),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _isUploading ? null : uploadFile,
              child: Text(_isUploading ? 'Uploading...' : 'Upload Permit'),
            ),
          ],
        ),
      ),
    );
  }
}