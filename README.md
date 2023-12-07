# debuglib-py

python debugger tool with easy integration into any program

> Installation currently only from source as the project is under development
> 
> To install the development version and test everything use:  
> `pip3 install git+https://github.com/utility-libraries/debuglib-py.git@dev#egg=debuglib[all]`

## Installation

[![PyPI - Version](https://img.shields.io/pypi/v/inifini)](https://pypi.org/project/inifini/)

```bash
pip install debuglib
pip install debuglib[all]  # recommended
```

| extra               | description                                                    | client/server |
|---------------------|----------------------------------------------------------------|---------------|
| `debuglib[dev]`     | better exceptions printing                                     | client        |
| `debuglib[orjson]`  | for faster packing/unpacking                                   | client/server |
| `debuglib[cli]`     | required to run the CLI Debugger                               | server        |
| `debuglib[all]`     | installs all of the ones above                                 | -             |

[//]: # (| `debuglib[msgpack]` | for possibly faster transmission speed through smaller packets | client+server |)

> Note: It's recommended to install all for the best debugging experience

### Why are there extras?

There are two reasons why some dependencies are marked as extra.

#### 1. Separation between script/program and debugger

Some dependencies are only used for the client/script and some are only used by the debugger (CLI).
In case you have different environments for both the dependencies work over extras

#### 2. To not overload the environment

The more dependencies your project has the likelier it is that version-conflicts arise or that your project gets to big.
`debuglib` tries to avoid that by requiring as few dependencies as possible but offers support for various packages for a better debugging experience.

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
    # the following is also possible for tiny performance boost
    # handlers=[logging.NullHandler() if prod else BlockingDebugHandler()],
)

logging.info("Hello World")
try:
    num = "Hi"
    print(int(num))
except ValueError as error:
    logging.error("failed to convert to integer", exc_info=error)
```

```bash
$ debuglib listen  # and start code.py in another terminal
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
my_function("debuglib")
my_function(name="debuglib")
```

```bash
$ debuglib listen  # and start code.py in another terminal
Listening on localhost:35353
New Connection from 127.0.0.1:43998 (localhost)
15:09:23.947665 | 127.0.0.1:43998 | INF | __main__.my_function() returned None after 6μs+803ns
15:09:23.947693 | 127.0.0.1:43998 | INF | __main__.my_function('debuglib') returned None after 2μs+234ns
15:09:23.947714 | 127.0.0.1:43998 | INF | __main__.my_function(name='debuglib') returned None after 2μs+405ns
Connection closed from 127.0.0.1:43998 (localhost)
```

### crash-hook

in case your program crashes, and you want to know the reason, you can install the custom excepthook

with the shortcut
```python
import debuglib.hook.install  # noqa
...
```

or the alternative/manual installation
```python
import debuglib.hook
...
debuglib.hook.hook()
```

```bash
$ debuglib listen  # and start code.py in another terminal
New Connection from 127.0.0.1:41302 (localhost)
15:09:23.528303 | 127.0.0.1:41302 | ERR | sys.excepthook
  File "/home/<user>/script.py", line 6, in <module>
    raise RuntimeError("testing error")

RuntimeError: testing error
--------------------------------------------------------------------------------
Connection closed from 127.0.0.1:41302 (localhost)
```
