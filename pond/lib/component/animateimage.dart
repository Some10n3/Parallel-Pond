import 'package:flutter/material.dart';
import 'dart:async';

class AnimatedImageSwitcher extends StatefulWidget {
  const AnimatedImageSwitcher({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _AnimatedImageSwitcherState createState() => _AnimatedImageSwitcherState();
}

class _AnimatedImageSwitcherState extends State<AnimatedImageSwitcher> {
  final List<String> images = [
    'assets/image1.png', // Replace with your image paths
    'assets/image2.png',
    'assets/image3.png',
    'assets/image4.png'
  ];

  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    _startImageSwitching();
  }

  void _startImageSwitching() {
    Timer.periodic(Duration(seconds: 2), (timer) {
      setState(() {
        _currentIndex = (_currentIndex + 1) % images.length;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: AnimatedSwitcher(
        duration: Duration(seconds: 1),
        child: Image.asset(
          images[_currentIndex],
          key: ValueKey<int>(
              _currentIndex), // This ensures that the widget is rebuilt
          fit: BoxFit.cover,
        ),
      ),
    );
  }
}
