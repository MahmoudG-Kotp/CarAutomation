import enum
import cv2 as cv
from colors import Colors
import face_recognition
from sklearn.cluster import KMeans
import numpy as np
from owner import Owner


def captureFromCamera():
    # Capture from camera or anything can get view
    # To use camera call cv.VideoCapture(0) for external devices use cv.VideoCapture(1)
    return cv.VideoCapture(0)


def captureFromVideo(directory: str):
    # Capture from existing sample directory
    return cv.VideoCapture(directory)


class Frame:
    @staticmethod
    def display(title: str, frame: cv.VideoCapture):
        # Display image
        cv.imshow(title,  # Window title
                  frame)  # frame

    @staticmethod
    def scale(frame, xy, x, y):
        # Resize frame of video to 1/4 size for faster face recognition processing
        return cv.resize(frame, xy, fx=x, fy=y)

    @staticmethod
    def crop(frame, x, y, width, height):
        return frame[int(y): int(y + height), int(x): int(x + width)]

    @staticmethod
    def getDimensions(captured_video: cv.VideoCapture):
        # Return Width, Height of frame
        return captured_video.get(cv.CAP_PROP_FRAME_WIDTH), captured_video.get(cv.CAP_PROP_FRAME_HEIGHT)

    @staticmethod
    def closeAllWindows(captured_video: cv.VideoCapture):
        # Closing video file or capturing device
        captured_video.release()
        cv.destroyAllWindows()


class ObjectPositions(enum.Enum):
    NONE = -1
    CENTER = 0
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOTTOM_LEFT = 3
    BOTTOM_RIGHT = 4


