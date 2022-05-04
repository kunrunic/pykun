# -*- coding:utf-8 -*-

import sys
import os
import time
from os import path
import shutil

'''package in Pykun'''
from pykun.file import log as logger
from pykun.file import configure as cfg


class MatchInfo(object):
    """
    This Class is information carrier.
    it's handled option about match key and convert value used in Reproducer
    """

    __slots__ = ["__convertKey", "__convertVal", "__option"]

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
    """
    This Class is Reproducer about file.
    Find the ''KEY'' value of ''MatchInfo'' in the file and change it to ''VAL'' according to ''OPT''.
    Create a file with the changed information.
    """

    __slots__ = ["__factors", "__converts", "__match", "__writeOptionMap", "__CONST_REMOVE"]

    def __init__(self):
        self.__factors = list()
        self.__converts = list()
        self.__match = False
        self.__writeOptionMap = {
            "Tu": self._textUp,
            "Td": self._textDown,
            "Tb": self._textBefore,
            "Ta": self._textAfter,
            "Tc": self._textCurrent,
            "Tl": self._textLineRemove,
        }
        self.__CONST_REMOVE = "&_R-E*M+0?(V)E$%"

    @property
    def _const_remove(self):
        return self.__CONST_REMOVE

    @property
    def factors(self):
        return self.__factors

    @factors.setter
    def factors(self, items):

        def _cvtToMatchInfoForDict():
            try:
                val = items["DATA"]

                if not isinstance(val, list):
                    raise SyntaxError("Unknown Format")
                return val

            except KeyError:
                raise SyntaxError("Unknown Format")

        # make MatchInfo Instance
        for item in _cvtToMatchInfoForDict():
            self.__factors.append(MatchInfo(item["KEY"].encode("ascii"), item["VAL"].encode("ascii"), item["OPT"]))

    @property
    def converts(self):
        return self.__converts

    @converts.setter
    def converts(self, item):
        if item != self._const_remove:
            self.__converts.append(item)

    @property
    def match(self):
        return self.__match

    @match.setter
    def match(self, flag):
        self.__match = flag

    def __iter__(self):
        return iter(self.converts)

    @staticmethod
    def _textUp(line, mInfo):
        return "{0}\n{1}".format(mInfo.val.decode('ascii'), line.decode('ascii')).encode('ascii')

    @staticmethod
    def _textDown(line, mInfo):
        return "{0}{1}\n".format(line.decode('ascii'), mInfo.val.decode('ascii')).encode('ascii')

    @staticmethod
    def _textCurrent(line, mInfo):
        return line.replace(mInfo.key, mInfo.val)

    @staticmethod
    def _textBefore(line, mInfo):
        sPos = line.find(mInfo.key)
        return b"".join([line[:sPos], mInfo.val, line[sPos:]])

    @staticmethod
    def _textAfter(line, mInfo):
        sPos = line.find(mInfo.key)
        ePos = sPos + len(mInfo.key)
        return b"".join([line[:ePos], mInfo.val, line[ePos:]])

    @classmethod
    def _textLineRemove(cls, line, mInfo):
        return cls._const_remove

    def _convert(self, line, matchList):
        if len(matchList) <= 0:
            return line

        self.match = True
        cvtLine = line
        for mInfo in matchList:
            cvtLine = self.__writeOptionMap[mInfo.opt](cvtLine, mInfo)
            if cvtLine == self._const_remove:
                break  # find remove const stopped loop
        return cvtLine

    def process(self, line):
        self.converts = self._convert(line, [mInfo for mInfo in self.factors if line.find(mInfo.key) > -1])

    def write(self, path):
        os.rename(path, "{0}_{1}_bk".format(path, time.strftime('%Y_%m_%d_%X', time.localtime(time.time()))))
        with open(path, "wb") as w:
            for line in self:
                w.write(line)
        print("ok ... Write : {0}".format(path))


def makeIter(data):
    if isinstance(data, dict):
        data = data.items()
    for val in data:
        yield val


def convertFile(sPath, dPath, factors):
    if sPath.endswith("_bk"):
        return
    reproducer = Reproducer()
    reproducer.factors = factors
    with open(sPath, "rb") as p:
        for lino, line in enumerate(makeIter(p)):
            reproducer.process(line)
        if reproducer.match:
            reproducer.write(dPath)


