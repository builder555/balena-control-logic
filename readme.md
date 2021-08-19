### Balena Blocks: binary logic

Subscribes to topics as inputs and provides a single output based on the specified logic gate

___Usage a block___

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
___Available variables___
- `inputs`: list of topics to subscribe to
- `output`: topic, under which to publish the output
- `gate`: logic to perform on the inputs

> ___N.B.___ list of topics must not have spaces!

___Available gates___

- 'and'
- 'or'
- 'nor'
- 'not' (when the input is single)

___Environment variables defaults___

- `inputs`: in1,in2
- `output`: output
- `gate`: or

___Tests___

```bash
$ PIPENV_VENV_IN_PROJECT=1 pipenv install --dev
$ pipenv shell
$ pytest -vs
```

___Standalone usage___

Given the code
```python
>>> from time import sleep
>>> logic_gate = MQTTLogic('input1', 'input2', 'input3')
>>> logic_gate.set_output(topic='output', method='and')
>>> while True:
>>>     sleep(0.1)
```
A message with payload '1' will be published under topic 'output' when all 3 topics (input1, 2, 3) receive message with payload '1'. Every time a message comes in, the output will be published, based on the current state.

> N.B. mqtt connects to host 'mqtt' on port 1883
