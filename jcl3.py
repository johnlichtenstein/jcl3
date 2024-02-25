"""
helper functions for jcl3
"""
import s3fs
import uuid
import os
from tarfile import TarFile
import tarfile
from datetime import datetime as dt
import time


class Hopper(object):
    def __init__(self, objSet, hopperSize=8):
        self.toFetch = objSet
        self.hopperSet = set()
        self.hopperSize = hopperSize
        self.hopper = str(uuid.uuid4())
        os.mkdir(self.hopper)
        self.fs = s3fs.S3FileSystem()

    def fetch(self, obj):
        if len(self.hopperSet) < self.hopperSize:
            key = obj.split("/")[-1]
            self.fs.get(obj, self.hopper + "/" + key)
            self.hopperSet.add(obj)
            return None
        else:
            return None

    def remove(self, obj):
        key = obj.split("/")[-1]
        os.remove(self.hopper + "/" + key)
        self.hopperSet.remove(obj)
        return None


class Archive(object):
    def __init__(
        self,
        arname,
        objSet,
        hopperSize=8,
        workers=8,
        verbose=False,
        artype="tar",
        compress=False,
        compressLevel=9,
    ):
        self.arname = arname
        self.hopper = Hopper(objSet, hopperSize)
        self.workers = workers
        self.artype = artype
        self.compress = compress
        self.verbose = verbose
        self.compressLevel = compressLevel
        self.done = False
        if self.artype == "tar":
            if self.compress:
                self.archive = TarFile(
                    self.arname, mode="w:gz", format=tarfile.GNU_FORMAT
                )
            else:
                self.archive = TarFile(
                    self.arname, mode="w", format=tarfile.GNU_FORMAT
                )

    def fetchOne(self):
        if len(self.hopper.hopperSet) < self.hopper.hopperSize:
            obj = self.hopper.toFetch.pop()
            self.hopper.fetch(obj)
            return None

    def add(self):
        try:
            item = self.hopper.hopperSet.pop()
        except KeyError:
            return None
        key = item.split("/")[-1]
        if self.artype == "tar":
            self.archive.add(self.hopper.hopper + "/" + key, arcname=key)
        return None

    def doMore(self):
        for j in range(len(self.hopper.hopperSet), self.hopper.hopperSize):
            # try:
            #     self.fetchOne()
            # except:
            #     pass
            self.fetchOne()
        self.add()
        if len(self.hopper.hopperSet) == 0:
            if len(self.hopper.toFetch) == 0:
                self.done = True
        return None

    def close(self):
        if self.artype == "tar":
            self.archive.close()
        os.rmdir(self.hopper.hopper)
        return None


if __name__ == "__main__":
    testL = """s3://datadeloro-regab/state/extract/0000929638-17-000295_1126530_32968_57.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000295_1694920_32968_57.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000314_1126530_32968_57.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000314_1694920_32968_57.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000459_1694920_32968_59.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000514_1694920_32955_59.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000577_1694920_32951_59.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000669_1694920_32949_61.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000710_1694920_32947_61.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000742_1694920_32945_61.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000769_1126530_42854_59.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000769_1716665_42854_59.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000806_1694920_32939_61.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000885_1694920_32938_61.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000886_1716665_33054_59.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000917_1694920_32932_61.parquet
s3://datadeloro-regab/state/extract/0000929638-17-000919_1716665_33043_59.parquet
s3://datadeloro-regab/state/extract/0000929638-18-000030_1136586_55710_66.parquet
s3://datadeloro-regab/state/extract/0000929638-18-000030_1725617_55710_66.parquet
s3://datadeloro-regab/state/extract/0000929638-18-000122_1694920_32926_61.parquet
s3://datadeloro-regab/state/extract/0000929638-18-000123_1716665_33041_59.parquet
s3://datadeloro-regab/state/extract/0000929638-18-000320_1694920_32923_61.parquet
s3://datadeloro-regab/state/extract/0000929638-18-000321_1716665_33036_61.parquet
s3://datadeloro-regab/state/extract/0000929638-18-000322_1725617_53449_66.parquet
s3://datadeloro-regab/state/extract/0000929638-18-000429_1694920_32917_61.parquet
s3://datadeloro-regab/state/extract/0000929638-18-000430_1716665_33032_61.parquet
s3://datadeloro-regab/state/extract/0000929638-18-000431_1725617_53447_66.parquet
s3://datadeloro-regab/state/extract/0000929638-18-000483_1725617_53443_66.parquet
s3://datadeloro-regab/state/extract/0000929638-18-000484_1694920_32914_61.parquet
s3://datadeloro-regab/state/extract/0000929638-18-000485_1716665_33026_61.parquet
""".split(
        "\n"
    )
    archive = Archive("examples.tar", set(testL))
    print(dt.now().strftime("%H:%M:%S"), len(archive.hopper.toFetch))
    obj = testL.pop(0)
    key = obj.split("/")[-1]

    # help(archive.hopper.fs.get())
    # archive.hopper.fs.get(obj, archive.hopper.hopper + "/" + key)
    # domoreCount = 0
    # while not archive.done:
    #     archive.doMore()
    #     domoreCount += 1
    #     print(dt.now().strftime("%H:%M:%S"), domoreCount
    #           , len(archive.hopper.hopperSet), archive.hopper.hopperSize)
    #     time.sleep(1)

    archive.close()
    print("done")
