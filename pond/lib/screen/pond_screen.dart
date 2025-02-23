import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:pond/mqtt/state/MQTTAppState.dart';
import 'package:pond/mqtt/MQTTManager.dart';
import 'package:provider/provider.dart';

class PondScreen extends StatefulWidget {
  final String pondName;
  const PondScreen({super.key, required this.pondName});

  @override
  _PondScreenState createState() => _PondScreenState();
}

class _PondScreenState extends State<PondScreen> {
  final TextEditingController _hostTextController = TextEditingController();
  final TextEditingController _topicTextController = TextEditingController();
  final TextEditingController _messageTextController = TextEditingController();
  late MQTTAppState currentAppState;
  late MQTTManager manager;

  @override
  void initState() {
    super.initState();
    // Initialize the manager with the provided MQTT server details
    currentAppState = MQTTAppState();
    manager = MQTTManager(
      state: currentAppState,
      identifier: 'ios', // Use a unique client identifier
      host: '40.90.169.126', // The MQTT broker IP address
      port: 1883, // The MQTT broker port
      username: 'dc24', // MQTT username
      password: 'kmitl-dc24', // MQTT password
      topic: 'fishhaven/stream', // The topic to subscribe/publish
    );
    manager.initializeMQTTClient();
    manager.connect();
  }

  @override
  void dispose() {
    _hostTextController.dispose();
    _topicTextController.dispose();
    _messageTextController.dispose();
    super.dispose();
  }

  _printLatestValue() {
    print('Second text field: ${_hostTextController.text}');
    print('Second text field: ${_topicTextController.text}');
    print('Second text field: ${_messageTextController.text}');
  }

  @override
  Widget build(BuildContext context) {
    final appState = Provider.of<MQTTAppState>(context);
    currentAppState = appState;
    var scaffold = Scaffold(
        appBar: _buildAppBar(context) as PreferredSizeWidget,
        body: _buildColumn());
    return scaffold;
  }

  Widget _buildAppBar(BuildContext context) {
    return AppBar(
      title: Text('Fish Haven - Pond'),
      backgroundColor: Colors.blue,
    );
  }

  Widget _buildColumn() {
    return Column(
      children: <Widget>[
        _buildConnectionStateText(_prepareStateMessageFrom(
            currentAppState.getAppConnectionState ??
                MQTTAppConnectionState.disconnected)),
        _buildEditableColumn(),
        _buildScrollableTextWith(currentAppState.getHistoryText),
      ],
    );
  }

  Widget _buildEditableColumn() {
    return Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: <Widget>[
            _buildTextFieldWith(
                _hostTextController,
                'Enter broker address',
                currentAppState.getAppConnectionState ??
                    MQTTAppConnectionState.disconnected),
            SizedBox(height: 20),
            _buildTextFieldWith(
                _topicTextController,
                'Enter a topic to subscribe or listen',
                currentAppState.getAppConnectionState ??
                    MQTTAppConnectionState.disconnected),
            SizedBox(height: 20),
            _buildTextFieldWith(
                _messageTextController,
                'Enter a message to publish',
                currentAppState.getAppConnectionState ??
                    MQTTAppConnectionState.disconnected),
          ],
        ));
  }

  Widget _buildTextFieldWith(TextEditingController controller, String hintText,
      MQTTAppConnectionState state) {
    bool shouldEnable = false;
    if (controller == _messageTextController &&
        state == MQTTAppConnectionState.connected) {
      shouldEnable = true;
    } else if (controller == _hostTextController &&
        state == MQTTAppConnectionState.disconnected) {
      shouldEnable = true;
    } else if (controller == _topicTextController &&
        state == MQTTAppConnectionState.disconnected) {
      shouldEnable = true;
    }

    return TextField(
      enabled: shouldEnable,
      controller: controller,
      decoration: InputDecoration(
        contentPadding: EdgeInsets.only(left: 0, bottom: 0, top: 0, right: 0),
        labelText: hintText,
      ),
    );
  }

  Widget _buildConnectionStateText(String state) {
    return Row(
      children: <Widget>[
        Expanded(
          child: Container(
            color: Colors.deepOrangeAccent,
            child: Center(
              child: Text(
                state,
                style: TextStyle(fontSize: 24),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildScrollableTextWith(String text) {
    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Container(
        width: 400,
        height: 300,
        child: SingleChildScrollView(
          child: Text(text),
        ),
      ),
    );
  }
}

String _prepareStateMessageFrom(MQTTAppConnectionState state) {
  switch (state) {
    case MQTTAppConnectionState.connected:
      return 'Connected';
    case MQTTAppConnectionState.connecting:
      return 'Connecting';
    case MQTTAppConnectionState.disconnected:
      return 'Disconnected';
    default:
      return 'Error';
  }
}
