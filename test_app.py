import app
import pytest
from unittest.mock import MagicMock, patch

class TestAsyncMQTTLogic:

    def test_subscribes_to_specified_input_signals_after_connecting(self, fake_mqtt):
        with patch('app.mqtt', new=fake_mqtt):
            app.MQTTLogic('in1', 'in2')
            fake_mqtt.simulate_connection()
            assert fake_mqtt.is_subscribed_to('in1')
            assert fake_mqtt.is_subscribed_to('in2')

    def test_publishes_under_specified_topic(self, fake_mqtt):
        with patch('app.mqtt', new=fake_mqtt):
            logic = app.MQTTLogic('in1','in2')
            logic.set_output(topic='logic-result', method='and')
            fake_mqtt.simulate_publish('in1', '0')
            assert fake_mqtt.published_topic() == 'logic-result'

    def test_NOR_operation_publishes_0_when_any_input_is_TRUTHY(self, fake_mqtt):
        with patch('app.mqtt', new=fake_mqtt):
            logic = app.MQTTLogic('in1','in2')
            logic.set_output(topic='logic-result', method='nor')
            fake_mqtt.simulate_publish('in1', '0')
            fake_mqtt.simulate_publish('in1', '1')
            assert fake_mqtt.published_payload() == '0'

    def test_NOR_operation_publishes_1_when_all_inputs_are_FALSY(self, fake_mqtt):
        with patch('app.mqtt', new=fake_mqtt):
            logic = app.MQTTLogic('in1','in2')
            logic.set_output(topic='logic-result', method='nor')
            fake_mqtt.simulate_publish('in1', '0')
            fake_mqtt.simulate_publish('in1', '0')
            assert fake_mqtt.published_payload() == '1'

    def test_NOR_used_as_NOT_gate(self, fake_mqtt):
        with patch('app.mqtt', new=fake_mqtt):
            logic = app.MQTTLogic('in1')
            logic.set_output(topic='logic-result', method='not')
            fake_mqtt.simulate_publish('in1', '1')
            assert fake_mqtt.published_payload() == '0'
            fake_mqtt.simulate_publish('in1', '0')
            assert fake_mqtt.published_payload() == '1'

    def test_OR_operation_publishes_1_when_any_input_is_TRUTHY(self, fake_mqtt):
        with patch('app.mqtt', new=fake_mqtt):
            logic = app.MQTTLogic('in1', 'in2')
            logic.set_output(topic='logic-result', method='or')
            fake_mqtt.simulate_publish('in1', '1')
            fake_mqtt.simulate_publish('in2', '0')
            assert fake_mqtt.published_payload() == '1'

    def test_OR_operation_publishes_0_when_all_inputs_are_FALSY(self, fake_mqtt):
        with patch('app.mqtt', new=fake_mqtt):
            logic = app.MQTTLogic('in1', 'in2')
            logic.set_output(topic='logic-result', method='or')
            fake_mqtt.simulate_publish('in1', '0')
            fake_mqtt.simulate_publish('in2', '0')
            assert fake_mqtt.published_payload() == '0'

    def test_AND_operation_publishes_1_when_all_inputs_are_TRUE(self, fake_mqtt):
        with patch('app.mqtt', new=fake_mqtt):
            logic = app.MQTTLogic('in1', 'in2')
            logic.set_output(topic='logic-result', method='and')
            fake_mqtt.simulate_publish('in1', '1')
            fake_mqtt.simulate_publish('in2', '1')
            assert fake_mqtt.published_payload() == '1'

    def test_AND_operation_publishes_0_when_any_input_is_FALSE(self, fake_mqtt):
        with patch('app.mqtt', new=fake_mqtt):
            logic = app.MQTTLogic('in1', 'in2')
            logic.set_output(topic='logic-result', method='and')
            fake_mqtt.simulate_publish('in1', '1')
            fake_mqtt.simulate_publish('in2', '0')
            assert fake_mqtt.published_payload() == '0'

    def test_ensure_pub_sub_loop_is_not_created(self, fake_mqtt):
        with patch('app.mqtt', new=fake_mqtt), pytest.raises(Exception):
            logic = app.MQTTLogic('in1', 'in2')
            logic.set_output(topic='in1', method='and')


@pytest.fixture
def fake_mqtt():

    class FakeClient:

        def __init__(self):
            self.__subscribed_to = []
            self.last_msg = {}
            self.on_message = lambda *a, **kw: None
            self.on_connect = lambda *a, **kw: None

        def connect(self, *a, **kw):
            pass

        def subscribe(self, topics):
            self.__subscribed_to = topics

        def publish(self, topic, payload, *a, **kw):
            self.last_msg = {'topic': topic, 'payload': payload}
            fake_msg = MagicMock(topic=topic, payload=payload)
            self.on_message(None, None, fake_msg)
            return MagicMock(is_published=lambda: True)

        def loop_start(self):
            pass

        def is_subscribed(self, topic):
            for subbed in self.__subscribed_to:
                if subbed[0] == topic:
                    return True
            return False

    c = FakeClient()
    mqtt = MagicMock(simulate_publish=c.publish, Client=lambda: c)
    mqtt.is_subscribed_to = lambda topic: c.is_subscribed(topic)
    mqtt.published_topic = lambda: c.last_msg['topic']
    mqtt.published_payload = lambda: c.last_msg['payload']
    mqtt.simulate_connection = lambda: c.on_connect()
    return mqtt
