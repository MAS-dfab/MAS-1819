import socket
from struct import *

def concatenate_script(list_ur_commands):
    """
    Internal function that concatenates generated UR script into one large script file. Usually used to combine
    scripts generated by the GrasshopperPython components

    Args:
        list_ur_commands: A list of formatted UR Script strings

    Returns:
        ur_script: The concatenated script
    """

    ur_script = "\ndef my_script():\n"
    #ur_script += '\tpopup("running my_script")\n'

    combined_script = ""
    for ur_cmd in list_ur_commands:
        combined_script += ur_cmd

    #format combined script
    lines =  combined_script.split("\n")
    for l in lines:
        ur_script += "\t" + l + "\n"

    ur_script += 'end\n'
    ur_script += '\nmy_script()\n'
    return ur_script

def send_script(script_to_send,robot_ip):
    """
    Opens a socket to the Robot and sends a script

    Args:
        script_to_send: Script to send to socket
        robot_id: Integer. ID of robot

    """

    '''Function that opens a socket connection to the robot'''
    PORT = 30002
    HOST = robot_ip

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((HOST, PORT))
    except:
        print ("Cannot connect to ",HOST,PORT)

    s.settimeout(None)
    max_size= 2<<18
    n=len(script_to_send)
    if n>max_size:
        raise Exception("Program too long")

    try:
        s.send(script_to_send)
    except:
        print("failed to send")
    s.close()

def listen_to_robot(robot_ip):
    PORT = 30003
    HOST = robot_ip
    # Create dictionary to store data
    chunks={}
    chunks["target_joints"] = []
    chunks["actual_joints"]= []
    chunks["forces"] = []
    chunks["pose"] = []
    chunks["time"] = [0]

    data = read(HOST, PORT)
    get_messages(data, chunks)
    return chunks


def read(HOST, PORT):
    """
    Method that opens a TCP socket to the robot, receives data from the robot server and then closes socket

    Returns:
        data: Data broadcast by the robot. In bytes
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((HOST, PORT))
        print "connected"
    except:
        traceback.print_exc()
        print "Cannot connect to ",HOST,PORT
    s.settimeout(None)
    data = s.recv(1024)
    s.close()
    return data

def get_messages(bytes, chunks_info):
    """
    Function parses data stream and selects the following information:
    1) q_target
    2) q_actual
    3) TCP force
    4) Tool Vector
    5) Time

    This data is formatted and the chunks dictionary is updated
    for more info see: http://wiki03.lynero.net/Technical/RealTimeClientInterface
    """


    # get messages
    q_target = bytes[12:60]
    q_actual = bytes[252:300]
    tcp_force = bytes[540:588]
    tool_vector = bytes[588:636]
    controller_time = bytes[740:748]

    # format type: int,
    fmt_double6 = "!dddddd"
    fmt_double1 = "!d"

    #Unpack selected data
    target_joints = unpack(fmt_double6,q_target)
    chunks_info["target_joints"]= (math.degrees(j) for j in target_joints)
    actual_joints = unpack(fmt_double6,q_actual)
    chunks_info["actual_joints"]= (math.degrees(j) for j in actual_joints)
    forces = unpack(fmt_double6,tcp_force)
    chunks_info["forces"]= forces
    pose = unpack(fmt_double6,tool_vector)
    chunks_info["pose"]= pose
    time = unpack(fmt_double1,controller_time)
    chunks_info["time"]= time
