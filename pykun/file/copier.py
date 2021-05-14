#-*- coding:utf-8 -*-
import sys
import os
import time
from os import path
import shutil
'''pkgs in Pykun'''
from pykun.file import log as logger
from pykun.file import configure as cfg

class MatchInfo(object):
	""" This Class is information carrier. 
		it's handled option about match key and convert value used in Reproducer 
	"""
	__solts__ = ["__convertKey", "__convertVal", "__option"]
	def __init__(self, convertKey, convertVal, option):
		self.__convertKey = convertKey
		self.__convertVal = convertVal
		self.__option = option

	def __str__(self):
		return "KEY:[{0}], VAL:[{1}], OPT:[{2}]".format(self.key, self.val, self.opt)

	@property
	def key(self):
		return self.__convertKey 
	@property
	def val(self):
		return self.__convertVal
	@property
	def opt(self):
		return self.__option


class Reproducer(object):
	""" This Class is Reproducer about file.
		Find the ''KEY'' value of ''MatchInfo'' in the file and change it to ''VAL'' according to ''OPT''.
		Create a file with the changed information.
	"""
	__slots__ = ["__factors", "__converts", "__match", "__writeOptionMap"]
	def __init__(self):
		self.__factors = list()
		self.__converts = list()
		self.__match = False
		self.__writeOptionMap = {
			"T^": self._textUp,
			"T_": self._textDown,
			"T<": self._textBefore,
			"T>": self._textAfter,
			"T.": self._textCurrent,
		}
	@property
	def factors(self):
		return self.__factors
	@factors.setter
	def factors(self, items):
		def _cvtToMatchInfoForDict():
			try :
				val = items["DATA"]
				if isinstance(val, list) == False :
					raise SyntaxError("Unknow Format")
				return val
			except KeyError :
				raise SyntaxError("Unknow Format")
		#make MatchInfo Instance
		for item in _cvtToMatchInfoForDict():
			self.__factors.append( MatchInfo(item["KEY"].encode("ascii"), item["VAL"].encode("ascii"), item["OPT"]))
	@property
	def converts(self):
		return self.__converts
	@converts.setter
	def converts(self, item):
		self.__converts.append(item)
	@property
	def match(self):
		return self.__match
	@match.setter
	def match(self, flag):
		self.__match = flag

	def __iter__(self):
		return iter(self.converts)

	def _textUp(self, line, mInfo):
		return "{0}\n{1}".format(mInfo.val.decode('ascii'), line.decode('ascii')).encode('ascii')

	def _textDown(self, line, mInfo):
		return "{0}{1}\n".format(line.decode('ascii'), mInfo.val.decode('ascii')).encode('ascii')

	def _textCurrent(self, line, mInfo):
		return line.replace(mInfo.key, mInfo.val)

	def _textBefore(self, line, mInfo):
		sPos = line.find(mInfo.key)
		return b"".join([line[:sPos], mInfo.val, line[sPos:]])

	def _textAfter(self, line, mInfo):
		sPos = line.find(mInfo.key)
		ePos = sPos + len(mInfo.key)
		return b"".join([line[:ePos], mInfo.val, line[ePos:]])

	def _convert(self, line, matchList):
		if len(matchList) <= 0 :
			return line

		self.match = True
		cvtLine = line
		for mInfo in matchList:
			cvtLine = self.__writeOptionMap[mInfo.opt](cvtLine, mInfo)
		return cvtLine

	def process(self, line):
		self.converts = self._convert( line, [mInfo for mInfo in self.factors if line.find(mInfo.key) > -1] )

	def write(self, path):
		os.rename(path, "{0}_{1}_bk".format(path, time.strftime('%Y_%m_%d_%X', time.localtime(time.time()))))
		with open(path, "wb") as w:
			for line in self:
				w.write(line)
		print("ok ... Write : {0}".format(path))

def makeIter( data ):
	if isinstance(data, dict) == True:
		data = data.items()
	for val in data :
		yield val

def convertFile(sPath, dPath, factors):
	if sPath.endswith("_bk") == True :
		return
	reproducer = Reproducer()
	reproducer.factors = factors
	with open(sPath, "rb") as p:
		for lino, line in enumerate(makeIter(p)):
			reproducer.process(line)
		if reproducer.match == True :
			reproducer.write(dPath)

def isDir( dirName ):
	rv = path.isdir(dirName)
	if rv == False :
		raise OSError("ERROR : Atrribute isn't Dir : {dirName}".format(**locals()))
	return dirName

