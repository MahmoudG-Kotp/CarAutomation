import enum
import cv2 as cv


class Colors:
    class BGRColors(enum.Enum):
        GREEN = (0, 230, 0)
        YELLOW = (0, 215, 220)
        RED = (0, 0, 240)
        WHITE = (255, 255, 255)

    @staticmethod
    def convertBGRToRGB(frame):
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        return frame[:, :, ::-1]

    @staticmethod
    def convertToGrayScale(frame):
        # Convert frame to gray scale to optimize processes
        return cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    @staticmethod
    def convertRGBToHSV(rgb):
        h, s, v = 0, 0, 0
        for r, g, b in rgb:
            r, g, b = r / 255.0, g / 255.0, b / 255.0
            mx = max(r, g, b)
            mn = min(r, g, b)
            df = mx - mn
            if mx == mn:
                h = 0
            elif mx == r:
                h = (60 * ((g - b) / df) + 360) % 360
            elif mx == g:
                h = (60 * ((b - r) / df) + 120) % 360
            elif mx == b:
                h = (60 * ((r - g) / df) + 240) % 360
            if mx == 0:
                s = 0
            else:
                s = (df / mx) * 100
            v = mx * 100
        return [(int(h), int(s), int(v))]

    @staticmethod
    def convertHSVToColorName(hsv):
        for h, s, v in hsv:
            if v == 0:
                return 'Black'
            elif s == 0:
                if 0 < v < 50:
                    return 'Gray'
                elif 50 <= v < 75:
                    return 'Silver'
                elif 75 <= v < 100:
                    return 'White'
            elif s > 0:
                if 0 < h < 20:
                    return 'Red'
                elif 20 <= h < 45:
                    return 'Orange'
                elif 45 <= h < 65:
                    return 'Yellow'
                elif 65 <= h < 110:
                    return 'Lime'
                elif 110 <= h < 150:
                    return 'Green'
                elif 150 <= h < 200:
                    return 'Cyan'
                elif 200 <= h < 250:
                    return 'Blue'
                elif 250 <= h < 300:
                    return 'Purple'
                elif 300 <= h < 340:
                    return 'Pink'
                elif 340 <= h < 360:
                    return 'Marron'
            else:
                return 'Unknown'
