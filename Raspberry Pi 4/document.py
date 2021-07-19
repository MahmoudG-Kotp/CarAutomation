import os
import pickle


class Directory:
    @staticmethod
    def create(path: str, name: str):
        # Create new dir by (name) if dir not exist
        if not os.path.exists(path + name):
            os.mkdir(path + name)
            print(name + " Directory Created")
        return path + name + '/'

    @staticmethod
    def countFiles(path: str) -> int:
        if os.path.exists(path):
            # Files in dir path
            return len(os.listdir(path))
        return -1

    @staticmethod
    def remove(path: str, name: str):
        if os.path.exists(path + name):
            os.remove(path + name)
            print(name + " Directory Removed")

    @staticmethod
    def listFiles(path: str):
        if os.path.exists(path):
            # Files in dir path
            return os.listdir(path)
        return None


class File:
    __name = str
    __path = str

    def __init__(self, name: str, path: str, extension: str):
        if name.__contains__(extension):
            self.__name = name
        else:
            self.__name = name + extension
        self.__path = path
        self.__create()

    def __create(self):
        # Create New text file by (name, path) if name not exist
        if not os.path.exists(self.__path + self.__name):
            open(os.path.join(self.__path, self.__name), 'x').close()
            print(self.__name + " File Created")

    def __open(self, purpose: str):
        # Open file if path exist
        if os.path.exists(self.__path + self.__name):
            print(self.__name + " File Opened")
            return True, open(os.path.join(self.__path, self.__name), purpose)
        else:
            print(self.__name + " File Failed To Open!")
        return False, None

    def writeTextData(self, text: str):
        # 'w' overwrite
        # 'a' append
        is_opened, file = self.__open('w')
        if is_opened:
            file.write(text)
            file.close()
            print("Data Successfully Written")
        else:
            print("Failed To Write Data!")

    def writeBinaryData(self, data):
        is_opened, file = self.__open('wb')
        if is_opened:
            pickle.dump(data, file)
            file.close()
            print("Data Successfully Written")
        else:
            print("Failed To Write Data!")

    def readTextData(self) -> str:
        is_opened, file = self.__open('r')
        data = []
        if is_opened:
            data = file.readlines()
            file.close()
            print("Data Fetched")
            return data
        else:
            print("Failed To Fetch Data!")
        return "None"

    def readBinaryData(self):
        is_opened, file = self.__open('rb')
        if is_opened:
            data = pickle.load(file)
            file.close()
            print("Data Fetched")
            return data
        else:
            print("Failed To Fetch Data!")
        return None

    def remove(self):
        if os.path.exists(self.__path + self.__name):
            os.remove(self.__path + self.__name)
            print(self.__name + " File Removed")
        else:
            print(self.__name + " File Not Exist!")