def searchFilesInDir( dirName ):
	fNames = os.listdir(dirName)
	if len(fNames) == 0 :
		return []
	return fNames

def cvtFilesSrcToDest( src, dest, factors ):
	for name in searchFilesInDir(src):
		try :
			cvtFilesSrcToDest(
				isDir("{src}/{name}".format(**locals())),
				"{dest}/{name}".format(**locals()),
				factors
				)
			continue
		except OSError :
			pass
		except Exception as e:
			print(e)
		srcName = "{src}/{name}".format(**locals())
		destName = "{dest}/{name}".format(**locals())
		convertFile( srcName, destName, factors)

def compareLine( sIter, dIter ):
	return [ (lino, "SRC >>", sLine, "DEST >>", dLine) for lino, (sLine, dLine) in enumerate(zip(sIter, dIter)) if sLine != dLine ]

def diffFile_3x(srcPath, destPath):
	with open(srcPath, "rb") as s , open(destPath, "rb") as d:
		cmpResult = compareLine(makeIter(s), makeIter(d))
		if len(cmpResult) > 0 :
			print("find ... Different : {srcPath} - {destPath}".format(**locals()))
			logger.display(cmpResult, "Different")
			return True
	print("find ... Same : {srcPath} - {destPath}".format(**locals()))
	return False

def diffFile_2x(srcPath, destPath):
	with open(srcPath, "rb") as s :
		with open(destPath, "rb") as d:
			cmpResult = compareLine(makeIter(s), makeIter(d))
			if len(cmpResult) > 0 :
				print("find ... Different : {srcPath} - {destPath}".format(**locals()))
				logger.display(cmpResult, "Different")
				return True
	print("find ... Same : {srcPath} - {destPath}".format(**locals()))
	return False

def cpFilesSrcToDest( src, dest, prefix ) :
	diffFile = diffFile_2x
	from platform import python_version
	if python_version()[0] >= "3" : # version 3 
		diffFile = diffFile_3x

	for name in searchFilesInDir(src):
		try :
			cpFilesSrcToDest(
				isDir("{src}/{name}".format(**locals())),
				"{dest}/{name}".format(**locals()),
				prefix
				)
			continue
		except OSError:
			pass
		except Exception as e:
			print(e)
		if name.startswith(prefix) == True or prefix == False :
			srcName = "{src}/{name}".format(**locals())
			destName = "{dest}/{name}".format(**locals())
			if diffFile(srcName, destName) == True:
				print("ok ... Copy : {srcName} -> {destName}".format(**locals()))
				shutil.copy2(srcName, destName)

def copy(src, dest, prefix):
	""" Process Directory files Copy
		:param src : soruce directory 
		:param dest : destination directory
		:param prefix : start file name 
	"""
	try :
		cpFilesSrcToDest( src, dest, prefix )
	except Exception as e:
		print(e)

def convert(src, dest, factors):
	""" Process Directory files reproduce
		:param src : soruce directory 
		:param dest : destination directory
		:param factors : reproduce condition
	"""
	print("Process ...")
	try :
		cvtFilesSrcToDest(src, dest, cfg.read(factors))
	except Exception as e:
		print(e)

def quickHelp():
	print("Usege : copier [ option ] [ option arg ]")
	print("Option :")
	print("> cp - inputs [ src, dest, prefix ] ")
	print("> cvt - inputs [src, dest, factors ] ... cvt factors input format is json")
	print("> cvt factors format \'{\"DATA\":[{\"KEY\":\"CVT_MATCH_KEY\", \"VAL\":\"CVT_VAL\", \"OPT\":\"Insert Position\"}]}\' ")
	print("> cvt factors option ")
	print(">> [T^] - text added up")
	print(">> [T_] - text added down")
	print(">> [T<] - text before")
	print(">> [T>] - text after")
	print(">> [T.] - text convert")

def quickMain():
	try :
		src = sys.argv[2]
		dest = sys.argv[3]
		prefix = ""
		isDir(src)
		isDir(dest)
	except OSError as e:
		print(e)
		return 
	except IndexError as e:
		quickHelp()
		return 

	if sys.argv[1] == "cvt" :
		if len(sys.argv) >= 5 :
			factors = sys.argv[4]
		convert(src, dest, factors)
	elif sys.argv[1] == "cp" :
		prefix = False
		if len(sys.argv) >= 5 :
			prefix = sys.argv[4]
		copy(src, dest, prefix)
	else :
		quickHelp()

if __name__ == "__main__":
	quickMain()
