import paho.mqtt.client as mqtt
import json
from time import sleep
import os

class MQTTLogic:

    def __init__(self, *inputs):
        self.__input_topics = inputs
        self.__client = mqtt.Client()
        self.__client.on_message = self.__on_message
        self.__client.on_connect = self.__on_connect
        self.__client.connect('mqtt', 1883, keepalive=60)
        self.__client.loop_start()
        self.__input_values = {input: False for input in inputs}

    def set_output(self, topic, method):
        assert not topic in self.__input_values, 'Output must not be one of the inputs'
        self.__topic = topic
        if method=='or':
            self.output = self.__or
        elif method=='nor' or method=='not':
            self.output = self.__nor
        elif method=='and':
            self.output = self.__and

    def __and(self):
        return int(all(self.__input_values.values()))

    def __or(self):
        return int(any(self.__input_values.values()))

    def __nor(self):
        return int(not self.__or())

    def __on_message(self, client, userdata, msg):
        if msg.topic in self.__input_values:
            self.__input_values[msg.topic] = json.loads(msg.payload)
            self.__publish_output()

    def __on_connect(self, *a, **kw):
        sub_to = list(zip(self.__input_topics, [1]*len(self.__input_topics)))
        self.__client.subscribe(sub_to)

    def __publish_output(self):
        self.__client.publish(self.__topic, payload=json.dumps(self.output()))

if __name__=='__main__':
    inputs = os.environ.get('INPUTS','in1,in2').strip().split(',')
    output = os.environ.get('OUTPUT','output')
    gate = os.environ.get('GATE','or')
    logic_gate = MQTTLogic(*inputs)
    logic_gate.set_output(topic=output, method=gate)
    while True:
        sleep(0.1)