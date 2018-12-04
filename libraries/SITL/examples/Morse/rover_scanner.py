'''
This is an example builder script that sets up a rover in Morse to
be driven by ArduPilot.

The rover has the basic set of sensors that ArduPilot needs

To start the simulation use this:

  morse run rover.py

Then connect with ArduPilot like this:

  sim_vehicle.py --model morse --console --map

This model assumes you will setup a skid-steering rover with left throttle on
channel 1 and right throttle on channel 2, which means you need to set:

  SERVO1_FUNCTION 73
  SERVO3_FUNCTION 74
'''
from morse.builder import *

# use the ATRV rover
vehicle = ATRV()
vehicle.properties(Object = True, Graspable = False, Label = "Vehicle")
vehicle.translate(x=0.0, z=0.0)

# add a camera
camera = SemanticCamera(name="Camera")
camera.translate(x=0.2, y=0.3, z=0.9)
vehicle.append(camera)
camera.properties(cam_far=800)
camera.properties(Vertical_Flip=True)

# we could optionally stream the video to a port
#camera.add_stream('socket')

# add sensors needed for ArduPilot operation to a vehicle
pose = Pose()
vehicle.append(pose)

imu = IMU()
vehicle.append(imu)

gps = GPS()
gps.alter('UTM')
vehicle.append(gps)

velocity = Velocity()
vehicle.append(velocity)

# add a 360 degree laser scanner, sitting 1m above the rover
scan = Hokuyo()
scan.translate(x=0.0, z=1.0)
vehicle.append(scan)
scan.properties(Visible_arc = True)
scan.properties(laser_range = 18.0)
scan.properties(resolution = 45.0)
scan.properties(scan_window = 360.0)
scan.create_laser_arc()

# this creates sensor output like this:
# "vehicle.scan": {"timestamp": 1543891359.949892, "point_list": [[0.0, 0.0, 0.0], [-8.97607135772705, -8.976069450378418, -8.642673492431641e-07], [9.677023626863956e-10, -15.284374237060547, 5.738123718401766e-07], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], "range_list": [18.0, 12.694079399108887, 15.284374237060547, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0]}

# create a compound sensor of all of the individual sensors and stream it
all_sensors = CompoundSensor([imu, gps, velocity, pose, scan])
all_sensors.add_stream('socket')

vehicle.append(all_sensors)

# make the vehicle controllable with speed and angular velocity
# this will be available on port 60001 by default
# an example command is:
# {"v":2, "w":1}
# which is 2m/s fwd, and rotating left at 1 radian/second
motion = MotionVW()
vehicle.append(motion)
motion.add_stream('socket')

# this would allow us to control the vehicle with a keyboard
# we don't enable it as it causes issues with sensor consistency
#keyboard = Keyboard()
#keyboard.properties(Speed=3.0)
#vehicle.append(keyboard)

# Environment
env = Environment('land-1/trees', fastmode=True)
env.set_camera_location([10.0, -10.0, 10.0])
env.set_camera_rotation([1.0470, 0, 0.7854])
env.select_display_camera(camera)
env.set_camera_clip(clip_end=1000)

# startup at CMAC. A location is needed for the magnetometer
env.properties(longitude = 149.165230, latitude = -35.363261, altitude = 584.0)