import sys
import RPi.GPIO as GPIO
import time
import serial

class BigController():
	def __init__(self):
		global ser
		ser = serial.Serial('/dev/ttyAMA0',9600)
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(3,GPIO.OUT)
		GPIO.setup(5,GPIO.OUT)
		GPIO.setup(7,GPIO.OUT)
		GPIO.setup(8,GPIO.OUT)
		pwm1 = GPIO.PWM(3,10000)
		pwm2 = GPIO.PWM(5,10000)
		pwm3 = GPIO.PWM(7,10000)
		pwm4 = GPIO.PWM(8,10000)
		self.main(p1=pwm1,p2=pwm2,p3=pwm3,p4=pwm4)

	def mapVal(self,a,b,c,d,e):
		return (a-b)*(e-d)/(c-b) + d

	def main(self,p1,p2,p3,p4):
		global ser
		p1.start(0)
		p2.start(0)
		p3.start(0)
		p4.start(0)

		leftr = leftf = rightr = rightf = x = y = pressed = throttle = rot = 0
		buffVal = 50
		centerBuff = 50
		prevx = prevy = 512
		prevRotVal = 0
		topValue = 100
		bufferRotVal = 20
		goX = 0
		goY = 0
		goR = 0
		goT = 0
		
		print 'a'
		while True:
			t = ser.readline()
			print t
			if t[0] == 'x':
				x = t[1:4]
				goX = 1
			elif t[0] == 'y':
				y = t[1:4]
				goY = 1
			elif t[0] == 'r':
				rotVal = t[1:4]
				goR = 1
			elif t[0] == 't':
				throttle = t[1:4]
				goT = 1 

			if (goX == 1 and goY == 1) or goT == 1 or goR == 1:

				if rotVal - prevRotVal >=bufferRotVal:
					rotVal = prevRotVal + bufferRotVal
				elif rotVal - prevRotVal <=-bufferRotVal:
					rotVal = prevRotVal - bufferRotVal
				elif rotVal - prevRotVal <=-bufferRotVal:
					rotVal = prevRotVal - bufferRotVal
				elif rotVal - prevRotVal >= bufferRotVal:
					rotVal = prevRotVal + bufferRotVal

				top = self.mapVal(throttle,0,200,0,topValue)

				if(x>1023): 
					x = 1023
				if(y>1023): 
					y = 1023
				if(x-prevx>buffVal):
					x = prevx + buffVal
				elif(x-prevx<-buffVal):
					x = prevx - buffVal
				if(y-prevy>buffVal):
					y = prevy + buffVal
				elif(y-prevy<-buffVal):
					y = prevy - buffVal
				if(x<=512+centerBuff and x>=512-centerBuff and y<=512+centerBuff and y>=512-centerBuff):
					leftf = leftr = rightf = rightr = 0
				elif(x<=512+centerBuff and x>=512-centerBuff):
					if(y>=512+centerBuff):
						rightf = self.mapVal(y,512+centerBuff,1023,0,top)
						rightr = 0
						leftr = self.mapVal(y,512+centerBuff,1023,0,top)
						leftf = 0
					elif(y<=512-centerBuff):
						rightr = self.mapVal(y,0,512-centerBuff,top,0)
						rightf = 0
						leftf = self.mapVal(y,0,512-centerBuff,top,0)
						leftr = 0
				elif(y<=512+centerBuff and y>=512-centerBuff):
					if(x>=512+centerBuff):
						leftf = self.mapVal(x,512+centerBuff,1023,0,top)
						leftr = 0
						rightf = 0
						rightr = 0
					elif(x<512-centerBuff):
						leftr = 0
						leftf = 0
						rightf = 0
						rightr = self.mapVal(x,0,512-centerBuff,top,0)
				else:
					refx = refy = 0
					if(y<512):
						if(x>512):
							refy = y
							refx = 1023 - refy
							if(x<=refx):
								leftr = 0
								leftf = self.mapVal(y,0,511,top,0)
								rightf = 0
								rightr = self.mapVal(x,512,refx,top,top/2.0)

							else:
								refx = x
								refy = 1023 - refx
								leftr = 0
								leftf = self.mapVal(x,512,1023,0,top)
								rightf = 0
								rightr = self.mapVal(y,refy,511,top/2.0,0)

						else:
							refy = refx = y
							if(x>=refx):
								rightf = 0
								rightr = self.mapVal(y,0,511,top,0)
								leftr = 0
								leftf = self.mapVal(x,refx,511,top/2.0,top)

							else:
								refx = refy = x
								rightf = 0
								rightr = self.mapVal(x,0,511,top,0)
								leftr = 0
								leftf = self.mapVal(y,refy,511,top/2.0,0)

					else:
						if(x<512):
							refy = y
							refx = 1023 - refy
							if(x>=refx):
								rightr = 0
								rightf = self.mapVal(y,512,1023,0,top)
								leftr = self.mapVal(x,refx,511,0,top)
								leftf = 0

							#else:
							#	refx = x
							#	refy = 1023 - refx
							#	leftf = 0
							#	leftr = self.mapVal(y,512,1023,0,top)
							#	rightr = 0
							#	rightf = self.mapVal(x,refx,511,0,top)

						else:
							refx = refy = y
							#if(x>refx):
							#	refx = refy = x
							#	rightr = 0
							#	rightf = self.mapVal(x,512,1023,0,top)
							#	leftr = 0
							#	leftf = self.mapVal(y,512,refy,top,0)

							if(x<=refx):
								refx = refy = y
								leftf = 0
								leftr = self.mapVal(y,512,1023,0,top)
								rightr = 0
								rightf = self.mapVal(x,512,refx,top,0)

				prevx = x
				prevy = y

				if rotVal!=0 and x<=512+centerBuff and x>=512-centerBuff and y<=512+centerBuff and y>=512-centerBuff:
					
					if(rotVal<-centerBuff):
						leftf = 0
						leftr = self.mapVal(rotVal,0,-100,0,top)
						rightf = 0
						rightr = self.mapVal(rotVal,0,-100,0,top)
					elif(rotVal>centerBuff):
						leftr = 0
						leftf = self.mapVal(rotVal,0,100,0,top)
						rightr = 0
						rightf = self.mapVal(rotVal,0,100,0,top)
					prevRotVal = rotVal

				if rotVal == 0:
					prevRotVal = 0

				leftf = int(leftf)
				leftr = int(leftr)
				rightf = int(rightf)
				rightr = int(rightr)

				print 'Leftf :%s Rightf :%s'%(leftf,rightf)
				print 'Leftr :%s Rightr :%s'%(leftr,rightr)

				p1.ChangeDutyCycle(leftf)
				p2.ChangeDutyCycle(leftr)
				p3.ChangeDutyCycle(rightf)
				p4.ChangeDutyCycle(rightr)

				time.sleep(0.2)

			



BigController()



