# Child runs onto highway at night in heavy rain near an intersection with a pedestrian crossing, requiring sudden braking.

param map = 'Town03.xodr'
param timeOfDay = 'night'
param weather = 'heavyRain'
param egoSpeed = Normal(33.3, 2)  # m/s (~120 km/h)
param childRunSpeed = Normal(5, 1)  # m/s

ego = new Car with:
    speed = egoSpeed

child = new Pedestrian where:
    position = lanes[0].leftSide.offset(-3, 2)  # sidewalk near intersection
    behavior = child.walk towards lanes[0].at(0.5) at speed childRunSpeed

intersection = map.intersections[0]
crosswalk = map.pedestrianCrossings[0]

require ego in intersection
require ego in crosswalk
require ego.acceleration < -5  # sudden braking threshold (m/s^2)