def isDir(dirName):
    rv = path.isdir(dirName)
    if not rv:
        raise OSError("ERROR : Attribute isn't Dir : {dirName}".format(**locals()))
    return dirName


def searchFilesInDir(dirName):
    fNames = os.listdir(dirName)
    if len(fNames) == 0:
        return []
    return fNames


def cvtFilesSrcToDst(src, dst, factors):
    for name in searchFilesInDir(src):
        try:
            cvtFilesSrcToDst(
                isDir("{src}/{name}".format(**locals())),
                "{dst}/{name}".format(**locals()),
                factors
            )
            continue
        except OSError:
            pass
        except Exception as e:
            print(e)
        srcName = "{src}/{name}".format(**locals())
        dstName = "{dst}/{name}".format(**locals())
        convertFile(srcName, dstName, factors)


def compareLine(sIter, dIter):
    return [(lino, "SRC >>", sLine, "DST >>", dLine) for lino, (sLine, dLine) in enumerate(zip(sIter, dIter)) if
            sLine != dLine]


def diffFile(srcPath, dstPath):
    with open(srcPath, "rb") as s:
        with open(dstPath, "rb") as d:
            cmpResult = compareLine(makeIter(s), makeIter(d))
            if len(cmpResult) > 0:
                print("find ... Different : {srcPath} - {dstPath}".format(**locals()))
                logger.display(cmpResult, "Different")
                return True
    print("find ... Same : {srcPath} - {dstPath}".format(**locals()))
    return False


def cpFilesSrcToDst(src, dst, prefix):
    for name in searchFilesInDir(src):
        try:
            cpFilesSrcToDst(
                isDir("{src}/{name}".format(**locals())),
                "{dst}/{name}".format(**locals()),
                prefix
            )
            continue
        except OSError:
            pass
        except Exception as e:
            print(e)
        if name.endswith("_bk"):
            return

        def isPrefix():
            if isinstance(prefix, bool):
                return True
            return name.startswith(prefix)

        if isPrefix():
            srcName = "{src}/{name}".format(**locals())
            dstName = "{dst}/{name}".format(**locals())
            if diffFile(srcName, dstName):
                os.rename(dstName,
                          "{0}_{1}_bk".format(dstName, time.strftime('%Y_%m_%d_%X', time.localtime(time.time()))))
                print("ok ... Copy : {srcName} -> {dstName}".format(**locals()))
                shutil.copy2(srcName, dstName)


def copy(src, dst, prefix):
    """
    Process Directory files Copy
     :param src : source directory
     :param dst : destination directory
     :param prefix : start file name
    """

    try:
        cpFilesSrcToDst(src, dst, prefix)
    except Exception as e:
        print(e)


def convert(src, dst, factors):
    """
    Process Directory files reproduce
     :param src : source directory
     :param dst : destination directory
     :param factors : reproduce condition
    """

    print("Process ...")
    try:
        cvtFilesSrcToDst(src, dst, cfg.read(factors))
    except Exception as e:
        print(e)


def quickHelp():
    print("Usage : copier [ option ] [ option arg ]")
    print("Option :")
    print("> diffcp - inputs [ src, dst, prefix ] ")
    print("> cvt - inputs [src, dst, factors ] ... cvt factors input format is json")
    print("> cvt factors format ")
    print("\'{\"DATA\":[{\"KEY\":\"CVT_MATCH_KEY\", \"VAL\":\"CVT_VAL\", \"OPT\":\"Insert Position\"}]}\' ")
    print("> cvt factors option ")
    print(">> [T^] - text added up")
    print(">> [T_] - text added down")
    print(">> [T<] - text before")
    print(">> [T>] - text after")
    print(">> [T.] - text convert")
    print(">> [T-] - text line remove")


def quickMain():
    try:
        src = sys.argv[2]
        dst = sys.argv[3]
        isDir(src)
        isDir(dst)
    except OSError as e:
        print(e)
        return
    except IndexError:
        quickHelp()
        return

    factors = None
    if sys.argv[1] == "cvt":
        if len(sys.argv) >= 5:
            factors = sys.argv[4]
        convert(src, dst, factors)
    elif sys.argv[1] == "diffcp":
        prefix = False
        if len(sys.argv) >= 5:
            prefix = sys.argv[4]
        copy(src, dst, prefix)
    else:
        quickHelp()


if __name__ == "__main__":
    quickMain()
