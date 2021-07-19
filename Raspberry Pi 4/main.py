from copy import copy
from car import CarActions
from object_detection import *
from owner import Owner
from colors import Colors


def traceOwner(owners_positions: ([str, ObjectPositions]), targeted_owner_name: str):
    # Targeted owner can detect only face or body can't detect both
    # so check if the detected is body or face to determine which actions will be implemented
    owners_faces_positions, owners_bodies_positions = owners_positions
    if not targeted_owner_name or (not owners_bodies_positions and not owners_faces_positions):
        # If targeted owner name empty or both of bodies and faces positions empty don't move
        CarActions.stop()
    elif owners_bodies_positions:
        # If owner bodies not empty fetch targeted owner position
        for owner_name, owner_position in owners_bodies_positions:
            if targeted_owner_name.lower().__eq__(owner_name.lower()):
                # Take action according to position
                if owner_position == ObjectPositions.CENTER.value:
                    CarActions.moveForward()
                elif owner_position == ObjectPositions.TOP_LEFT.value:
                    CarActions.rotateRight()
                elif owner_position == ObjectPositions.TOP_RIGHT.value:
                    CarActions.rotateLeft()
                elif owner_position == ObjectPositions.BOTTOM_LEFT.value:
                    CarActions.rotateRight()
                elif owner_position == ObjectPositions.BOTTOM_RIGHT.value:
                    CarActions.rotateLeft()
                else:
                    CarActions.stop()
    elif owners_faces_positions:
        # If owner faces not empty fetch targeted owner position
        for owner_name, owner_position in owners_faces_positions:
            if targeted_owner_name.lower().__eq__(owner_name.lower()):
                # Take action according to position
                if owner_position == ObjectPositions.TOP_LEFT.value:
                    CarActions.rotateRight()
                elif owner_position == ObjectPositions.TOP_RIGHT.value:
                    CarActions.rotateLeft()
                elif owner_position == ObjectPositions.BOTTOM_LEFT.value:
                    CarActions.moveBackwardRight()
                elif owner_position == ObjectPositions.BOTTOM_RIGHT.value:
                    CarActions.moveBackwardLeft()
                else:
                    CarActions.stop()


def main():
    # Initialize needed variables
    captured_video = captureFromCamera()
    camera_dimensions = Frame.getDimensions(captured_video)
    default_border_color = Colors.BGRColors.RED
    od = ObjectDetector()
    owners_list = [
        Owner("Mahmoud", "mahmoud_samples/"),
        Owner("Ahmed", "ahmed_samples/")
    ]
    # Only process every other frame of video to save time
    is_this_frame_processed = True
    # Count Frames
    frame_counter = 0
    while True:
        # Grab a single frame from camera or video
        is_frame_exist, original_frame = captured_video.read()
        # Copy value of original frame - because python passing by reference - to another variable to keep captured frame pure from any modifications
        processing_frame = copy(original_frame)
        # If system not able to get frame from video break
        if not is_frame_exist:
            break
        # Detect objects
        owners_faces_position = od.detectHumanFace(
            (original_frame, processing_frame, is_this_frame_processed, frame_counter),
            owners_list,
            default_border_color,
            camera_dimensions)
        owners_bodies_position = od.detectHumanBody(
            (original_frame, processing_frame),
            owners_list,
            default_border_color,
            camera_dimensions)
        # Trace owner if his face or body detected
        traceOwner((owners_faces_position, owners_bodies_position), owners_list[0].getName())
        # Display detected objects
        Frame.display("Objects Detectors", processing_frame)
        # Increase frame counter one
        frame_counter += 1
        # Close window when ord(key) pressed
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    Frame.closeAllWindows(captured_video)


main()
