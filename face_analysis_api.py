// Flutter: main.dart с отправкой фото на сервер DeepFace API

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(AstroMatchApp());
}

class AstroMatchApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AstroMatch',
      theme: ThemeData(
        primarySwatch: Colors.pink,
        scaffoldBackgroundColor: Colors.pink[50],
        textTheme: TextTheme(bodyMedium: TextStyle(fontSize: 16)),
      ),
      home: CompatibilityScreen(),
    );
  }
}

class CompatibilityScreen extends StatefulWidget {
  @override
  _CompatibilityScreenState createState() => _CompatibilityScreenState();
}

class _CompatibilityScreenState extends State<CompatibilityScreen> {
  DateTime? date1;
  DateTime? date2;
  File? image1;
  File? image2;
  String? result;

  final picker = ImagePicker();

  Future<void> calculateCompatibility() async {
    if (date1 == null || date2 == null || image1 == null || image2 == null) return;

    int score = 50;
    int diff = (date1!.difference(date2!).inDays).abs();
    if (diff < 30) score += 20;
    if (diff % 365 < 90) score += 10;

    String zodiac1 = getZodiac(date1!);
    String zodiac2 = getZodiac(date2!);

    if (zodiac1 == zodiac2) score += 20;
    if ((zodiac1 == 'Овен' && zodiac2 == 'Лев') ||
        (zodiac1 == 'Рыбы' && zodiac2 == 'Скорпион')) score += 10;

    int faceScore = await getFaceCompatibility(image1!, image2!);
    score = ((score + faceScore) / 2).round();

    setState(() {
      result = 'Совместимость: $score% ($zodiac1 + $zodiac2)';
    });
  }

  Future<int> getFaceCompatibility(File img1, File img2) async {
    var uri = Uri.parse("http://127.0.0.1:5000/analyze_faces"); // замените на свой сервер
    var request = http.MultipartRequest('POST', uri);
    request.files.add(await http.MultipartFile.fromPath('image1', img1.path));
    request.files.add(await http.MultipartFile.fromPath('image2', img2.path));

    try {
      var response = await request.send();
      var responseData = await response.stream.bytesToString();
      var jsonData = json.decode(responseData);
      return jsonData['face_compatibility'] ?? 0;
    } catch (e) {
      print("Ошибка анализа лица: $e");
      return 0;
    }
  }

  String getZodiac(DateTime date) {
    final day = date.day;
    final month = date.month;
    if ((month == 3 && day >= 21) || (month == 4 && day <= 19)) return 'Овен';
    if ((month == 4 && day >= 20) || (month == 5 && day <= 20)) return 'Телец';
    if ((month == 5 && day >= 21) || (month == 6 && day <= 20)) return 'Близнецы';
    if ((month == 6 && day >= 21) || (month == 7 && day <= 22)) return 'Рак';
    if ((month == 7 && day >= 23) || (month == 8 && day <= 22)) return 'Лев';
    if ((month == 8 && day >= 23) || (month == 9 && day <= 22)) return 'Дева';
    if ((month == 9 && day >= 23) || (month == 10 && day <= 22)) return 'Весы';
    if ((month == 10 && day >= 23) || (month == 11 && day <= 21)) return 'Скорпион';
    if ((month == 11 && day >= 22) || (month == 12 && day <= 21)) return 'Стрелец';
    if ((month == 12 && day >= 22) || (month == 1 && day <= 19)) return 'Козерог';
    if ((month == 1 && day >= 20) || (month == 2 && day <= 18)) return 'Водолей';
    if ((month == 2 && day >= 19) || (month == 3 && day <= 20)) return 'Рыбы';
    return 'Неизвестно';
  }

  Future<void> pickDate(bool isFirst) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime(2000),
      firstDate: DateTime(1950),
      lastDate: DateTime(2050),
    );
    if (picked != null) {
      setState(() {
        if (isFirst) {
          date1 = picked;
        } else {
          date2 = picked;
        }
      });
    }
  }

  Future<void> pickImage(bool isFirst) async {
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        if (isFirst) {
          image1 = File(pickedFile.path);
        } else {
          image2 = File(pickedFile.path);
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('AstroMatch')),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: SingleChildScrollView(
          child: Column(
            children: [
              TextButton(
                onPressed: () => pickDate(true),
                child: Text(date1 == null ? 'Выбрать дату мужчины' : DateFormat.yMMMd().format(date1!)),
              ),
              TextButton(
                onPressed: () => pickImage(true),
                child: Text(image1 == null ? 'Загрузить фото мужчины' : 'Фото мужчины выбрано'),
              ),
              Divider(),
              TextButton(
                onPressed: () => pickDate(false),
                child: Text(date2 == null ? 'Выбрать дату женщины' : DateFormat.yMMMd().format(date2!)),
              ),
              TextButton(
                onPressed: () => pickImage(false),
                child: Text(image2 == null ? 'Загрузить фото женщины' : 'Фото женщины выбрано'),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: calculateCompatibility,
                child: Text('Рассчитать совместимость'),
              ),
              SizedBox(height: 20),
              if (result != null)
                Text(result!, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            ],
          ),
        ),
      ),
    );
  }
}
