import enum
import serial
from time import sleep


class CarActions:
    # Communicating with ATmega32 by USBasp using UART protocol
    # These characters already defined in ATmega32 to do moving actions in case one of them received
    class __UARTOrders(enum.Enum):
        FORWARD = 'A'
        FORWARD_RIGHT = 'Y'
        FORWARD_LEFT = 'E'
        BACKWARD = 'B'
        BACKWARD_RIGHT = 'Q'
        BACKWARD_LEFT = 'W'
        ROTATE_RIGHT = 'R'
        ROTATE_LEFT = 'L'
        STOP = 'S'

    @staticmethod
    def __transmitToATmega(order: __UARTOrders):
        # Identify ATmega32 port and baudrate
        #transmitter_location = serial.Serial(port="/dev/serial0", baudrate=9600)
        #sleep(0.05)
        #transmitter_location.write(str.encode(order.value))
        #sleep(0.05)
        # Print data that will be transmitted to ATmega32
        print("Order: ", order.value)

    @staticmethod
    def __transmitToATmega2(order: __UARTOrders):
        # Identify ATmega32 port and baudrate
        transmitter_location = serial.Serial(port="/dev/serial0", baudrate=9600)
        sleep(0.05)
        transmitter_location.write(str.encode(order.value))
        sleep(0.05)
        # Print data that will be transmitted to ATmega32
        print("Order: ", order.value)


    # Asking car to take moving action by transmitting data to ATmega32 #
    @staticmethod
    def moveForward():
        CarActions.__transmitToATmega(CarActions.__UARTOrders.FORWARD)

    @staticmethod
    def moveForwardRight():
        CarActions.__transmitToATmega(CarActions.__UARTOrders.FORWARD_RIGHT)

    @staticmethod
    def moveForwardLeft():
        CarActions.__transmitToATmega(CarActions.__UARTOrders.FORWARD_LEFT)

    @staticmethod
    def moveBackward():
        CarActions.__transmitToATmega(CarActions.__UARTOrders.BACKWARD)

    @staticmethod
    def moveBackwardRight():
        CarActions.__transmitToATmega(CarActions.__UARTOrders.BACKWARD_RIGHT)

    @staticmethod
    def moveBackwardLeft():
        CarActions.__transmitToATmega(CarActions.__UARTOrders.BACKWARD_LEFT)

    @staticmethod
    def rotateRight():
        CarActions.__transmitToATmega(CarActions.__UARTOrders.ROTATE_RIGHT)

    @staticmethod
    def rotateLeft():
        CarActions.__transmitToATmega(CarActions.__UARTOrders.ROTATE_LEFT)

    @staticmethod
    def stop():
        CarActions.__transmitToATmega(CarActions.__UARTOrders.STOP)
