### Balena Blocks: logic

Subscribes to topics as inputs and provides a single output based on the specified logic gate

_Usage a block_

Add the following to your `docker-compose.yaml`:

```yaml
  control-logic:
    build: ./control-logic
    restart: always
    environment: 
      - inputs=sensor_1,button_1
      - output=logic_1
      - gate=or
```

_Available gates_

- 'and'
- 'or'
- 'nor' (also used as 'not' gate)

_Tests_

```bash
$ PIPENV_VENV_IN_PROJECT=1 pipenv install --dev
$ pipenv shell
$ pytest -vs
```

_Standalone usage_

Publish MQTT message when specified pin is activated/deactivated.

Given the code
```python
>>> from time import sleep
>>> logic_gate = MQTTLogic('input1', 'input2', 'input3')
>>> logic_gate.set_output(topic='output', method='and')
>>> while True:
>>>     sleep(0.1)
```
A message with payload '1' will be published under topic 'output' when all 3 topics (input1, 2, 3) receive message with payload '1'. Every time a message comes in, the output will be published, based on the current state.
