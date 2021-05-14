#-*- coding:utf-8 -*-
import json

class DictUpper(object):
	__slots__ = ["__funcs","__data"]
	def __init__(self):
		self.__funcs = {list:self._list, dict:self._dict}
		self.__data = list()

	@property
	def funcs(self):
		return self.__funcs

	def _dict( self, data ):
		val = dict()
		for dName, dVal in data.items():
			try :
				val[dName.upper()] = self.funcs[type(dVal)](dVal)
			except:
				val[dName.upper()] = dVal
		return val


	def _list( self, data ):
		val = list()
		for item in data:
			try :
				val.append(self.funcs[type(item)](item))
			except:
				val.append(item)
		return val

    #Multi data 처리
	def process( self, data ):
		return self.funcs[type(data)](data)

def isJson(data):
    try :
        json.loads(data)
    except ValueError :
        return False
    return True

def read(data):
	if isJson(data) == True :
		jData = json.loads(data)
        # Dict 경우 key의 값을 대문자로 변경한다.
		dictUpper = DictUpper()
		return dictUpper.process(jData)
	elif data.find("/") < 0 :
		raise ValueError("Not Supported Format [{0}]".format(data))

	with open(data,'r') as conf:
 		return json.loads(conf.read())

if __name__ == "__main__" :
	data = read('{"data":[{"key":"val", "key2":"val2", "KeY3":"Val3"}]}')
	print("result :",data)
	data = read('{"Data":[{"Key":"INVITE","vaL":"TTT","OpT":"T."}, {"key":"from","val":"ttfrom","opt":"T<"}]}')
	print("result :",data)