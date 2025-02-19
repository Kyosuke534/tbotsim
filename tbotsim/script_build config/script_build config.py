from tbotlib import *
from math import pi
import os
import numpy as np

absolute_path = os.path.dirname(__file__)

# create holds
""" hold_positions = np.array([[0.527,1.285,0.002],[0.827,0.985,0.002],[0.827,0.085,0.002],[0.077,0.235,0.002],[0.077,1.135,0.002],
                           [0.527,1.585,0.002],[0.827,1.285,0.002],[0.827,0.385,0.002],[0.077,0.535,0.002],[0.077,1.435,0.002]]) """
hold_positions = np.array([[0.522,1.291,0.002],[0.832,0.990,0.002],[0.822,0.086,0.002],[0.077,0.234,0.002],[0.079,1.139,0.002],
                           [0.534,1.586,0.002],[0.838,1.290,0.002],[0.835,0.384,0.002],[0.078,0.537,0.002],[0.078,1.435,0.002]])

holds = []

for position in hold_positions:
    holds.append(TbHold(T_local = position, 
                        geometries = [TbTrianglemesh(filename=os.path.join(absolute_path, 'stl/Tetherbot_Wall_Dock Hold.stl'))],
                        hoverpoint = TbHoverPoint(T_local = [0,0,0.084]),
                        grippoint = TbGripPoint(T_local = [0,0,0.029])))

# create wall
wall = TbWall(holds = holds, 
              geometries = [TbTrianglemesh(filename=os.path.join(absolute_path, 'stl/Tetherbot_Wall_Board.stl'))])

# create arm
links = []
links.append(TbRevoluteLink(q0=0, alpha=-pi/2, a=0, d=0.0435, qlim=np.deg2rad([-175, 175]), # -180+d, 180-d, dead band (d) should be big enough that the arm can not jump over the -180/180 deg threshhold during path planning 
                            geometries = [TbTrianglemesh(filename=os.path.join(absolute_path, 'stl/Tetherbot_Platform_Arm_Joint 1.stl'))])
                            )
links.append(TbPrismaticLink(phi=0, alpha=-pi/2, a=0, q0=0.381, qlim=[0.375,0.961], 
                             geometries = [TbTrianglemesh(filename=os.path.join(absolute_path, 'stl/Tetherbot_Platform_Arm_Joint 2.stl'))])
                             )

links.append(TbPrismaticLink(phi=0, alpha=0, a=0, q0=0.198, qlim=[0.074,0.198], 
                             geometries = [TbTrianglemesh(filename=os.path.join(absolute_path, 'stl/Tetherbot_Platform_Arm_Joint 3.stl'))]))

arm = TbRPPArm(T_local = [0,0,0.167],
               links = links,
               geometries = [TbTrianglemesh(filename=os.path.join(absolute_path, 'stl/Tetherbot_Platform_Arm_Base.stl'))])

# create platform
anchorpoint_positions = np.array([[0.285,0,0.008],[0.220,-0.130,0.008],[-0.220,-0.120,0.008],[-0.220,0.120,0.008],
                                  [0.220,0.130,0.008],[0.285,0,0.121],[0.220,-0.130,0.121],[-0.220,-0.120,0.121],
                                  [-0.220,0.120,0.121],[0.220,0.130,0.121]])

anchorpoints = []

for position in anchorpoint_positions:
    anchorpoints.append(TbAnchorPoint(T_local = position))

platform = TbPlatform(T_local = [0.423,0.820,0.068,0,0,90],
                      arm = arm , 
                      anchorpoints = anchorpoints,
                      depthsensor = TbDepthsensor(T_local = [-0.27645,0,0.14625,0,180,0]),
                      geometries = [TbTrianglemesh(filename=os.path.join(absolute_path, 'stl/Tetherbot_Platform.stl'))])

# create grippers
grippers = []

for i in range(5):
    grippers.append(TbGripper(hoverpoint = TbHoverPoint(T_local = [0,0,0.195]),
                              dockpoint = TbDockPoint(T_local = [0,0,0.143,180,0,0]),
                              anchorpoint = TbAnchorPoint(T_local = [0,0,0.0815]),
                              grippoint = TbGripPoint(T_local = [0,0,0.029]),
                              marker = TbMarker(T_local= [0,-0.011,0.089,90,0,0]),
                              geometries = [TbTrianglemesh(filename=os.path.join(absolute_path, 'stl/Tetherbot_Dock Gripper.stl'))]))
    
# create tethers
tethers = []

for i in range(10):
    tethers.append(TbTether(geometries = [TbTethergeometry(radius = 0.005)],
                            f_min = 0,
                            f_max = 150))


# create tetherbot file
mapping = [[0,0],[1,1],[2,2],[3,3],[4,4],[0,5],[1,6],[2,7],[3,8],[4,9]]
aorder = Ring([4,3,2,1,0]) #indices of the grippers counter clockwise 
W = TbRectangleWrenchSet([2,2,0,0,0,0.22], [-2,-2,-0,-0,-0,-0.22])
F = TbTetherForceSet(0, 150)
tbot = TbTetherbot(platform = platform, grippers = grippers, tethers = tethers, wall = wall, 
                   mode_2d = True, 
                   mapping = mapping,
                   aorder = aorder, 
                   W = W,
                   F = F,
                   l_min = 0.12,
                   l_max = 2)
tbot.place_all([0,1,2,3,4])
tbot.save(os.path.join(absolute_path, 'pickle/tetherbot.pkl'), overwrite = True)

""" vi = TetherbotVisualizer(tbot)
vi.run() """

# create urdf files
tb2urdf(tbot, prefix = '', stlpath = 'package://tbotros_description/desc/', filepath = os.path.join(absolute_path, 'urdf'))

# create light tetherbot file
tbot_light = TbTetherbot(platform = platform, grippers = grippers, tethers = tethers, wall = wall, 
                   mapping = mapping,
                   aorder = aorder, 
                   W = W,
                   F = F,
                   l_min = 0.12,
                   l_max = 2)
tbot_light.remove_all_geometries()
tbot_light.save(os.path.join(absolute_path, 'pickle/tetherbot_light.pkl'), overwrite = True)

""" Tetherbotplot(tbot)
show()
 """