# Ambulance runs red light at junction - night driving, sudden braking required

param map = 'Town03.xodr'
param timeOfDay = 'night'
param weather = 'clear'
param egoSpeed = Normal(8.33, 0.5)  # m/s (~30 km/h)
param startDist = Uniform(5, 15)  # meters before intersection

ego = new Car with:
    speed = egoSpeed
    position = offsetAlongLane(map.getLane('lane_0'), -startDist)

emergency = new Car with:
    category = 'emergency_vehicle'
    speed = Normal(13.33, 1)  # ~48 km/h
    behavior = runsRedLight

behavior runsRedLight:
    goStraight()

require not ego.collidesWith(emergency)
require ego.speedAfter(2 seconds) < 2  # sudden braking after encounter
require timeOfDay == 'night'
require ego.lane.intersection is not None or emergency.lane.intersection is not None
require emergency.enteredIntersection and emergency.trafficLightState == 'red'
