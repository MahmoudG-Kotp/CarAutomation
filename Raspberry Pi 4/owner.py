import face_recognition
from document import File
from document import Directory


class Owner:
    # Owner Data
    __name = str
    __shirt_color = str
    __face_samples_path = str
    __samples_encodings_default_path = str
    __owner_data_file = File

    def __init__(self, name: str, face_samples_path: str):
        self.__name = name.lower()
        self.__face_samples_path = "owners_data/owner_samples/" + face_samples_path
        self.__samples_encodings_default_path = Directory.create(self.__face_samples_path, "encodings")
        self.__saveData()

    def __saveData(self):
        # Create owner directory if not created yet
        dir_path = Directory.create("owners_data/", self.__name + "_data")
        # Create new file for owner data
        self.__owner_data_file = File(self.__name + "_data", dir_path, ".txt")
        # Count face samples in the given path
        samples_count = Directory.countFiles(self.__face_samples_path)
        # Get old count of samples
        encoded_samples_count = Directory.countFiles(self.__samples_encodings_default_path)
        if encoded_samples_count > -1:
            samples_count -= 1  # Minus one cause encodings directory will be counted
        # If samples count changed encode from the beginning
        if encoded_samples_count != samples_count:
            self.__encodeSamples()
            print(self.__name + " Samples Encoded")
            # Write (name of owner + count of samples)
            self.__owner_data_file.writeTextData(
                ".Owner Name:\n" + self.__name +
                "\n.Samples Count:\n" + str(samples_count) +
                "\n.Shirt Color:\n" + "None")

    def __encodeSamples(self):
        sample_counter = 0
        for sample_file in Directory.listFiles(self.__face_samples_path):
            if not sample_file.__contains__("encodings"):
                sample_counter += 1
                sample_encodings = \
                    face_recognition.face_encodings(
                        face_recognition.load_image_file(self.__face_samples_path + sample_file))[0]
                File("encoding_" + str(sample_counter), self.__samples_encodings_default_path, ".dat").writeBinaryData(
                    sample_encodings)

        encoded_samples_count = Directory.countFiles(self.__samples_encodings_default_path)
        # If encoded samples more than samples delete the extras
        while encoded_samples_count > sample_counter:
            sample_counter += 1
            File("encoding_" + str(sample_counter), self.__samples_encodings_default_path, ".dat").remove()

    def getName(self) -> str:
        return self.__name

    def saveShirtColor(self, color: str):
        if self.__owner_data_file and color is not None:
            self.__shirt_color = color
            written_data = ""
            # Detect color line in text
            is_this_color_line = False  # Detect color line in text
            for text in self.__owner_data_file.readTextData():
                # If color and saved color are same no need to write it again
                if is_this_color_line:
                    if text.lower().__eq__(color.lower()):
                        return None
                    break
                if ".Shirt Color:" in text:
                    is_this_color_line = True
                written_data += text
            self.__owner_data_file.writeTextData(written_data + color)
        else:
            print(self.__name + " Shirt Color Not Saved!")

    def getShirtColor(self):
        if self.__owner_data_file != "":
            is_this_color_line = False  # Detect color line in text
            for text in self.__owner_data_file.readTextData():
                if ".Shirt Color:" in text:
                    is_this_color_line = True
                    continue
                if is_this_color_line:
                    return text
        else:
            print(self.__name + " File Not Found!")
            return "Empty"

    def getFaceEncodings(self):
        samples_encodings = []
        for encoding_file in Directory.listFiles(self.__samples_encodings_default_path):
            samples_encodings.append(
                File(encoding_file, self.__samples_encodings_default_path, ".dat").readBinaryData())
        return samples_encodings

    def delete(self):
        Directory.remove("owners_data/", self.__name + "_data")
