import math
import requests
from stepper_class_gpio_multiprocessing_LAB7_SOLNS import Stepper
import multiprocessing
from requests.exceptions import HTTPError
import RPi.GPIO as GPIO
import socket
import time
import threading

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)

# Global Variables and Flags
laserState = "off"
turretCoordsUrl = "http://mml.umd.edu/enme441/teams.json" # contains our turret home coordinates
targetCoordsUrl = "http://mml.umd.edu/enme441/targets.json" # contains coordinates of 13 targets to hit
phase1 = False
phase2 = False
moveMotorsBool = False
azimuthAngle = 0
elevationAngle = 0
zeroMotorsBool = False

targetID1=1
targetID2=2
targetID3=3
targetID4=4

# Lock setup for multiprocessing
lock1 = multiprocessing.Lock()
lock2 = multiprocessing.Lock()

# Stepper motor setup
m1 = Stepper([6, 13, 19, 26], lock1)
m2 = Stepper([12, 16, 20, 21], lock2)

def laserControl():
    # Control laser state
    if laserState == "on":
        GPIO.output(25,1)
    else:
        GPIO.output(25,0)
    

def moveMotors(az_theta, el_theta):
    # Move motors to specified azimuth and elevation angles
    p1 = multiprocessing.Process(target=m1.rotate, args=(az_theta,))
    p2 = multiprocessing.Process(target=m2.rotate, args=(el_theta,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()

def zeroMotors():
    #Set current motor angles to zero
    m1.zero()
    m2.zero()
    print("Zeroing Motors!")
    
def goZero():
    # Send Motors to zero angle position
    p1 = multiprocessing.Process(target=m1.goAngle, args=(0,))
    p2 = multiprocessing.Process(target=m2.goAngle, args=(0,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print("Motors moving back to home")

def fetchCoords():
    # Fetch turret and target coordinates using requests
    global turretCoordsUrl, targetCoordsUrl
    targets = []
    try:
        r1 = requests.get(turretCoordsUrl)
        r2 = requests.get(targetCoordsUrl)
        r1.raise_for_status()
        r2.raise_for_status()
        
        jsonTurret = r1.json()
        jsonTargets = r2.json()

        print(jsonTurret)
        for team in jsonTurret:
            if team['Team Name'] == 'Waser Wurret':
                turretCoords = (team['x'], team['y'])
                break

        targets = [{'target number' : t["target number"], 'x': float(j["x"]), 'y': float(j["y"]), 'z': float(j["z"])} for t in jsonTargets]
        
        return turretCoords, targets
    except (HTTPError, ValueError) as e:
        print(f"Error fetching coordinates: {e}")

def executePhase1(turretCoords, targets):
    
    sortedTargets = sorted(targets, key=lambda x: int(x['target number']))
    print(sortedTargets)

    # Calculating azimuth and elevationa angles
    for t in sortedTargets:
        if t["x"]-float(turretCoords[0]) == 0:
            if t["y"] > float(turretCoords[1]):
                az_theta = 90
            else:
                az_theta = -90
        else:
            az_theta = math.degrees(
                math.atan(((t["y"]-float(turretCoords[1])))/(t["x"]-float(turretCoords[0]))))
        if (t["x"] < float(turretCoords[0])):
            az_theta += 180
        print(f"Target {t['target number']} - Azimuth angle: {az_theta:.2f}")

        if ((t["x"]-float(turretCoords[0])) == 0 and (t["y"]-float(turretCoords[1])) == 0):
            el_theta = 90
        else:
            h_distance = math.sqrt(
                (t["x"]-float(turretCoords[0]))**2 + (t["y"]-float(turretCoords[1]))**2)
            el_theta = math.degrees(math.atan((t["z"]-12.5)/(h_distance)))
        print(f"Target {t['target number']} - Elevation angle: {el_theta:.2f}")

        # Actuating stepper motors simultaneously to those angles
        p1 = multiprocessing.Process(target=m1.goAngle, args=(az_theta,))
        p2 = multiprocessing.Process(target=m2.goAngle, args=(el_theta,))
        p1.start()
        p2.start()
        p1.join()
        p2.join()

        # Laser firing for 3 seconds
        GPIO.output(25,1)
        time.sleep(3)
        GPIO.output(25,0)
        
def executePhase2(turretCoords, targets, ids):
    # Phase 2: Speed challenge to hit four targets
    idCoords = []
    # Find 4 target ids in list of 13 targets and store their coords in new list
    idCoords = [{'target number' : j["target number"], 'x': float(j["x"]), 'y': float(j["y"]), 'z': float(j["z"])} for j in targets if j["target number"] in ids]
    
    executePhase1(turretCoords,idCoords) # Sending new list of targets to phase 1 func

def web_page():
    """Generate the HTML control page."""
    
    html = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Waser Wurret Control</title>
    <style>
        body {
            background-color: #1e293b; /* Dark blue-gray background */
            color: #f8fafc; /* Light text */
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        .military-panel {
            background-color: #334155; /* Darker gray-blue for panels */
            border: 2px solid #475569; /* Subtle border */
            border-radius: 8px;
            padding: 20px;
            max-width: 700px;
            margin: 0 auto;
        }
        h1, h2 {
            text-align: center;
        }
        h1 {
            font-size: 24px;
            margin-bottom: 20px;
        }
        h2 {
            font-size: 20px;
            margin-bottom: 15px;
        }
        input[type="text"],
        input[type="number"] {
            width: calc(100% - 20px);
            padding: 8px;
            margin: 5px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
            background-color: #f0f0f0;
        }
        button {
            background-color: #16a34a; /* Military green */
            color: #f8fafc;
            font-weight: bold;
            border: none;
            border-radius: 4px;
            padding: 10px 20px;
            cursor: pointer;
            margin: 10px 0;
            display: inline-block;
        }
        button.off {
            background-color: #b91c1c; /* Red for OFF */
        }
        button.off:hover {
            background-color: #991b1b; /* Darker red on hover */
        }
        button:hover {
            background-color: #15803d; /* Darker green on hover */
        }
        .flex {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .flex input {
            flex: 1;
        }
        .flex label {
            width: 35%;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="military-panel">
        <h1>Waser Wurret Control</h1>
        
        <!-- Laser On/Off Button -->
        <div>
            <h2>Laser Control</h2>
            <form method="POST" action="">
                <input type="hidden" name="laserState" value="on">
                <button type="submit" class="on" style="width: 100%;">Turn Laser ON</button>
            </form>
            <form method="POST" action="">
                <input type="hidden" name="laserState" value="off">
                <button type="submit" class="off" style="width: 100%;">Turn Laser OFF</button>
            </form>
        </div>

        <!-- Phase 1: Coordinate Loading -->
        <div>
            <h2>Phase 1: Hit Targets</h2>
            <form method="POST" action="">
                <button type="submit" id="startPhase1" name="startPhase1" value="1" style="width: 100%;">Start Phase 1</button>
            </form>
        </div>

        <!-- Phase 2: Target IDs -->
        <div>
            <h2>Phase 2: Target IDs</h2>
            <form method="POST" action="">
                <input type="text" id="targetID1" name="targetID1" placeholder="Target ID 1">
                <input type="text" id="targetID2" name="targetID2" placeholder="Target ID 2">
                <input type="text" id="targetID3" name="targetID3" placeholder="Target ID 3">
                <input type="text" id="targetID4" name="targetID4" placeholder="Target ID 4">
                <button type="submit" id="startPhase2" name="startPhase2" value="1" style="width: 100%;">Start Phase 2</button>
            </form>
        </div>

        <!-- Manual Movement -->
        <div>
            <h2>Manual Movement</h2>
            <form method="POST" action="">
                <div class="flex">
                    <label for="azimuthAngle">Azimuth Angle (°):</label>
                    <input 
                        type="number" 
                        id="azimuthAngle" 
                        name="azimuthAngle" 
                        placeholder="Enter Azimuth Angle"
                    >
                </div>
                <div class="flex">
                    <label for="elevationAngle">Elevation Angle (°):</label>
                    <input 
                        type="number" 
                        id="elevationAngle" 
                        name="elevationAngle" 
                        placeholder="Enter Elevation Angle"
                    >
                </div>
                <button type="submit" id="moveMotorsBool" name="moveMotorsBool" value="1" style="width: 100%;">Move Motors</button>
            </form>
        </div>

        <!-- Zero Motors -->
        <div>
            <h2>Zero Motors</h2>
            <form method="POST" action="">
                <button type="submit" id="zeroMotorsBool" name="zeroMotorsBool" value="1" style="width: 100%;">Zero Motors</button>
            </form>
        </div>
    </div>
</body>
</html>
"""
    return bytes(html, 'utf-8')

def parsePOSTdata(data):
    # Parse POST data from HTTP requests
    data_dict = {}
    idx = data.find("\r\n\r\n") + 4
    data = data[idx:]
    data_pairs = data.split("&")
    for pair in data_pairs:
        key_val = pair.split("=")
        if len(key_val) == 2:
            data_dict[key_val[0]] = key_val[1]
    return data_dict

def serve_web_page():
    # Serve the control page
    global laserState, turretCoordsUrl, targetCoordsUrl, targetID1, targetID2, targetID3, targetID4, azimuthAngle, elevationAngle, moveMotorsBool, phase1, phase2
    global zeroMotorsBool
    try:

        while True:
            conn, _ = s.accept()
            client_message = conn.recv(2048).decode("utf-8")
            if "POST" in client_message:
                data_dict = parsePOSTdata(client_message)
                if "laserState" in data_dict:
                    laserState = data_dict["laserState"]
                if "targetID1" in data_dict:
                    targetID1 = data_dict["targetID1"]
                if "targetID2" in data_dict:
                    targetID2 = data_dict["targetID2"]
                if "targetID3" in data_dict:
                    targetID3 = data_dict["targetID3"]
                if "targetID4" in data_dict:
                    targetID4 = data_dict["targetID4"]
                if "azimuthAngle" in data_dict:
                    azimuthAngle = data_dict["azimuthAngle"]
                if "elevationAngle" in data_dict:
                    elevationAngle = data_dict["elevationAngle"]
                if "moveMotorsBool" in data_dict:
                    moveMotorsBool = data_dict["moveMotorsBool"]
                if "zeroMotorsBool" in data_dict:
                    zeroMotorsBool = data_dict["zeroMotorsBool"]
                if "startPhase1" in data_dict:
                    phase1 = True
                if "startPhase2" in data_dict:
                    phase2 = True

            conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            conn.sendall(web_page())
            conn.close()
    except Exception as e:
        print(f"Web server error: {e}")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", 80))
s.listen(3)

# Start the web server in a separate thread
webpageThread = threading.Thread(target=serve_web_page)
webpageThread.daemon = True
webpageThread.start()

# Main loop
try:
    while True:
        laserControl()

        # Phase 1 button logic and starting of sequence
        if phase1:
            print(turretCoordsUrl)
            print(targetCoordsUrl)
            if turretCoordsUrl != ""  and targetCoordsUrl != "":
                turretCoords, targets = fetchCoords()
                print("stage 1 reached")
                if turretCoords and targets:
                    print("executing phase 1")
                    executePhase1(turretCoords, targets)
            else:
                print("Phase 1 skipped: Missing URLs.")
            phase1 = False
        
        # Zero Motors logic
        if zeroMotorsBool:
            try:
                goZero() # hardware zero
                print("Zero Motors Button Pushed!")
            except Exception as e:
                print(f"Error in zeroing motors movement: {e}")
            finally:
                zeroMotorsBool = False

        #Phase 2 Button logic
        if phase2:
            if turretCoordsUrl != "" and targetCoordsUrl != "" and all([targetID1, targetID2, targetID3, targetID4]):
                turretCoords, targets = fetchCoords()
                if turretCoords and targets:
                    executePhase2(turretCoords, targets, [targetID1, targetID2, targetID3, targetID4])
            else:
                print("Phase 2 skipped: Missing Target IDs or URLs.")
            phase2 = False

        # manual motor movement button logic
        if moveMotorsBool:
            try:
                print("Moving motors!")
                print(azimuthAngle == '')
                if azimuthAngle == '':
                    az = 0
                    print("az is none")
                else:
                    az = int(azimuthAngle.strip())
                if elevationAngle == '':
                    el = 0
                    print("el is none")
                else:
                    el = int(elevationAngle.strip())
                print(f"Manual Move Azimuth angle: {az:.2f}")
                print(f"Manual Move Elevation angle: {el:.2f}")
                moveMotors(az, el)
                zeroMotors() # Software zero

            except Exception as e:
                print(f"Error in manual motor movement: {e}")
            finally:
                azimuthAngle, elevationAngle = 0, 0
                moveMotorsBool = False

        time.sleep(0.1)
except KeyboardInterrupt:
    print("Program terminated by user.")

    GPIO.cleanup()
    s.close()