class ObjectDetector:
    # Initialize variables
    __owners_indexes = []
    __owners_encodings = []

    @staticmethod
    def __createObjectBorders(detected_object,
                              frame: cv.VideoCapture,
                              border_color: Colors.BGRColors,
                              border_thickness: int):
        # Display object in rectangle
        for (x, y, width, height) in detected_object:
            cv.rectangle(frame,  # Image color
                         (x, y),  # Start point
                         (width, height),  # End point
                         border_color.value,  # Rectangle color
                         border_thickness)  # Rectangle thickness

    def __createObjectNameLabel(self,
                                detected_object,
                                frame: cv.VideoCapture,
                                object_name: str,
                                text_size: float,
                                text_font: int,
                                text_thickness: float,
                                text_color: Colors.BGRColors,
                                border_color: Colors.BGRColors):
        for (x, y, width, height) in detected_object:
            background_height = 30
            text_shift_x = 25
            text_shift_y = 8
            if text_size < 0.8:
                (text_width, text_height), text_baseline = cv.getTextSize(object_name, text_font, text_size,
                                                                          text_thickness)
                background_height = 20
                text_shift_x = int((width - x - text_width) / 2)
                text_shift_y = int((background_height - text_height) / 2) + 2
            # Draw a label with a name below the object
            self.__createObjectBorders([(x, height - background_height, width, height)], frame, border_color, cv.FILLED)
            cv.putText(frame, object_name, (x + text_shift_x, height - text_shift_y), cv.QT_FONT_NORMAL, text_size,
                       text_color.value, 1)

    @staticmethod
    def __detectShirtColor(shirt_sample):
        # T-Shirt Color Detection Processes #
        # Frame.display("Taken Shirt Sample", shirt_sample) # Display shirt sample
        shirt_height, shirt_width, shirt_dim = shirt_sample.shape
        k_means = KMeans(n_clusters=3)
        k_means.fit(np.reshape(shirt_sample, (shirt_height * shirt_width, shirt_dim)))
        unique_labels, counts_labels = np.unique(k_means.labels_, return_counts=True)
        count_frame_clusters = 0
        for cluster_center in k_means.cluster_centers_[np.argsort(counts_labels)[::-1]]:
            count_frame_clusters += 1
            # Take the bottom cluster
            if count_frame_clusters == 1:
                # Captured colors
                hsv = Colors.convertRGBToHSV([(int(cluster_center[2]),
                                               int(cluster_center[1]),
                                               int(cluster_center[0]))])
                return Colors.convertHSVToColorName(hsv)

    def __getOwnersData(self, known_owners: [Owner]):
        # Load owners data once to optimize
        if not len(self.__owners_indexes) or not len(self.__owners_encodings):
            # Give every owner index of encodings according to length of previous owners
            """ 
                Example: say owners A, B have two, three samples that means we have five samples in total 
                    so we set that if face match index < 2 that means owner A who has (0,1)
                    indexes detected and if > 2 that means B who has (2,3,4) indexes detected
                """
            old_length = 0
            for iteration_count, owner in enumerate(known_owners):
                encodings = owner.getFaceEncodings()
                encodings_len = len(encodings)  # Get length of encodings
                self.__owners_indexes.append(
                    encodings_len - 1 + old_length)  # Add encodings-1 - cause index count from zero - to the previous one
                old_length += encodings_len  # Assign current index
                for encoding in encodings:
                    self.__owners_encodings.append(encoding)
        return self.__owners_encodings, self.__owners_indexes

    def __detect_object_position(self, width_of_cam, height_of_cam, object_dimensions):
        x_object, y_object, width_of_object, height_of_object = object_dimensions
        # Center point of camera
        center_width_cam = int(width_of_cam / 2)
        center_height_cam = int(height_of_cam / 2)
        # Center point of rectangle
        center_width_object = int((x_object + width_of_object / 2))
        center_height_object = int((y_object + height_of_object / 2))

        if center_width_cam + 50 > center_width_object > center_width_cam - 50 and center_height_cam + 50 > center_height_object > center_height_cam - 50:
            return ObjectPositions.CENTER
        elif center_width_object > center_width_cam and center_height_object < center_height_cam:
            return ObjectPositions.TOP_LEFT
        elif center_width_object < center_width_cam and center_height_object < center_height_cam:
            return ObjectPositions.TOP_RIGHT
        elif center_width_object < center_width_cam and center_height_object > center_height_cam:
            return ObjectPositions.BOTTOM_RIGHT
        elif center_width_object > center_width_cam and center_height_object > center_height_cam:
            return ObjectPositions.BOTTOM_LEFT
        else:
            return ObjectPositions.NONE

    def detectHumanFace(self,
                        frame_data: ([cv.VideoCapture], bool, int),
                        known_owners: [Owner],
                        border_color: Colors.BGRColors,
                        camera_dimensions: ([int])):
        # Face Detection Processes #
        # Get frame data
        original_frame, processing_frame, is_frame_processed, frame_counter = frame_data
        camera_width, camera_height = camera_dimensions
        detected_face_locations = []
        detected_face_encodings = []
        detected_face_names = []
        owners_faces_position = []
        if is_frame_processed:
            # Initialize some variables to detect faces
            owners_face_encodings, owners_samples_indexes = self.__getOwnersData(known_owners)
            # Scale frame and convert it to RGB color (which face_recognition uses) to optimize
            rgb_small_frame = Colors.convertBGRToRGB(Frame.scale(processing_frame, (0, 0), 0.25, 0.25))
            # Find all the faces and face encodings in the current frame of video
            detected_face_locations = face_recognition.face_locations(rgb_small_frame)
            detected_face_encodings = face_recognition.face_encodings(rgb_small_frame, detected_face_locations)
            for face_encoding in detected_face_encodings:
                # See if the face is a match for the known face(s)
                detected_face_name = "Unknown"
                matches = face_recognition.compare_faces(owners_face_encodings, face_encoding, tolerance=0.6)

                # If a match was found in known_face_encodings, just use the first one.
                # Every face matches use their index to fetch name from known names
                if True in matches:
                    first_match_index = matches.index(True)
                    for iteration_count, index in enumerate(owners_samples_indexes):
                        if index >= first_match_index:
                            detected_face_name = known_owners[iteration_count].getName().capitalize()
                            break
                detected_face_names.append(detected_face_name)
        is_frame_processed = not is_frame_processed
        # Display the results
        detected_faces = zip(detected_face_locations, detected_face_names)
        # (top, right, bottom, left)
        for (y, width, height, x), detected_face_name in detected_faces:
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            detected_face_location = [(x * 4 - 20, y * 4 - 70, width * 4 + 10, height * 4 + 35)]
            # Draw a box around the face
            if detected_face_name == "Unknown":
                self.__createObjectBorders(detected_face_location, processing_frame, border_color, 2)
            else:
                self.__createObjectBorders(detected_face_location, processing_frame, Colors.BGRColors.GREEN, 2)
                self.__createObjectNameLabel(detected_face_location,
                                             processing_frame,
                                             detected_face_name,
                                             text_size=0.8,
                                             text_font=cv.QT_FONT_NORMAL,
                                             text_thickness=1,
                                             text_color=Colors.BGRColors.WHITE,
                                             border_color=Colors.BGRColors.GREEN)
                owners_faces_position.append(
                    (detected_face_name,
                     self.__detect_object_position(camera_width,
                                                   camera_height,
                                                   (x * 2, y * 2, width * 4, height * 4)).value))

                # Run in every 30 frame
                if (frame_counter % 30) == 0:
                    # Crop frame to specific dimensions according to detected face dimensions
                    shirt_sample = Frame.crop(original_frame, x * 2, y * 4, width * 4, height * 6)
                    for owner in known_owners:
                        if owner.getName().lower().__eq__(detected_face_name.lower()):
                            # Detect shirt color and save it
                            owner.saveShirtColor(self.__detectShirtColor(shirt_sample))
                            break
        return owners_faces_position

    def detectHumanBody(self,
                        frames: [cv.VideoCapture],
                        known_owners: [Owner],
                        border_color: Colors.BGRColors,
                        camera_dimensions: ([int])):
        # Body Detection Processes #
        original_frame, processing_frame = frames
        camera_width, camera_height = camera_dimensions
        # Load the cascade classifier
        is_owner_detected = list(range(len(known_owners)))
        owners_bodies_position = []
        # Convert frame to gray scale to optimize processes
        gray_frame = Colors.convertToGrayScale(processing_frame)
        detected_human_body = cv.CascadeClassifier("cv_objects_haarcascade/haarcascade_fullbody.xml") \
            .detectMultiScale(gray_frame,
                              1.1,  # Scale factor
                              5)  # Minimum neighbors
        for (x, y, width, height) in detected_human_body:
            detected_body_location = [(x, y + 10, x + width, y + height)]
            # Crop frame to specific dimensions according to detected body dimensions
            shirt_sample = Frame.crop(original_frame, x + 40, y + 50, width=40, height=50)
            # Track owners shirt in every frame
            shirt_color = self.__detectShirtColor(shirt_sample)
            for iteration, owner in enumerate(known_owners):
                if owner.getShirtColor().__eq__(shirt_color) and not is_owner_detected[iteration]:
                    is_owner_detected[iteration] = True
                    self.__createObjectBorders(detected_body_location, processing_frame, Colors.BGRColors.GREEN, 2)
                    self.__createObjectNameLabel(detected_body_location,
                                                 processing_frame,
                                                 owner.getName().capitalize(),
                                                 text_size=0.5,
                                                 text_font=cv.QT_FONT_NORMAL,
                                                 text_thickness=1,
                                                 text_color=Colors.BGRColors.WHITE,
                                                 border_color=Colors.BGRColors.GREEN)
                    owners_bodies_position.append(
                        (owner.getName().capitalize(),
                         self.__detect_object_position(camera_width, camera_height, (x, y, width, height)).value))
                    break
                else:
                    self.__createObjectBorders(detected_body_location, processing_frame, border_color, 2)
        return owners_bodies_position
