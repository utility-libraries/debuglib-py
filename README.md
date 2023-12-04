# debuglib-py

python debugger tool with easy integration into any program

> Installation currently only from source as the project is under development
> 
> To install the development version and test everything use:  
> `pip3 install git+https://github.com/utility-libraries/debuglib-py.git@dev#egg=debuglib[dev]`

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

## Examples

> Note: there is no need for a server to run/exist.
> That way you don't have to change anything when going into production
> but would still have the option to monitor when errors occur.

### 1: logging

`code.py`
```python
import logging
from debuglib.logging import BlockingDebugHandler

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[BlockingDebugHandler()],
)

logging.info("Hello World")
try:
    num = "Hi"
    print(int(num))
except ValueError as error:
    logging.error("failed to convert to integer", exc_info=error)
```

```bash
$ debuglib listen  # and start the script in another terminal
New Connection from 127.0.0.1 (localhost)
23:48:42.183558 | 127.0.0.1 | INFO | Hello World
23:48:42.184598 | 127.0.0.1 | ERROR | failed to convert to integer
--------------------------------------------------------------------------------
  File "/home/<user>/code.py", line 12, in <module>
    print(int(num))
              └ 'Hi'

ValueError: invalid literal for int() with base 10: 'Hi'
================================================================================
Connection closed from 127.0.0.1 (localhost)
```

### 2: function monitoring

> Note: the monitor decorator

`code.py`
```python
from debuglib.decorator import Decorator as DebugDecorator
# from debuglib.decorator import monitor  # shorthand if you only use it once

# better performance than the single `monitor` decorator as everything 
# registered with debugger.monitor() shares the same connection
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
