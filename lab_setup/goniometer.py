import thorlabs_apt as apt
import numpy as np

print(apt.list_available_devices())



def GoFrom(angle0, angle1, Num):
    AngleList = np.linspace(angle0, angle1, Num)
    for angle in AngleList:
        Goniometer.move_to(angle)


class Goniometer(object):
    name = HDR50

    def __init__(self, id=40219394):
	self.id        = id
	self.motor     = apt.Motor(self.id)
	self._Position = None

    @property
    def Position(self):
	return self._Position

    @Position.setter
    def Position(self, val)
        self.motor.move_to(val)
	
