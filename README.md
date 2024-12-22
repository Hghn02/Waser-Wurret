# Waser-Wurret
This was a project for my Mechatronics &amp; IoT class in which my partner and I developed a completely wireless IoT laser turret that competed in a class competition. Our challenge was to design the hardware and software for a fully autonomous laser turret that could hit targets at specific coordinates accurately with a laser diode beam. My partner and I spent countless hours testing our software and fine tuning the control logic. However we were only able to hit 7 out of 13 targets during the phase 1 competition and 2 out of 4 for the phase 2 competition. We believe the issue was our calibration as the turret always went in the correct direction. There was also a smoke alarm incident that forced us to leave the building when our turret was able to hit 11 out of 13 targets accurately so consequently we had lost our calibration.

---

## Phase 1 Sequential Targeting
In Phase 1, the challenge was to hit 13 targets sequentially based on coordinate data provided via an online JSON file. We designed a user interface using LLM tools, while the rest of the software was written entirely from scratch by my partner and me. First we used the requests library to access a url with JSON data containing our turret coordinates and target coordinates and stored them in a tuple and list of dictionaries respectively. To achieve precise targeting, we calculated azimuth and elevation angles for each target set of coordinates. Then we simultaneously controlled two stepper motors using multiprocessing to drive the turret to each target using the calculated rotation angles. Additionally, we implemented features to calibrate and zero the stepper motors inside the GUI and wrote logic to handle GUI button states.

### Fetching Coordinates
``` python
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
```
[View the full function here](https://github.com/Hghn02/Waser-Wurret/blob/main/Waser_Wurret_Main.py#L72C1-L100C50)

### Phase 1 Sequence
``` python
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
```
[View the full function here](https://github.com/Hghn02/Waser-Wurret/blob/main/Waser_Wurret_Main.py#L72C1-L100C50)

### Manual Movement
``` python
def moveMotors(az_theta, el_theta):
    # Move motors to specified azimuth and elevation angles
    p1 = multiprocessing.Process(target=m1.rotate, args=(az_theta,))
    p2 = multiprocessing.Process(target=m2.rotate, args=(el_theta,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
```
---

## Phase 2 Target ID Input
In Phase 2, we manually entered four target IDs into the web interface and hit those targets. This phase required filtering of the JSON data and used some of the code from Phase 1 to drive the motors to the targets.

---

## Hardware Design
Here is a picture of our actual turret:

<img src="AB1EA855-9786-4916-A7A5-55DB48450EA0_1_102_o.jpeg" alt="Screenshot Placeholder" width="650" height="400">

Credit to my partner Alexander Wang for the exceptional hardware design.
[See his work here](https://alexwan9.myportfolio.com/waser-wurret-1)

## Web Interface
Here is a picture of our web interface:

<img src="Screenshot 2024-12-17 231104.png" width="550" height="700">

Credit to Claude 3.5 LLM Model for the HTML and CSS code behind the web page.



