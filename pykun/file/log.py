#-*- coding : utf-8 -*-
class Distribute(object):
	def __init__(self):
		self.__layout = 0
		self.__funcs = {list:self._list, dict:self._dict}

	@property
	def funcs(self):
		return self.__funcs

	def _drowTab( self, tab, add=' |' ):
		add = add * tab
		return " {add}".format(**locals())

	def _dict( self, data, tab ):
		for idx, (dName, dVal) in enumerate(data.items(), 1):
			#print(self.__layout, tab)
			try :
				if self.__layout < tab :
					self.__layout = tab
					print("{0} {1}".format(self._drowTab(tab),type(data)))
				print("{0} \"{dName}\"".format(self._drowTab(tab), **locals()))
				self.funcs[type(dVal)](dVal, tab+1)
			except:
				if self.__layout > tab :
					self.__layout -= 1
				print("{0} | \"{dVal}\"<\'{dName} value\'>".format(self._drowTab(tab),**locals()))

	def _list( self, data, tab ):
		for item in data:
			#print(self.__layout, tab)
			try :
				if self.__layout < tab :
					self.__layout = tab
					print("{0} {1}".format(self._drowTab(tab),type(data)))
				self.funcs[type(item)](item, tab+1 )
			except:
				if self.__layout > tab :
					self.__layout -= 1
				print("{0} \"{item}\"".format(self._drowTab(tab), **locals()))

	def process( self, data ):
		self.funcs[type(data)](data, 1)


def display(data, title=None):
	if title == None :
		title = "Display"
	print("< {title} >".format(**locals()))
	distri = Distribute()
	distri.process(data)

if __name__ == "__main__" :
	display([1,2,3,4,5,6,[7],0,0,0, [8]])
	display({"key":[1,2,3,4,5,6,[7,{"InKey_val_array":[9,9,9,9]}],0,{"K":"v","K2":[10,9,8,7],"K3":"v3"},0,0,[8]]})