import 'package:flutter/material.dart';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';
import 'dart:async'; // Import Timer
import 'dart:convert'; // Import JSON encoding
import 'package:intl/intl.dart'; // Import to work with UNIX timestamps

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
  final String topic = "fish_haven/pond";
  Timer? _imageChangeTimer; // Timer for automatic image change

  @override
  void initState() {
    super.initState();
    connectToMQTT();
    startImageChangeTimer(); // Start the timer when the widget is initialized
  }

  @override
  void dispose() {
    _imageChangeTimer?.cancel(); // Cancel the timer when the widget is disposed
    super.dispose();
  }

  final List<String> images = [
    'lib/assets/tile1.png', // Replace with your image paths
    'lib/assets/tile2.png',
    'lib/assets/tile3.png',
    'lib/assets/tile4.png'
  ];

  int _currentIndex = 0;

  Future<void> connectToMQTT() async {
    client =
        MqttServerClient('40.90.169.126', ''); // Use the provided server IP
    client.port = 1883; // Use the provided port
    client.logging(on: true);
    client.onConnected = onConnected;
    client.onDisconnected = onDisconnected;
    client.onSubscribed = onSubscribed;

    // Set up connection message with username and password
    final connMessage = MqttConnectMessage()
        .withClientIdentifier(widget.pondName)
        .authenticateAs(
            'dc24', 'kmitl-dc24') // Use the provided username and password
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

      // Subscribe to topic
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

  void sendMessage(String message) {
    final builder = MqttClientPayloadBuilder();

    // Create the "hello" message in JSON format with UNIX timestamp
    final helloMessage = json.encode({
      "type": "hello",
      "sender": widget.pondName, // Use the pondName as sender
      "timestamp":
          DateTime.now().millisecondsSinceEpoch ~/ 1000, // UNIX timestamp
      "data": {}
    });

    builder.addString(helloMessage);

    client.publishMessage(topic, MqttQos.atLeastOnce, builder.payload!);
    setState(() {
      statusMessage = "Message sent: $helloMessage";
    });
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

  void startImageChangeTimer() {
    // Set a periodic timer to change the image every 3 seconds
    _imageChangeTimer = Timer.periodic(Duration(seconds: 1), (timer) {
      setState(() {
        _currentIndex =
            (_currentIndex + 1) % images.length; // Change index cyclically
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
            // Pond visual
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
            SizedBox(height: 60),
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
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                sendMessage("Hello from ${widget.pondName}!");
              },
              child: Text('Send "Hello"'),
            ),
          ],
        ),
      ),
    );
  }
}
