import serial
from .cmd import get_, set_, mov_
from .helper import parse, error_check, move_check
import sys
from . import status
import numpy as np
from pprint import pprint


class Motor(serial.Serial):

	def __init__(self, port, baudrate=9600, bytesize=8, parity='N', timeout=2):
		try:
			super().__init__(port, baudrate=9600, bytesize=8, parity='N', timeout=2)
		except serial.SerialException:
			print('Could not open port %s' % port)
			sys.exit()

		if self.is_open:
			print('Connection established!')
			#self.info = self._send_command(get_['info'])
			#pprint(self.info)
			self._get_motor_info()
			self.conv_factor = float(self.info['Range'])/float(self.info['Pulse/Rev'])
			self.range = self.info['Range']
			self.counts_per_rev = self.info['Pulse/Rev']

	def _get_motor_info(self):
			# instruction = cmd['info']
			self.info = self._send_command(get_['info'])

	def do_(self, req='home', data='0', adress='0'):
		try:
			instruction = mov_[req]
		except KeyError:
			print('Invalid Command: %s' % req)
		else:
			command = adress.encode('utf-8') + instruction
			if data:
				command += data.encode('utf-8')

			self.Write(command)


	def set_(self, req='', data='', adress='0'):
		adress = ArgString(adress)
		try:
			instruction = set_[req]
		except KeyError:
			print('Invalid Command')
		else:
			command = adress.encode('utf-8') + instruction
			if data:
				command += data.encodeW('utf-8')

			self.Write(command)


	def Write(self, command, response=True):
		print(f"Sending SET command: {command}")
		self.write(command)
		response    = self.read_until(b'\n')
		status = parse(response)
		print(f'Returned status: {status}')
		error_check(status)

		return status


	def get_(self, req='status', data='', adress='0'):
		adress = ArgString(adress)
		try:
			instruction = get_[req]
		except KeyError:
			print('Invalid Command')
		else:
			command = adress.encode('utf-8') + instruction
			if data:
				command += data.encode('utf-8')

			self.status = self.Write(command)

			return self.status


	def deg_to_hex(self, deg):
		factor = self.counts_per_rev//self.range
		val = hex(deg*factor)
		return val.replace('0x', '').zfill(8).upper()

	def hex_to_deg(self, hexval):
		factor = self.counts_per_rev//self.range
		val = round(int(hexval,16)/factor)
		return val

	def deg_to_hex_2scomplement(self, deg):
		factor = self.counts_per_rev//self.range
		isneg = (deg<0)
		deg = abs(deg)
		val = deg*factor
		if isneg:
			val=hex((~np.uint32(val))+np.uint32(1))
		else:
			val=hex(val)
		return val.replace('0x','').zfill(8).upper()


	def _send_command(self, instruction, msg=None, address=b'0'):
		command = address + instruction
		if msg:
			command += msg

		self.write(command)
		response = self.read_until(b'\n')
		return parse(response)

	def __str__(self):
		string = '\nPort - ' + self.port + '\n\n'
		for key in self.info:
			string += (key + ' - ' + str(self.info[key]) + '\n')
		return string


	def move_absolute(self, pos , adress='0'):
		self.do_(req    = 'absolute',
		         data   = self.deg_to_hex_2scomplement(pos),
				 adress = adress)

	def get_position(self):
		pos = self.get_('position')
		return pos[1]/(self.counts_per_rev//self.range)

	def home(self):
		self.do_('home')


	def move_relative(self, pos, adress='0'):
		self.do_(req    = 'relative',
		         data   = self.deg_to_hex_2scomplement(pos),
				 adress = adress)
