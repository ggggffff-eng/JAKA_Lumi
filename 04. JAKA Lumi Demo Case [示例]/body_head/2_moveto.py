import lumi_url
import requests
import json
import time
import socket
import jkrc

HOST = "192.168.10.10"  # Replace with the server's IP address
ROB_HOST = "192.168.10.90"
PORT = 31001        # Replace with the server's port number

robot = jkrc.RC(ROB_HOST) #返回一个机器人对象
robot.login()

pick = [0.0, -90, 0, 20]
pick_rob = [0, 110, -100, 0, -0, -50]

place = [300.0, -45, 0, 0]
place_rob = [0, 110, -100, 0, -10, -50]

home = [0, 0, 0, 0]
home_rob = [0, 110, -100, 0, -80, -50]

def ext_moveto(point, v = 100, acc = 100):
    response = requests.post(
        lumi_url.LUMI_MOVETO_URL,
        json={"pos": point, "vel": v, "acc": acc},
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
    return

def send_command_and_receive_response(command, host, port):
    try:
        # Create a TCP/IP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to the server
            sock.connect((host, port))
            
            # Send the command
            sock.sendall(command.encode('utf-8'))
            
            # Receive the response
            response = sock.recv(4096).decode('utf-8')
            
            # Parse the JSON response
            response_json = json.loads(response)
            return response_json
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def agv_moveto(point_name):
    response = send_command_and_receive_response(
        f"/api/move?marker={point_name}", HOST, PORT
    )
    if response:
        print("Received response:")
        print(json.dumps(response, indent=4))
    else:
        print("Failed to get a valid response.")

    # wait for done
    is_done = False
    while not is_done:
        time.sleep(0.1)
        try:
            response = send_command_and_receive_response("/api/robot_status",HOST,PORT)
            if response['results']['move_status'] == "succeeded":
                is_done = True
        except Exception as e:
            print(e)
        
    return

def rob_moveto(jpos, vel = 90):
    joint_pos = [0, 0, 0, 0, 0, 0]
    for i in range(6):
        joint_pos[i] = jpos[i] / 180.0 * 3.1415926
    robot.joint_move(joint_pos, 0, True, vel / 180 * 3.14)
    return


def all_gohome():
    agv_moveto(1)
    rob_moveto(home_rob)
    ext_moveto([20,0,0,0])

def gopick():
    agv_moveto(2)
    rob_moveto(pick_rob)
    ext_moveto(pick)

def goplace():
    agv_moveto(3)
    rob_moveto(place_rob)
    ext_moveto(place)

def test2():
    while True:
        all_gohome()
        gopick()
        goplace()

def test():
    # get system infomation
    response = requests.get(lumi_url.LUMI_SYSINFO_URL)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    parsed_text_json = json.loads(response.text)
    print(f"JAKA Lumi info: {parsed_text_json}")

    # reset all joint
    response = requests.post(lumi_url.LUMI_RESET_URL, json={})
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    print("reset ok")

    # enable all joint
    response = requests.post(lumi_url.LUMI_ENABLE_URL, json={"enable": 1})
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    print("enable ok")

    # read position
    response = requests.get(lumi_url.LUMI_GETSTATE_URL)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    parsed_text_json = json.loads(response.text)  # Parse the text as JSON
    print(
        f"JAKA Lumi state: {parsed_text_json[0]['pos']},{parsed_text_json[1]['pos']},{parsed_text_json[2]['pos']}"
    )
    parsed_text_json[0]["pos"]

    # home
    response = requests.post(
        lumi_url.LUMI_MOVETO_URL,
        json={"pos": [0, -45, 0, 0], "vel": 100, "acc": 100},
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return

    print("home ok")
    time.sleep(3)

    # move to position A blockly
    for i in range(100):
        response = requests.post(
            lumi_url.LUMI_MOVETO_URL,
            json={"pos": [0.0, -100.0, -90.0, -5.0], "vel": 100, "acc": 100},
        )
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return
        print("move to A ok")

        # move to position B blockly
        response = requests.post(
            lumi_url.LUMI_MOVETO_URL,
            json={"pos": [200.0, 100.0, 90.0, 30.0], "vel": 100, "acc": 100},
        )
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return
        print("move to B ok")

    # disable all joint
    time.sleep(2)
    response = requests.post(lumi_url.LUMI_ENABLE_URL, json={"enable": 0})
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    print("disable ok")


if __name__ == "__main__":
    # test()
    test2()
