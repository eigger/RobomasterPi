# -*- coding: utf-8 -*-

import multiprocessing as mp
from typing import Optional
from dataclasses import dataclass
if __name__ == '__main__':
    from uclient import UClient
else:
    from .uclient import UClient
import time

CTX = mp.get_context('spawn')

AUDIO_PORT: int = 40922
CTRL_PORT: int = 40923

# switch_enum
SWITCH_ON: str = 'on'
SWITCH_OFF: str = 'off'

# mode_enum
MODE_CHASSIS_LEAD: str = 'chassis_lead'
MODE_GIMBAL_LEAD: str = 'gimbal_lead'
MODE_FREE: str = 'free'
MODE_ENUMS = (MODE_CHASSIS_LEAD, MODE_GIMBAL_LEAD, MODE_FREE)

# armor_event_attr_enum
ARMOR_HIT: str = 'hit'
ARMOR_ENUMS = (ARMOR_HIT,)

# sound_event_attr_enum
SOUND_APPLAUSE: str = 'applause'
SOUND_ENUMS = (SOUND_APPLAUSE,)

# led_comp_enum
LED_ALL = 'all'
LED_TOP_ALL = 'top_all'
LED_TOP_RIGHT = 'top_right'
LED_TOP_LEFT = 'top_left'
LED_BOTTOM_ALL = 'bottom_all'
LED_BOTTOM_FRONT = 'bottom_front'
LED_BOTTOM_BACK = 'bottom_back'
LED_BOTTOM_LEFT = 'bottom_left'
LED_BOTTOM_RIGHT = 'bottom_right'
LED_ENUMS = (LED_ALL, LED_TOP_ALL, LED_TOP_RIGHT, LED_TOP_LEFT,
             LED_BOTTOM_ALL, LED_BOTTOM_FRONT, LED_BOTTOM_BACK,
             LED_BOTTOM_LEFT, LED_BOTTOM_RIGHT)

# led_effect_enum
LED_EFFECT_SOLID = 'solid'
LED_EFFECT_OFF = 'off'
LED_EFFECT_PULSE = 'pulse'
LED_EFFECT_BLINK = 'blink'
LED_EFFECT_SCROLLING = 'scrolling'
LED_EFFECT_ENUMS = (LED_EFFECT_SOLID, LED_EFFECT_OFF,
                    LED_EFFECT_PULSE, LED_EFFECT_BLINK,
                    LED_EFFECT_SCROLLING)

# line_color_enum
LINE_COLOR_RED = 'red'
LINE_COLOR_BLUE = 'blue'
LINE_COLOR_GREEN = 'green'
LINE_COLOR_ENUMS = (LINE_COLOR_RED, LINE_COLOR_BLUE, LINE_COLOR_GREEN)

# marker_color_enum
MARKER_COLOR_RED = 'red'
MARKER_COLOR_BLUE = 'blue'
MARKER_COLOR_ENUMS = (MARKER_COLOR_RED, MARKER_COLOR_BLUE)

# ai_push_attr_enum
AI_PUSH_PERSON = 'person'
AI_PUSH_GESTURE = 'gesture'
AI_PUSH_LINE = 'line'
AI_PUSH_MARKER = 'marker'
AI_PUSH_ROBOT = 'robot'
AI_PUSH_ENUMS = (AI_PUSH_PERSON, AI_PUSH_GESTURE, AI_PUSH_LINE, AI_PUSH_MARKER, AI_PUSH_ROBOT)

# ai_pose_id_enum
AI_POSE_FORWARD: int = 4
AI_POSE_REVERSE: int = 5
AI_POSE_SHOOTING: int = 6
AI_POSE_ENUMS = (AI_POSE_FORWARD, AI_POSE_REVERSE, AI_POSE_SHOOTING)

# ai_marker_id_enum
AI_MARKER_STOP: int = 1
AI_MARKER_TURN_LEFT: int = 4
AI_MARKER_TURN_RIGHT: int = 5
AI_MARKER_MOVE_FORWARD: int = 6
AI_MARKER_RED_HEART: int = 8
AI_MARKER_ENUMS = (AI_MARKER_STOP, AI_MARKER_TURN_LEFT, AI_MARKER_TURN_RIGHT, AI_MARKER_MOVE_FORWARD, AI_MARKER_RED_HEART)

