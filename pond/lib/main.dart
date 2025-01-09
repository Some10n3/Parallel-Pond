import 'package:flutter/material.dart';
import 'package:pond/screen/pond_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Fish Haven - Pond',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: PondScreen(pondName: 'Parallel Pond'),
    );
  }
}
