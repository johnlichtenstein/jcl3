"""
helper functions for jcl3
"""
import s3fs
import uuid
import os
from tarfile import TarFile
import tarfile

class Hopper(object):
    def __init__(self, objSet, hopperSize=8):
        self.toFetch = objSet
        self.hopperSet = set()
        self.hopperSize = hopperSize
        self.hopper = str(uuid.uuid4())
        os.mkdir(self.hopper)
        self.fs = s3fs.S3FileSystem(asynchronous=True)

    def fetch(self, obj):
        if len(self.hopperSet) < self.hopperSize:
            key = obj.split('/')[-1]
            self.fs.get(obj, self.hopper + '/' + key)
            self.hopperSet.add(obj)
            return None
        else:
            return None

    def remove(self, obj):
        key = obj.split('/')[-1]
        os.remove(self.hopper + '/' + key)
        self.hopperSet.remove(obj)
        return None

class Archive(object):
    def __init__(self, arname, objSet, hopperSize=8, workers=8, verbose=False, artype='tar', compress=False, compressLevel=9):
        self.arname = arname
        self.hopper = Hopper(objSet, hopperSize)
        self.workers = workers
        self.artype = artype
        self.compress = compress
        self.verbose = verbose
        self.compressLevel = compressLevel
        if self.format == 'tar':
            if self.compress:
                self.archive = TarFile(self.arname, mode='w:gz', format=tarfile.GNU_FORMAT)
            else:
                self.archive = TarFile(self.arname, mode='w', format=tarfile.GNU_FORMAT)
