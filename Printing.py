from datetime import datetime
import os


class Printing(object):
    def __init__(self):

        self.enter_flag = 0

    def __enter__(self):
        self.enter_flag = 1
        now = datetime.now()
        suffix = now.strftime('%Y%m%d_%H%M')
        self.file_name = "./番剧信息_%s.txt" % (suffix)
        self.textStorage = open(self.file_name, "a+", encoding='utf-8')
        return self

    def __exit__(self, Type, value, traceback):
        if self.enter_flag:
            self.save()
            self.textStorage.close()
        else:
            os.remove(self.file_name)

    def write(self, content):
        self.textStorage.write("%s\n" % (content))

    def save(self):
        self.textStorage.flush()

    def read(self):
        ret = []
        old_pos = self.textStorage.tell()
        self.textStorage.seek(0)
        lines = self.textStorage.readlines()
        self.textStorage.seek(old_pos)
        idx = 0
        content = ""
        image_url = ""
        for line in lines:
            if idx == 0:
                content = line
                idx += 1
            elif idx == 1:
                image_url = line
                idx += 1
                ret.append((content, image_url))
            else:
                idx = 0
        return ret

    def seek(self, whence, offset):
        self.textStorage.seek(whence, offset)
