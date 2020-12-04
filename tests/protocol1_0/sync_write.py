# -*- coding: utf-8 -*-

################################################################################
# Copyright 2017 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

# Author: Ryu Woon Jung (Leon)

#
# *********     Sync Write Example      *********
#
#
# Available Dynamixel model on this example : All models using Protocol 1.0
# This example is tested with two Dynamixel MX-28, and an USB2DYNAMIXEL
# Be sure that Dynamixel MX properties are already set as %% ID : 1 / Baudnum : 34 (Baudrate : 57600)
#

from dynamixel_sdk import *                    # Uses Dynamixel SDK library
import os

if os.name == 'nt':
    import msvcrt

    def getch():
        return msvcrt.getch().decode()
else:
    import sys
    import tty
    import termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


# Control table address
# Control table address is different in Dynamixel model
ADDR_MX_TORQUE_ENABLE = 24
ADDR_MX_GOAL_POSITION = 30
ADDR_MX_PRESENT_POSITION = 36

# Data Byte Length
LEN_MX_GOAL_POSITION = 2
LEN_MX_PRESENT_POSITION = 2

# Protocol version
# See which protocol version is used in the Dynamixel
PROTOCOL_VERSION = 1.0

# Default setting
DXL1_ID = 1                 # Dynamixel#1 ID : 1
DXL2_ID = 2                 # Dynamixel#1 ID : 2
BAUDRATE = 1000000             # Dynamixel default baudrate : 57600
DEVICENAME = 'COM5'    # Check which port is being used on your controller
# ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

TORQUE_ENABLE = 1                 # Value for enabling the torque
TORQUE_DISABLE = 0                 # Value for disabling the torque
# Dynamixel will rotate between this value
DXL_MINIMUM_POSITION_VALUE = 0
# and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
DXL_MAXIMUM_POSITION_VALUE = 1023
# Dynamixel moving status threshold
DXL_MOVING_STATUS_THRESHOLD = 10

index = 0
dxl_goal_position = [DXL_MINIMUM_POSITION_VALUE,
                     DXL_MAXIMUM_POSITION_VALUE]         # Goal position


# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Set the protocol version
# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Initialize GroupSyncWrite instance
groupSyncWrite = GroupSyncWrite(
    portHandler, packetHandler, ADDR_MX_GOAL_POSITION, LEN_MX_GOAL_POSITION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()


# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()


# Enable Dynamixel#1 Torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
    portHandler, DXL1_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("Dynamixel#%d has been successfully connected" % DXL1_ID)

# Enable Dynamixel#2 Torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
    portHandler, DXL2_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("Dynamixel#%d has been successfully connected" % DXL2_ID)

while 1:
    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(0x1b):
        break

    # Allocate goal position value into byte array
    param_goal_position = [DXL_LOBYTE(DXL_LOWORD(dxl_goal_position[index])), DXL_HIBYTE(DXL_LOWORD(
        dxl_goal_position[index])), DXL_LOBYTE(DXL_HIWORD(dxl_goal_position[index])), DXL_HIBYTE(DXL_HIWORD(dxl_goal_position[index]))]

    # Add Dynamixel#1 goal position value to the Syncwrite parameter storage
    dxl_addparam_result = groupSyncWrite.addParam(DXL1_ID, param_goal_position)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncWrite addparam failed" % DXL1_ID)
        quit()

    # Add Dynamixel#2 goal position value to the Syncwrite parameter storage
    dxl_addparam_result = groupSyncWrite.addParam(DXL2_ID, param_goal_position)
    if dxl_addparam_result != True:
        print("[ID:%03d] groupSyncWrite addparam failed" % DXL2_ID)
        quit()

    # Syncwrite goal position
    dxl_comm_result = groupSyncWrite.txPacket()
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

    # Clear syncwrite parameter storage
    groupSyncWrite.clearParam()

    while 1:
        # Read Dynamixel#1 present position
        dxl1_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(
            portHandler, DXL1_ID, ADDR_MX_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        # Read Dynamixel#2 present position
        dxl2_present_position, dxl_comm_result, dxl_error = packetHandler.read4ByteTxRx(
            portHandler, DXL2_ID, ADDR_MX_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        print("[ID:%03d] GoalPos:%03d  PresPos:%03d\t[ID:%03d] GoalPos:%03d  PresPos:%03d" % (
            DXL1_ID, dxl_goal_position[index], dxl1_present_position, DXL2_ID, dxl_goal_position[index], dxl2_present_position))

        if not ((abs(dxl_goal_position[index] - dxl1_present_position) > DXL_MOVING_STATUS_THRESHOLD) and (abs(dxl_goal_position[index] - dxl2_present_position) > DXL_MOVING_STATUS_THRESHOLD)):
            break

    # Change goal position
    if index == 0:
        index = 1
    else:
        index = 0


# Disable Dynamixel#1 Torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
    portHandler, DXL1_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))

# Disable Dynamixel#2 Torque
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
    portHandler, DXL2_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))

# Close port
portHandler.closePort()
