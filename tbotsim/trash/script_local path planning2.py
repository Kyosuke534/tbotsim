from tbotlib import * 
from sys import exit
from copy import deepcopy
import numpy as np

### USER INPUTS ######################################################################
######################################################################################

grid     = circulargrid([1,1.5,2], [0,20,40,60], 2.15)
position = [1.5,0.25,2.18,0,0,100]
start    = [7,6,8,0,2] #to  [10  6  8  0  2]
grip_idx = 0
hold_idx = 10 #10

""" position = [1.4607,0.7538,2.18,0,-0,115]
start = [10,6,11,3,5]
grip_idx = 1
hold_idx = 9 """

### PREPARATIONS #####################################################################
######################################################################################

# Simulation timestep
dt = 0.0167

# Smoothing algorithm
platformsmoother = BsplineSmoother(0.005)
armsmoother = BsplineSmoother(0.2)

# Profile generators
platformprofiler = SlicedProfile6(a_t = [0.05,10], 
                                  d_t = [0.05,10], 
                                  v_t = [0.75,2.5], 
                                  dt = dt, 
                                  smoother = platformsmoother)
platformprofiler = ProfileQPlatform(platformsmoother, dt, t_t = 7, qlim=[[[-np.inf,+np.inf],[-1,1],[-2,2]]])

armprofiler = Profile3(a_t = 0.05, 
                       d_t = 0.05,
                       v_t = 0.75, 
                       dt = dt, 
                       smoother = armsmoother)
armprofiler = ProfileQArm(armsmoother, dt, v_t = 0.1, qlim=[ [[-np.inf,+np.inf],[-120,120],[-360,360]],
                                                  [[-np.inf,+np.inf],[-1,1],[-5,5]],
                                                  [[-np.inf,+np.inf],[-1,1],[-5,5]]], mode='arm')

# Local path planner objects
iter = 10000

platform2configuration = PlanPlatform2Configuration(graph = TbPlatformPoseGraph(goal_dist = 0.025, 
                                                                                goal_skew = 1, 
                                                                                directions = [0.02,0.02,0,2.5,0,0],
                                                                                iter_max = iter),
                                                    profiler = platformprofiler,
                                                    workspace = TbWorkspace(padding = [-0.1,-1.0,0,-180,-180,-45], 
                                                                            scale = [0.1,0.1,0.1,45,45,15], 
                                                                            mode = 'max'))

platform2gripper = PlanPlatform2Gripper(graph = TbPlatformAlignGraph(goal_skew = 1, 
                                                                     directions = [0.01,0.01,0,1,0,0], 
                                                                     iter_max = iter),
                                        profiler = platformprofiler)

platform2hold = PlanPlatform2Hold(graph = TbPlatformAlignGraph(goal_skew = 1, 
                                                               directions = [0.01,0.01,0,1,0,0], 
                                                               iter_max = iter),
                                  profiler = platformprofiler)

arm2pose = PlanArm2Pose(graph = TbArmPoseGraph(goal_dist = 0.05,
                                               directions = [0.025,0.025,0.025], 
                                               iter_max = iter),
                        profiler = armprofiler)

localplanner = PlanPickAndPlace2(
                    platform2configuration = platform2configuration,
                    platform2gripper       = platform2gripper, 
                    platform2hold          = platform2hold, 
                    arm2pose               = arm2pose)

# Create assets

W       = hyperRectangle(np.array([5,5,5,0.5,0.5,0.5]), np.array([-5,-5,-5,-0.5,-0.5,-0.5]))
mapping = [[0,0],[0,1],[1,2],[1,3],[3,4],[3,5],[4,6],[4,7],[2,8],[2,9]]
aorder  = Ring([0,1,3,4,2]) #indices of the grippers counter clockwise
tethers  = [TbTether.example() for _ in range(10)]
grippers = [TbGripper.example() for _ in range(5)]
platform = TbPlatform.example()
holds    = TbHold.batch(grid.T, hoverpoint = [0,0,0.05],  grippoint = [0,0,0])

for hold in holds:
    hold.add_geometry(TbCylinder(radius = 0.05, height = 0.03))

for gripper in grippers:
    gripper.add_geometry(TbCylinder(T_local = [0,0,0.015], radius = 0.015, height = 0.03))
    gripper.add_geometry(TbSphere(T_local = [0,0,0.03], radius=0.02))

for tether in tethers:
    tether.add_geometry(TbTethergeometry(radius = 0.008))

wall = TbWall(holds=holds)
tbot = TbTetherbot(platform=platform, grippers=grippers, tethers=tethers, wall=wall, W=W, mapping=mapping, aorder=aorder)

tbot.platform.T_local= TransformMatrix(position)
tbot.place_all(start)

import sys
np.set_printoptions(threshold=sys.maxsize)

""" tbot.platform.T_local = tbot.platform.T_local.translate([-0.2,0.1,0]).rotate(0,0,10)
tbot.platform.T_local = TransformMatrix([1.18710192,0.97841682,2.18,0,0.,125])
tbot.tension(grip_idx, False)
print(tbot._tensioned)
print(tbot.stability()) """

""" vi = TetherbotVisualizer(platform)
vi.run()
exit() """

### ACTUAL PATH PLANNING #############################################################
######################################################################################

tic()
#profiler = Profiler()
#profiler.on()
_, commands, exitflag = localplanner.plan(deepcopy(tbot), grip_idx, hold_idx, CommandList()) #CommandList())
toc()
print(exitflag)
#profiler.off()
#profiler.print()

if exitflag == False:
    exit()

### VISUALIZATION #######################################################################
######################################################################################

#tbtetherbot = simscene.tetherbot.toTbTetherbot()
vi = TetherbotVisualizer(tbot)

done = True
while commands and vi.opened:
    vi.update()

    if done:
        command = commands.pop(0)

    done = command.do(tetherbot=tbot)

    #print(tbot.stability(), np.all(tbot.tensioned))



    