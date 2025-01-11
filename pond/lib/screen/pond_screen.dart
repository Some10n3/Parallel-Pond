import 'package:flutter/material.dart';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';
import 'dart:async';
import 'dart:convert';

class PondScreen extends StatefulWidget {
  final String pondName;
  const PondScreen({super.key, required this.pondName});

  @override
  _PondScreenState createState() => _PondScreenState();
}

class _PondScreenState extends State<PondScreen> {
  late MqttServerClient client;
  String statusMessage = "Disconnected";
  String receivedMessage = "No messages yet";
  final String topic =
      "fishhaven/stream"; // Updated to match Python script topic
  Timer? _imageChangeTimer;

  final List<String> images = [
    'lib/assets/tile1.png',
    'lib/assets/tile2.png',
    'lib/assets/tile3.png',
    'lib/assets/tile4.png'
  ];
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    connectToMQTT();
    startImageChangeTimer();
  }

  @override
  void dispose() {
    _imageChangeTimer?.cancel();
    super.dispose();
  }

  void onConnected() {
    setState(() {
      statusMessage = "Connected to MQTT broker!";
    });
  }

  void onDisconnected() {
    setState(() {
      statusMessage = "Disconnected from MQTT broker!";
    });
  }

  void onSubscribed(String topic) {
    setState(() {
      statusMessage = "Subscribed to $topic";
    });
  }

  Future<void> connectToMQTT() async {
    client = MqttServerClient('40.90.169.126', '');
    client.port = 1883;
    client.logging(on: true);
    client.onConnected = onConnected;
    client.onDisconnected = onDisconnected;
    client.onSubscribed = onSubscribed;

    final connMessage = MqttConnectMessage()
        .withClientIdentifier(widget.pondName)
        .authenticateAs('dc24', 'kmitl-dc24')
        .startClean()
        .withWillTopic('willtopic')
        .withWillMessage('Client Disconnected')
        .withWillQos(MqttQos.atLeastOnce);

    client.connectionMessage = connMessage;

    try {
      await client.connect();
    } catch (e) {
      setState(() {
        statusMessage = "Connection failed: $e";
      });
      client.disconnect();
    }

    if (client.connectionStatus?.state == MqttConnectionState.connected) {
      setState(() {
        statusMessage = "Connected to MQTT broker!";
      });

      client.subscribe(topic, MqttQos.atLeastOnce);
      client.updates?.listen((List<MqttReceivedMessage<MqttMessage>> events) {
        final MqttPublishMessage recMessage =
            events[0].payload as MqttPublishMessage;
        final String message = MqttPublishPayload.bytesToStringAsString(
            recMessage.payload.message);

        setState(() {
          receivedMessage = message;
        });
      });
    } else {
      setState(() {
        statusMessage = "Failed to connect: ${client.connectionStatus?.state}";
      });
      client.disconnect();
    }
  }

  void startImageChangeTimer() {
    _imageChangeTimer = Timer.periodic(Duration(milliseconds: 300), (timer) {
      setState(() {
        _currentIndex = (_currentIndex + 1) % images.length;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Pond: ${widget.pondName}'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 400,
              height: 400,
              decoration: BoxDecoration(
                color: Colors.blue,
                shape: BoxShape.circle,
                border: Border.all(color: Colors.black, width: 3),
              ),
              child: Center(
                child: Image.asset(
                  images[_currentIndex],
                  fit: BoxFit.cover,
                ),
              ),
            ),
            SizedBox(height: 20),
            Text(
              'Pond Name: ${widget.pondName}',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 20),
            Text(
              'Status: $statusMessage',
              style: TextStyle(fontSize: 16),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 20),
            Text(
              'Received Message: $receivedMessage',
              style: TextStyle(fontSize: 16, color: Colors.green),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
