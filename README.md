# pykun
Develop a Callection of useful packages

[![PyPI version](https://badge.fury.io/py/pykun.svg)](https://badge.fury.io/py/pykun)

## # Gool 
---
```
Easy to use features.
```
## # Install
--- 
```python 
pip install pykun
```

## # Usage
--- 
### **1. Packages : file**
```python
from pykun.file import copier
copier.quickMain()

from pykun.file import configure as cfg
cfg.read()

from pykun.file import log as logger
logger.display(list() or dict())
```

#### **1.1 Module : copier**
This Module is to give file copy in accordance with option.

- #### `quickMain()`
	: fast-forward run function
```python
>>> quickMain()

Usege : copier [ option ] [ option arg ]
Option :
> diffcp - inputs [ src, dest, prefix ]
> cvt - inputs [src, dest, factors ] ... cvt factors input format is json
> cvt factors format '{"DATA":[{"KEY":"CVT_MATCH_KEY", "VAL":"CVT_VAL", "OPT":"Insert Position"}]}'
> cvt factors option
>> [T^] - text added up
>> [T_] - text added down
>> [T<] - text before
>> [T>] - text after
>> [T.] - text convert
```

#### **1.2 Module : configure**
This Module is current to give functions

- #### `read()`
	: param : file path or json string
```python
>>> data = read('{"data":[{"key":"val", "key2":"val2", "KeY3":"Val3"}]}')
>>> print("result :",data)
>>> data = read('{"Data":[{"Key":"INVITE","vaL":"TTT","OpT":"T."}, {"key":"from","val":"ttfrom","opt":"T<"}]}')
>>> print("result :",data)

result : {'DATA': [{'KEY': 'val', 'KEY2': 'val2', 'KEY3': 'Val3'}]}
result : {'DATA': [{'KEY': 'INVITE', 'VAL': 'TTT', 'OPT': 'T.'}, {'KEY': 'from', 'VAL': 'ttfrom', 'OPT': 'T<'}]}
```

#### **1.3 Module : log**
This Module is current to give functions

 - #### `display()`
	: param : list or dict 
```python
>>> display([1,2,3,4,5,6,[7],0,0,0, [8]])
>>> display({"key":[1,2,3,4,5,6,[7,{"InKey_val_array":[9,9,9,9]}],0,{"K":"v","K2":[10,9,8,7],"K3":"v3"},0,0,[8]]})

< Display >
  | <class 'list'>
  | "1"
  | "2"
  | "3"
  | "4"
  | "5"
  | "6"
  | | <class 'list'>
  | | "7"
  | "0"
  | "0"
  | "0"
  | | <class 'list'>
  | | "8"
< Display >
  | <class 'dict'>
  | "key"
  | | <class 'list'>
  | | "1"
  | | "2"
  | | "3"
  | | "4"
  | | "5"
  | | "6"
  | | | <class 'list'>
  | | | "7"
  | | | | <class 'dict'>
  | | | | "InKey_val_array"
  | | | | | <class 'list'>
  | | | | | "9"
  | | | | | "9"
  | | | | | "9"
  | | | | | "9"
  | | "0"
  | | | "K"
  | | | | "v"<'K value'>
  | | | "K2"
  | | | | <class 'list'>
  | | | | "10"
  | | | | "9"
  | | | | "8"
  | | | | "7"
  | | | "K3"
  | | | | "v3"<'K3 value'>
  | | "0"
  | | "0"
  | | | <class 'list'>
  | | | "8"
```
