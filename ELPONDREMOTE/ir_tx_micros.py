#!/usr/bin/env python

import pigpio

class tx:

   """
   """

   def __init__(self, pi, gpio, carrier_hz):

      """
      Initialises an IR tx on a Pi's gpio with a carrier of
      carrier_hz.

      http://www.hifi-remote.com/infrared/IR-PWM.shtml
      """

      self.pi = pi
      self.gpio = gpio
      self.carrier_hz = carrier_hz
      self.micros = 1000000 / carrier_hz
      self.on_mics = self.micros / 2
      self.off_mics = self.micros - self.on_mics
      self.offset = 0

      self.wf = []
      self.wid = -1

      pi.set_mode(gpio, pigpio.OUTPUT)

   def clear_code(self):
      self.wf = []
      if self.wid >= 0:
         self.pi.wave_delete(self.wid)
         self.wid = -1

   def construct_code(self):
      if len(self.wf) > 0:
         pulses = self.pi.wave_add_generic(self.wf)
         print("waveform TOTAL {} pulses".format(pulses))
         self.wid = self.pi.wave_create()

   def send_code(self):
      if self.wid >= 0:
        print("Sending...") 
	self.pi.wave_send_once(self.wid)
        while self.pi.wave_tx_busy():
            pass

   def add_to_code(self, on_micros, off_micros):
      """
      Add on micros of carrier followed by off micros of silence.
      """
      # Calculate cycles of carrier.
      on = (on_micros + self.on_mics) / self.micros

      # Is there room for more pulses?

      if (on*2) + 1 + len(self.wf) > 680: # 682 is maximum
         
         pulses = self.pi.wave_add_generic(self.wf)
         print("waveform partial {} pulses".format(pulses))
         self.offset = self.pi.wave_get_micros()

         # Continue pulses from offset.
         self.wf = [pigpio.pulse(0, 0, self.offset)]

      # Add on cycles of carrier.
      for x in range(on):
         self.wf.append(pigpio.pulse(1<<self.gpio, 0, self.on_mics))
         self.wf.append(pigpio.pulse(0, 1<<self.gpio, self.off_mics))

      # Add off_micros of silence.
      self.wf.append(pigpio.pulse(0, 0, off_micros))

if __name__ == "__main__":

   import sys
   import time

   import pigpio
   import ir_tx_micros

   if len(sys.argv) < 2:
      print("No pulse file specified.")
      exit()

   f = open(sys.argv[1], "r")
   p = f.read().split("\n")

   pulses = (len(p)/2) * 2

   pi = pigpio.pi() # Connect to local Pi.

   tx = ir_tx_micros.tx(pi, 2, 30000) # Pi, IR gpio, carrier frequency Hz.

   tx.clear_code()

   for x in xrange(0, pulses, 2):

      #print(int(p[x]), int(p[x+1]))
      tx.add_to_code(int(p[x]), int(p[x+1]))

   tx.construct_code()

   tx.send_code()

   tx.clear_code()

   pi.stop()

   print("Complete")

