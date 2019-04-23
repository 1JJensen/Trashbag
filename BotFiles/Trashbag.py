import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.structures.ball_prediction_struct import BallPrediction, Slice
from rlbot.utils.structures.quick_chats import QuickChats

from random import triangular as triforce

class Trashbag(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.car = carobject(self.index)
        self.ball = ballobject()
        self.controller_state = SimpleControllerState()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        '''Rendering manager'''
        self.turn_on_turn_radius_rendering = False
        self.turning_circle_points = 20

        self.turn_on_ballprediction_rendering = False
        self.amount_of_ballprediction_locations = 360


        self.preprocess(packet)

        self.ball2D = (self.ball.loc).flatten()
        self.local_ball = local(self.car, self.ball.loc)
        self.angle_steer = math.atan2(self.local_ball[1], self.local_ball[0])
        self.controller_state.steer = clamp(self.angle_steer, 1, -1)
        if self.angle_steer > 0:
            self.action_display = "Turn left"
        else:
            self.action_display = "Turn right"

        self.speed = self.car.vel.magnitude()
        self.turn_radius = 156 + 0.1*self.speed + 0.000069*self.speed**2 + 0.000000164*self.speed**3 + -5.62E-11*self.speed**4
        self.pointright = self.car.matrix.data[1] * self.turn_radius + self.car.loc
        self.pointleft = self.car.matrix.data[1] * self.turn_radius * -1 + self.car.loc
        if (self.ball2D - self.pointright).magnitude() < self.turn_radius or (self.ball2D - self.pointleft).magnitude() < self.turn_radius:
            if (self.car.loc.flatten() - self.ball.loc.flatten()).magnitude() < 300:
                self.controller_state.handbrake = True
                self.controller_state.throttle = 0.2
                self.throttle_display = "Deja vu"
            else:
                self.controller_state.handbrake = False
                self.controller_state.throttle = -0.2
                self.throttle_display = "Slow down"
        else:
            self.controller_state.handbrake = False
            self.controller_state.throttle = 1
            self.throttle_display = "Full throttle"
        
        self.ball_prediction = self.get_ball_prediction_struct()
        prediction_slice = self.ball_prediction.slices[120]
        location = prediction_slice.physics.location
        '''if location[1] > 5120 * ((self.team - 0.5) * 2):
            self.send_quick_chat0(QuickChats.CHAT_EVERYONE, QuickChats.Reaction Nooo)'''
        draw_debug(self,self.renderer, self.car, self.ball)

        return self.controller_state

    def preprocess(self, gamepacket):
        self.car.update(gamepacket.game_cars[self.index])
        self.ball.update(gamepacket.game_ball)

class carobject:
    def __init__(self, i):
        self.index = i
        self.loc = Vector3(0,0,0)
        self.vel = Vector3(0,0,0)
        self.rot = Vector3(0,0,0)#this is not a vector
        self.Rotvel = Vector3(0,0,0)
        self.matrix = Matrix3D(self.rot)
        self.goals = 0
        self.saves = 0
        self.name = "Trashbag"
        self.jumped = False
        self.doublejumped = False
        self.team = 0
        self.boostAmount = 0
        self.wheelcontact = False
        self.supersonic = False

    def update(self,TempVar):
        self.loc.data = [TempVar.physics.location.x,TempVar.physics.location.y,TempVar.physics.location.z]
        self.vel.data = [TempVar.physics.velocity.x,TempVar.physics.velocity.y,TempVar.physics.velocity.z]
        self.rot.data = [TempVar.physics.rotation.pitch,TempVar.physics.rotation.yaw,TempVar.physics.rotation.roll]
        self.matrix = Matrix3D(self.rot)
        TempRot = Vector3(TempVar.physics.angular_velocity.x,TempVar.physics.angular_velocity.y,TempVar.physics.angular_velocity.z)
        self.Rotvel = self.matrix.dot(TempRot)
        self.goals = TempVar.score_info.goals
        self.saves = TempVar.score_info.saves
        self.name = TempVar.name
        self.jumped = TempVar.jumped
        self.doublejumped = TempVar.double_jumped
        self.team = TempVar.team
        self.boostAmount = TempVar.boost
        self.wheelcontact = TempVar.has_wheel_contact
        self.supersonic = TempVar.is_super_sonic

class ballobject:
    def __init__(self):
        self.loc = Vector3(0,0,0)
        self.vel = Vector3(0,0,0)
        self.rot = Vector3(0,0,0)
        self.Rotvel = Vector3(0,0,0)

    def update(self,TempVar):
        self.loc.data = [TempVar.physics.location.x,TempVar.physics.location.y,TempVar.physics.location.z]
        self.vel.data = [TempVar.physics.velocity.x,TempVar.physics.velocity.y,TempVar.physics.velocity.z]
        self.rot.data = [TempVar.physics.rotation.pitch,TempVar.physics.rotation.yaw,TempVar.physics.rotation.roll]
        self.Rotvel.data = [TempVar.physics.angular_velocity.x,TempVar.physics.angular_velocity.y,TempVar.physics.angular_velocity.z]

def draw_debug(self, renderer, car, ball):
    renderer.begin_rendering()
    renderer.draw_line_3d(self.car.loc, self.ball.loc, renderer.white())
    renderer.draw_line_3d(self.car.loc, self.car.matrix.data[0] * 500 + self.car.loc, renderer.blue())
    renderer.draw_string_2d(10, 80 * (self.team * 2), 1, 1, self.action_display, renderer.red())
    renderer.draw_string_2d(10, 80 * (self.team * 2) + 20, 1, 1, self.throttle_display, renderer.red())
    renderer.draw_string_2d(10, 80 * (self.team * 2) + 40, 1, 1, "Speed" +'\n'+ str(self.speed), renderer.lime())
    renderer.draw_string_2d(10, 80 * (self.team * 2) + 80, 1, 1, str(Vector3(round(self.local_ball[0]), round(self.local_ball[1]), round(self.local_ball[2]))), renderer.blue())

    '''Turning circles'''
    if self.turn_on_turn_radius_rendering ==True:
        connections = self.turning_circle_points
        b = []
        b0 = []
        for i in range(connections):
            a = (i / connections) * 2 * math.pi
            b.append(Vector3(self.turn_radius * math.cos(a), self.turn_radius * math.sin(a) , self.car.loc[2]) + self.pointright)
            b0.append(Vector3(self.turn_radius * math.cos(a), self.turn_radius * math.sin(a) , self.car.loc[2]) + self.pointleft)
        if self.angle_steer < 0:
            renderer.draw_polyline_3d(b, self.renderer.create_color(255, 255, 0, 255))
        else:
            renderer.draw_polyline_3d(b0, self.renderer.create_color(255, 255, 0, 255))

    '''Ball prediction'''
    if self.turn_on_ballprediction_rendering == True:
        c = []
        points = 360 / clamp(self.amount_of_ballprediction_locations, 360, 1)
        for i in range(0, self.ball_prediction.num_slices, round(int(points))):
            prediction_slice = self.ball_prediction.slices[i]
            location = prediction_slice.physics.location
            c.append(location)
        '''renderer.draw_polyline_3d(c, renderer.create_color(255, 0, 255, 0))'''
        for vec in c:
            renderer.draw_string_3d(vec, 1, 1, "-", renderer.red())

    renderer.end_rendering()

def clamp(t: float, max_value: float, min_value: float) -> float:
    return max(min(t, max_value), min_value)

def local(car,vector): #example: local_ball = local(self.car, self.ball.loc)
    return car.matrix.dot(vector - car.loc)

class Matrix3D:
    def __init__(self,r):
        CR = math.cos(r[2])
        SR = math.sin(r[2])
        CP = math.cos(r[0])
        SP = math.sin(r[0])
        CY = math.cos(r[1])
        SY = math.sin(r[1])        
        self.data = [Vector3(CP*CY, CP*SY, SP),Vector3(CY*SP*SR-CR*SY, SY*SP*SR+CR*CY, -CP * SR),Vector3(-CR*CY*SP-SR*SY, -CR*SY*SP+SR*CY, CP*CR)]

    def dot(self,vector):
        return Vector3(self.data[0].dot(vector),self.data[1].dot(vector),self.data[2].dot(vector))

class Vector3:
    def __init__(self,a,b,c):
        self.data = [a,b,c]
    def __getitem__(self,key):
        return self.data[key]
    def __str__(self):
        return str(self.data)
    def __add__(self,value):
        return Vector3(self[0]+value[0], self[1]+value[1], self[2]+value[2])
    def __sub__(self,value):
        return Vector3(self[0]-value[0],self[1]-value[1],self[2]-value[2])
    def __mul__(self,value):
        return Vector3(self[0]*value, self[1]*value, self[2]*value)
    __rmul__ = __mul__
    def __div__(self,value):
        return Vector3(self[0]/value, self[1]/value, self[2]/value)
    def magnitude(self):
        return math.sqrt((self[0]*self[0]) + (self[1] * self[1]) + (self[2]* self[2]))
    def normalize(self):
        mag = self.magnitude()
        if mag != 0:
            return Vector3(self[0]/mag, self[1]/mag, self[2]/mag)
        else:
            return Vector3(0,0,0)
    def dot(self,value):
        return self[0]*value[0] + self[1]*value[1] + self[2]*value[2]
    def cross(self,value):
        return Vector3((self[1]*value[2]) - (self[2]*value[1]),(self[2]*value[0]) - (self[0]*value[2]),(self[0]*value[1]) - (self[1]*value[0]))
    def flatten(self):
        return Vector3(self[0],self[1],0)