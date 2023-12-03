# debuglib-py

python debugger tool with easy integration into any program

> Nothing is done yet

## Installation

[![PyPI - Version](https://img.shields.io/pypi/v/inifini)](https://pypi.org/project/inifini/)

```bash
pip install debuglib
```

| extra               | description                      |
|---------------------|----------------------------------|
| `debuglib[dev]`     | better exceptions printing       |
| `debuglib[msgpack]` | for possibly faster transmission |
| `debuglib[cli]`     | required to run the CLI Debugger |
| `debuglib[all]`     | installs all of the ones above   |

## Example

> Note: soon there will be integration with the logging module

`code.py`
```python
from debuglib.decorator import Decorator as DebugDecorator

debugger = DebugDecorator()

@debugger.monitor()
def my_function(name: str = "World"):
    print(f"Hello {name}")

my_function()
my_function(name="debuglib")
```

```bash
$ debuglib listen  # and start the script in another terminal
Listening on localhost:35353
New Connection from 127.0.0.1 (localhost)
15:09:23.947665 | 127.0.0.1 | __main__.my_function() returned None after 6.232000032468932e-06s
15:09:23.947714 | 127.0.0.1 | __main__.my_function(name='debuglib') returned None after 3.716999799507903e-06s
Connection closed from 127.0.0.1 (localhost)
```
