# Waser-Wurret
This was a project for my Mechatronics &amp; IoT class in which my partner and I developed and IoT laser turret that competed in a class competition. Our challenge was to design the hardware and software for a fully autonomous lasser turret that could hit targets at specific coordinates accurately with a laser diode beam. 

---

## Phase 1 Sequential Targeting
In Phase 1, the challenge was to hit 13 targets sequentially based on coordinate data provided via an online JSON file. We designed a user interface using LLM tools, while the rest of the software was written entirely from scratch by my partner and me. To achieve precise targeting, we calculated azimuth and elevation angles and simultaneously controlled two stepper motors to drive the turret to each target. Additionally, we implemented features to calibrate and zero the stepper motors.

---

## Phase 2 Target ID Input
In Phase 2, we manually entered four target IDs into the web interface and hit those targets. This phase required filtering of the JSON data and used some of the code from Phase 1 to drive the motors to the targets.

---

## Hardware Design
Here is a picture of our actual turret:

<img src="AB1EA855-9786-4916-A7A5-55DB48450EA0_1_102_o.jpeg" alt="Screenshot Placeholder" width="650" height="400">

Credit to my partner Alexander Wang for the exceptional hardware design.

## Web Interface
Here is a picture of our web interface:

<img src="Screenshot 2024-12-17 231104.png" width="400" height="700">



