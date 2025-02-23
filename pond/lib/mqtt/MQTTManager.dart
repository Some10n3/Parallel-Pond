import 'package:mqtt_client/mqtt_client.dart';
import 'package:pond/mqtt/state/MQTTAppState.dart';

class MQTTManager {
  MQTTAppState _currentState;
  late MqttClient _client;
  String _identifier;
  String _host;
  int _port;
  String _username;
  String _password;
  String _topic;

  MQTTManager({
    required MQTTAppState state,
    required String identifier,
    required String host,
    required int port,
    required String username,
    required String password,
    required String topic,
  })  : _currentState = state,
        _identifier = identifier,
        _host = host,
        _port = port,
        _username = username,
        _password = password,
        _topic = topic;

  void initializeMQTTClient() {
    _client = MqttClient(_host, _identifier);
    _client.port = _port;
    _client.keepAlivePeriod = 20;
    _client.onDisconnected = onDisconnected;
    _client.onConnected = onConnected;
    _client.onSubscribed = onSubscribed;
    _client.logging(on: true);

    final MqttConnectMessage connMess = MqttConnectMessage()
        .withClientIdentifier(_identifier)
        .withWillTopic('willtopic')
        .withWillMessage('Client Disconnected')
        .startClean()
        .withWillQos(MqttQos.atLeastOnce)
        .authenticateAs(_username, _password); // Authentication

    print('MQTT client connecting....');
    _client.connectionMessage = connMess;
  }

  void connect() async {
    assert(_client != null);
    try {
      print('Example: MQTT client connecting....');
      _currentState.setappConnectionState(MQTTAppConnectionState.connecting);
      await _client.connect();
    } on Exception catch (e) {
      print('Example: Client exception - $e');
      disconnect();
    }
  }

  void disconnect() {
    print('MQTT client disconnecting....');
    _client.disconnect();
  }

  void publish(String message) {
    final MqttClientPayloadBuilder builder = MqttClientPayloadBuilder();
    builder.addString(message);
    if (builder.payload != null) {
      _client.publishMessage(_topic, MqttQos.exactlyOnce, builder.payload!);
    } else {
      print('Error: Payload is null');
    }
  }

  void onSubscribed(String topic) {
    print('Subscription confirmed for topic $topic');
  }

  void onDisconnected() {
    print('OnDisconnected client callback - Client disconnection');
    if (_client.connectionStatus?.returnCode ==
        MqttConnectReturnCode.connectionAccepted) {
      print('OnDisconnected callback is solicited, this is correct');
    }
    _currentState.setappConnectionState(MQTTAppConnectionState.disconnected);
  }

  void onConnected() {
    _currentState.setappConnectionState(MQTTAppConnectionState.connected);
    print('MQTT client connected');
    _client.subscribe(_topic, MqttQos.atLeastOnce);
    _client.updates?.listen((List<MqttReceivedMessage<MqttMessage>> c) {
      final MqttPublishMessage recMess = c[0].payload as MqttPublishMessage;
      final String pt =
          MqttPublishPayload.bytesToStringAsString(recMess.payload.message);
      _currentState.setReceivedText(pt);
      print(
          'Change notification:: topic is <${c[0].topic}>, payload is <-- $pt -->');
      print(' ');
    });
    print('OnConnected callback - Client connection was successful');
  }
}
