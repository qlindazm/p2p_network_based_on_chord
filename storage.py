import os


class FILE(object):
    '''A virtual file without a actual storage.

    Be referred to POSIX I/O standard, except the file statement (so there is no open(), close(), lseek(),...)
    Make sure you carefully considering the PageCache or Locks if you try to store the real file (ANSI C stdio or DB).

    Attributes:
        name: A str indicating the filename.
        content: The file's content.
    '''

    def __init__(self, name: str, content: str = ""):
        self.name = name
        self.content = content

    def read(self) -> str:
        return self.content

    def write(self, content: str) -> None:
        self.content = content


class StorageComponent(object):
    '''Manage files stored on server

    For simplification, there is only one dir (no cd(), mkdir(), cp(),...)
    While using virtual files, we consider there is always no file before the component start.
    '''
    def __init__(self):
        self.files = []

    def ls(self) -> list:
        return [file.name for file in self.files]

    def touch(self, fileName: str) -> None:
        self.files.append(FILE(fileName))

    def rm(self, fileName: str) -> str:
        tmp = [file for file in self.files if file.name == fileName]
        if len(tmp) == 0:
            return "No such file"
        self.files.remove(tmp[0])
        return "Succeed"

    def cat(self, fileName: str) -> str:
        tmp = [file for file in self.files if file.name == fileName]
        if len(tmp) == 0:
            return "No such file"
        return tmp[0].content

    def write(self, fileName: str, content: str) -> None:
        tmp = [file for file in self.files if file.name == fileName]
        tmp[0].write(content)