@dataclass
class ChassisSpeed:
    x: float
    y: float
    z: float
    w1: int
    w2: int
    w3: int
    w4: int


@dataclass
class ChassisPosition:
    x: float
    y: float
    z: Optional[float]


@dataclass
class ChassisAttitude:
    pitch: float
    roll: float
    yaw: float


@dataclass
class ChassisStatus:
    static: bool
    uphill: bool
    downhill: bool
    on_slope: bool
    pick_up: bool
    slip: bool
    impact_x: bool
    impact_y: bool
    impact_z: bool
    roll_over: bool
    hill_static: bool


@dataclass
class GimbalAttitude:
    pitch: float
    yaw: float


@dataclass
class ArmorHitEvent:
    index: int
    type: int


@dataclass
class SoundApplauseEvent:
    count: int

class Commander(UClient):
    def __init__(self):
        super().__init__()
        self.thread_use(False)
        self.set_udp(False)
        self._mu: mp.Lock = CTX.Lock()

    def connectToRMS(self, ip):
        if self.is_opened():
            return True
        if ip == "":
            return False
        self.connect(ip, CTRL_PORT, 10)
        self.enter_sdk()
        
    @staticmethod
    def _is_ok(resp: str) -> bool:
        return resp == 'ok'

    def _do(self, *args) -> str:
        assert len(args) > 0, 'empty arg not accepted'
        cmd = ' '.join(map(str, args)) + ';'
        self.send(cmd)
        print("Send: " + str(cmd))
        buf, addr = self.recv(60)
        # print("Recv: " + str(buf))
        return buf.decode().strip(' ;')
    
    def get_ip(self) -> str:
        return self._ip

    def do(self, *args) -> str:
        with self._mu:
            return self._do(*args)

    def enter_sdk(self) -> str:
        resp = self.do('command')
        assert self._is_ok(resp), f'SDK: {resp}'
        return resp

    def version(self) -> str:
        return self.do('version')

    def robot_mode(self, mode: str) -> str:
        assert mode in MODE_ENUMS, f'unknown mode {mode}'
        resp = self.do('robot', 'mode', mode)
        assert self._is_ok(resp), f'robot_mode: {resp}'
        return resp

    def get_robot_mode(self) -> str:
        resp = self.do('robot', 'mode', '?')
        assert resp in MODE_ENUMS, f'unexpected robot mode result: {resp}'
        return resp

    def get_robot_battery(self) -> str:
        resp = self.do('robot', 'battery', '?')
        return int(resp)

    def chassis_speed(self, x: float = 0, y: float = 0, z: float = 0) -> str:
        assert -3.5 <= x <= 3.5, f'x {x} is out of range'
        assert -3.5 <= y <= 3.5, f'y {y} is out of range'
        assert -600 <= z <= 600, f'z {z} is out of range'
        resp = self.do('chassis', 'speed', 'x', x, 'y', y, 'z', z)
        assert self._is_ok(resp), f'chassis_speed: {resp}'
        return resp

    def get_chassis_speed(self) -> ChassisSpeed:
        resp = self.do('chassis', 'speed', '?')
        ans = resp.split(' ')
        assert len(ans) == 7, f'get_chassis_speed: {resp}'
        return ChassisSpeed(x=float(ans[0]), y=float(ans[1]), z=float(ans[2]), w1=int(ans[3]), w2=int(ans[4]), w3=int(ans[5]), w4=int(ans[6]))

    def chassis_wheel(self, w1: int = 0, w2: int = 0, w3: int = 0, w4: int = 0) -> str:
        for i, v in enumerate((w1, w2, w3, w4)):
            assert -1000 <= v <= 1000, f'w{i + 1} {v} is out of range'
        resp = self.do('chassis', 'wheel', 'w1', w1, 'w2', w2, 'w3', w3, 'w4', w4)
        assert self._is_ok(resp), f'chassis_wheel: {resp}'
        return resp

    def chassis_move(self, x: float = 0, y: float = 0, z: float = 0, speed_xy: float = None, speed_z: float = None, wait_for_complete: bool = True) -> str:
        assert -5 <= x <= 5, f'x {x} is out of range'
        assert -5 <= y <= 5, f'y {y} is out of range'
        assert -1800 <= z <= 1800, f'z {z} is out of range'
        assert speed_xy is None or 0 < speed_xy <= 3.5, f'speed_xy {speed_xy} is out of range'
        assert speed_z is None or 0 < speed_z <= 600, f'speed_z {speed_z} is out of range'
        cmd = ['chassis', 'move', 'x', x, 'y', y, 'z', z]
        if speed_xy is not None:
            cmd += ['vxy', speed_xy]
        if speed_z is not None:
            cmd += ['vz', speed_z]
        if wait_for_complete:
            cmd += ['wait_for_complete', 'true']
        else:
            cmd += ['wait_for_complete', 'false']
        resp = self.do(*cmd)
        assert self._is_ok(resp), f'chassis_move: {resp}'
        return resp

    def chassis_stop(self) -> str:
        cmd = ['chassis', 'stop']
        resp = self.do(*cmd)
        assert self._is_ok(resp), f'chassis_stop: {resp}'
        return resp
        
    def get_chassis_position(self) -> ChassisPosition:
        resp = self.do('chassis', 'position', '?')
        ans = resp.split(' ')
        assert len(ans) == 3, f'get_chassis_position: {resp}'
        return ChassisPosition(float(ans[0]), float(ans[1]), float(ans[2]))

    def get_chassis_attitude(self) -> ChassisAttitude:
        resp = self.do('chassis', 'attitude', '?')
        ans = resp.split(' ')
        assert len(ans) == 3, f'get_chassis_attitude: {resp}'
        return ChassisAttitude(float(ans[0]), float(ans[1]), float(ans[2]))

    def get_chassis_status(self) -> ChassisStatus:
        resp = self.do('chassis', 'status', '?')
        ans = resp.split(' ')
        assert len(ans) == 11, f'get_chassis_status: {resp}'
        return ChassisStatus(*map(lambda x: bool(int(x)), ans))

    def chassis_push_on(self, position_freq: int = None, attitude_freq: int = None, status_freq: int = None, all_freq: int = None) -> str:
        valid_frequencies = (1, 5, 10, 20, 30, 50)
        cmd = ['chassis', 'push']
        if all_freq is not None:
            assert all_freq in valid_frequencies, f'all_freq {all_freq} is not valid'
            cmd += ['freq', all_freq]
        else:
            if position_freq is not None:
                assert position_freq in valid_frequencies, f'position_freq {position_freq} is not valid'
                cmd += ['position', SWITCH_ON, 'pfreq', position_freq]
            if attitude_freq is not None:
                assert attitude_freq in valid_frequencies, f'attitude_freq {attitude_freq} is not valid'
                cmd += ['attitude', SWITCH_ON, 'afreq', attitude_freq]
            if status_freq is not None:
                assert status_freq in valid_frequencies, f'status_freq {status_freq} is not valid'
                cmd += ['status', SWITCH_ON, 'sfreq', status_freq]
        assert len(cmd) > 2, 'at least one argument should not be None'
        resp = self.do(*cmd)
        assert self._is_ok(resp), f'chassis_push_on: {resp}'
        return resp

    def chassis_push_off(self, position: bool = False, attitude: bool = False, status: bool = False, all: bool = False) -> str:
        cmd = ['chassis', 'push']
        if all or position:
            cmd += ['position', SWITCH_OFF]
        if all or attitude:
            cmd += ['attitude', SWITCH_OFF]
        if all or status:
            cmd += ['status', SWITCH_OFF]

        assert len(cmd) > 2, 'at least one argument should be True'
        resp = self.do(*cmd)
        assert self._is_ok(resp), f'chassis_push_off: {resp}'
        return resp

    def gimbal_speed(self, pitch: float, yaw: float) -> str:
        assert -450 <= pitch <= 450, f'pitch {pitch} is out of range'
        assert -450 <= yaw <= 450, f'yaw {yaw} is out of range'
        resp = self.do('gimbal', 'speed', 'p', pitch, 'y', yaw)
        assert self._is_ok(resp), f'gimbal_speed: {resp}'
        return resp

    def gimbal_move(self, pitch: float = 0, yaw: float = 0, pitch_speed: float = None, yaw_speed: float = None, wait_for_complete: bool = True) -> str:
        assert -55 <= pitch <= 55, f'pitch {pitch} is out of range'
        assert -55 <= yaw <= 55, f'yaw {yaw} is out of range'
        assert pitch_speed is None or 0 < pitch_speed <= 540, f'pitch_speed {pitch_speed} is out of range'
        assert yaw_speed is None or 0 < yaw_speed <= 540, f'yaw_speed {yaw_speed} is out of range'
        cmd = ['gimbal', 'move', 'p', pitch, 'y', yaw]
        if pitch_speed is not None:
            cmd += ['vp', pitch_speed]
        if yaw_speed is not None:
            cmd += ['vy', yaw_speed]
        if wait_for_complete:
            cmd += ['wait_for_complete', 'true']
        else:
            cmd += ['wait_for_complete', 'false']
        resp = self.do(*cmd)
        assert self._is_ok(resp), f'gimbal_move: {resp}'
        return resp

    def gimbal_moveto(self, pitch: float = 0, yaw: float = 0, pitch_speed: float = None, yaw_speed: float = None, wait_for_complete: bool = True) -> str:
        assert -25 <= pitch <= 30, f'pitch {pitch} is out of range'
        assert -250 <= yaw <= 250, f'yaw {yaw} is out of range'
        assert pitch_speed is None or 0 < pitch_speed <= 540, f'pitch_speed {pitch_speed} is out of range'
        assert yaw_speed is None or 0 < yaw_speed <= 540, f'yaw_speed {yaw_speed} is out of range'
        cmd = ['gimbal', 'moveto', 'p', pitch, 'y', yaw]
        if pitch_speed is not None:
            cmd += ['vp', pitch_speed]
        if yaw_speed is not None:
            cmd += ['vy', yaw_speed]
        if wait_for_complete:
            cmd += ['wait_for_complete', 'true']
        else:
            cmd += ['wait_for_complete', 'false']
        resp = self.do(*cmd)
        assert self._is_ok(resp), f'gimbal_moveto: {resp}'
        return resp

    def gimbal_stop(self) -> str:
        cmd = ['gimbal', 'stop']
        resp = self.do(*cmd)
        assert self._is_ok(resp), f'gimbal_stop: {resp}'
        return resp

    def gimbal_suspend(self):
        resp = self.do('gimbal', 'suspend')
        assert self._is_ok(resp), f'gimbal_suspend: {resp}'
        return resp

    def gimbal_resume(self):
        resp = self.do('gimbal', 'resume')
        assert self._is_ok(resp), f'gimbal_resume: {resp}'
        return resp

    def gimbal_recenter(self):
        resp = self.do('gimbal', 'recenter')
        assert self._is_ok(resp), f'gimbal_recenter: {resp}'
        return resp

    def get_gimbal_attitude(self) -> GimbalAttitude:
        resp = self.do('gimbal', 'attitude', '?')
        ans = resp.split(' ')
        assert len(ans) == 2, f'get_gimbal_attitude: {resp}'
        return GimbalAttitude(pitch=float(ans[0]), yaw=float(ans[1]))

    def gimbal_push_on(self, attitude_freq: int = 5) -> str:
        valid_frequencies = (1, 5, 10, 20, 30, 50)
        assert attitude_freq in valid_frequencies, f'invalid attitude_freq {attitude_freq}'
        resp = self.do('gimbal', 'push', 'attitude', SWITCH_ON, 'afreq', attitude_freq)
        assert self._is_ok(resp), f'gimbal_push_on: {resp}'
        return resp

    def gimbal_push_off(self, attitude: bool = True) -> str:
        assert attitude, 'at least one augment should be True'
        resp = self.do('gimbal', 'push', 'attitude', SWITCH_OFF)
        assert self._is_ok(resp), f'gimbal_push_off: {resp}'
        return resp

    def armor_sensitivity(self, value: int) -> str:
        assert 1 <= value <= 10, f'value {value} is out of range'
        resp = self.do('armor', 'sensitivity', value)
        assert self._is_ok(resp), f'armor_sensitivity: {resp}'
        return resp

    def get_armor_sensitivity(self) -> int:
        resp = self.do('armor', 'sensitivity', '?')
        return int(resp)

    def armor_event(self, attr: str, switch: bool) -> str:
        assert attr in ARMOR_ENUMS, f'unexpected armor event attr {attr}'
        resp = self.do('armor', 'event', attr, SWITCH_ON if switch else SWITCH_OFF)
        assert self._is_ok(resp), f'armor_event: {resp}'
        return resp

    def sound_event(self, attr: str, switch: bool) -> str:
        assert attr in SOUND_ENUMS, f'unexpected armor event attr {attr}'
        resp = self.do('sound', 'event', attr, SWITCH_ON if switch else SWITCH_OFF)
        assert self._is_ok(resp), f'armor_event: {resp}'
        return resp

    def led_control(self, comp: str, effect: str, r: int, g: int, b: int) -> str:
        assert comp in LED_ENUMS, f'unknown comp {comp}'
        assert effect in LED_EFFECT_ENUMS, f'unknown effect {effect}'
        assert 0 <= r <= 255, f'r {r} is out of scope'
        assert 0 <= g <= 255, f'g {g} is out of scope'
        assert 0 <= b <= 255, f'b {b} is out of scope'
        if effect == LED_EFFECT_SCROLLING:
            assert comp in (LED_TOP_ALL, LED_TOP_LEFT, LED_TOP_RIGHT), 'scrolling effect works only on gimbal LEDs'
        resp = self.do('led', 'control', 'comp', comp, 'r', r, 'g', g, 'b', b, 'effect', effect)
        assert self._is_ok(resp), f'led_control: {resp}'
        return resp

    def ir_sensor_measure(self, switch: bool = True):
        resp = self.do('ir_distance_sensor', 'measure', SWITCH_ON if switch else SWITCH_OFF)
        assert self._is_ok(resp), f'ir_sensor_measure: {resp}'
        return resp

    def get_ir_sensor_distance(self, id: int) -> float:
        assert 1 <= id <= 4, f'invalid IR sensor id {id}'
        resp = self.do('ir_distance_sensor', 'distance', id, '?')
        return float(resp)

    def stream(self, switch: bool) -> str:
        resp = self.do('stream', SWITCH_ON if switch else SWITCH_OFF)
        assert self._is_ok(resp), f'stream: {resp}'
        return resp

    def audio(self, switch: bool) -> str:
        resp = self.do('audio', SWITCH_ON if switch else SWITCH_OFF)
        assert self._is_ok(resp), f'audio: {resp}'
        return resp

    def blaster_fire(self) -> str:
        resp = self.do('blaster', 'fire')
        assert self._is_ok(resp), f'blaster_fire: {resp}'
        return resp

    def blaster_bead(self, cnt:int) -> str:
        resp = self.do('blaster', 'bead', cnt)
        assert self._is_ok(resp), f'blaster_bead: {resp}'
        return resp

    def enable_armor_event(self, enable):
        return self.armor_event(ARMOR_HIT, enable)
    
    def enable_sound_event(self, enable):
        return self.sound_event(SOUND_APPLAUSE, enable)

    def pwm_value(self, port_mask: int, value: float) -> str:
        assert 0 <= port_mask <= 0xffff, f'port_mask {port_mask} is out of range'
        assert 0 <= value <= 100, f'value {value} is out of range'
        resp = self.do('pwm', 'value', 'port', port_mask, 'data', value)
        assert self._is_ok(resp), f'pwm_value: {resp}'
        return resp

    def pwm_freq(self, port_mask: int, value: int) -> str:
        assert 0 <= port_mask <= 0xffff, f'port_mask {port_mask} is out of range'
        assert 0 <= value <= 50000, f'value {value} is out of range'
        resp = self.do('pwm', 'freq', 'port', port_mask, 'data', value)
        assert self._is_ok(resp), f'pwm_freq: {resp}'
        return resp

    def servo_angle(self, id: int, angle:float) -> str:
        assert 1 <= id <= 6, f'id {id} is out of range'
        assert -180 <= angle <= 180, f'angle {angle} is out of range'
        resp = self.do('servo', 'angle', 'id', id, 'angle', angle)
        assert self._is_ok(resp), f'servo_angle: {resp}'
        return resp
    

commander = Commander()
if __name__ == '__main__':
    commander.connectToRMS("127.0.0.1")
    print("OK")
    while True:
        time.sleep(1)