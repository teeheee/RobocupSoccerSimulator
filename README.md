# RobocupSoccerSimulator
A simulator for Robocup Junior Soccer Open written in python.

# Dependencies

  numpy, pymunk, pygame, python3
  
# Install raw
```
install python3 pip3 and git
pip install numpy pymunk pygame
git clone https://github.com/teeheee/RobocupSoccerSimulator
cd RobocupSoccerSimulator
```  
# Install windows

download robocupsoccersimulator_win32.exe and install
  
# Run
```  
python robotsimul.py
```    
or just start the robotsimul.exe in the windows installation directory

# Usage

## Simulator-Interface
- select robot with 1,2,3,4
- enable user control with holding space
- pause with holding p key
- control robot with arrow keys and j,m

## Program-Interface-rules
- edit the main.py in the corresponding Teamx/robotx folders
- call function with robot.<functionname>
```python
    # Returns a list of 16 Analog Sensor Values representing Black and White and Green lines
    # Numbering starts at the front and goes clockwise
    robot.getBodenSensors()
    
    # Returns a list of 4 Distance measurements in all 4 directions
    # Numbering starts at the front and goes clockwise
    robot.getUltraschall()
    
    # Returns a list of 16 IR sensors. Value corresponds to distance from the Ball
    # Numbering starts at the front and goes clockwise
    robot.getIRBall()
    
    # Returns the orientation of the Robot in degree. 180° is opponent goal. Numbering goes clockwise
    robot.getKompass()
       
    # Sets the Motor speeds to this Value Motors rotate the Robot counter clockwise.
    # Numbering starts at the front and goes clockwise
    robot.setMotorSpeed(m0,m1,m2,m3)
```



