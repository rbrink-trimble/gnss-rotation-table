#! /usr/bin/env python

import sys
import serial
import serial.tools.list_ports
import re
import time
import logging

logger = logging.getLogger(__name__)

# Each response from the GT6 controller ends with this.
RESP_TERM = '\r\n> '
RESP_UNDEF = '\r\n? '
RESP_PROG = '\r\n- '  # In the middle of a program definition.

class StepMotorError(Exception): pass
class StepMotorNoDevice(StepMotorError): pass


# Some debugging commands for the Parker GT6 Gemini Stepper controller:
# *TST?
# *SYST:ERR?
# *CLS
# *TST
#
# Connection to the stepper is typically 8-N-1 9600 Baud

#==============================================================================
# StepMotor:
#==============================================================================
class StepMotor(object):
    def __init__(self,
                 spname=None,
                 steps_per_rotation=900000,
                 post_move_sleep=1,
    ):
        self.serialport = None
        self.steps_per_rotation = steps_per_rotation
        self.post_move_sleep = post_move_sleep
        if spname == 'dryrun':
            splist = []
        else:
            if spname is None:
                splist = list(self.get_serial_ports())
            else:
                splist = [ spname ]
            for spname in splist:
                try:
                    logger.info('Trying serial port: {}'.format(spname))
                    self.serialport = serial.Serial(spname, baudrate=9600, timeout=0.1)

                    # See if we get a prompt from the serial port sending a bogus command
                    # and read everything in the buffer until we timeout.  If we don't get
                    # the undefined label response, go to the next serial port and try
                    # again.
                    msg = 'xxx\n'
                    logging.debug(f"SEND: {msg.strip()}")
                    self.serialport.write(msg.encode())
                    resp = self.serialport.read(128).decode()
                    logger.debug(f'RESP: {resp.strip()}')
                    if '*UNDEFINED_LABEL' not in resp:
                        continue
                    break
                except serial.SerialException as exc:
                    logger.info('dev={}: {}'.format(spname, exc))
                else:
                  raise StepMotorNoDevice('No Serial Device Found')

        if self.serialport:
            self.serialport.flushInput()                # flush input buffer
            self.serialport.flushOutput()               # flush output buffer
        logger.info('Using serial port: {}'.format(spname))

    def get_serial_ports(self):
        # Starting with serial version 3.0.1? list_ports.comports() returns an
        # object. Older versions return a list of tuples.
        #logging.info(f'{serial.VERSION=}')
        if '3' in serial.VERSION[0]:
            p = serial.tools.list_ports.comports()
            for port, desc, hwid in sorted(p):
                logging.info(f'{port=}')
                #logging.debug(f"{port=} {desc=} {hwid=}")
                #if p.subsystem in ('pnp', 'usb-serial'):
                #    yield p.device
                if 'usbserial' in port:
                  print(f'Found {port}')
                  yield port
                if 'ttyUSB' in port:
                  print(f'Found {port}')
                  yield port
        #else:
        #    for p in serial.tools.list_ports.comports():
        #        if 'USB' in p[0]:
        #            yield p[0]

    def send_cmd(self, cmd):
        msg = '{}\n'.format(cmd.strip())
        logger.debug(f"SEND: {msg.strip()}")
        if self.serialport:
            self.serialport.write(msg.encode())

        resp = ''
        if self.serialport:
            while not (resp.endswith(RESP_TERM) or resp.endswith(RESP_UNDEF)) or resp.endswith(RESP_PROG):
                ch = self.serialport.read(1).decode()
                if ch:
                    resp += ch

        logger.debug(f'RESP: {resp.strip()}')
        return resp

    def send_script(self, fname):
        for l in open(fname, 'rb'):
          line = l.strip()
          if not line:
              continue
          cmd = line.split(';')[0].strip()
          if not cmd:
              continue
          print(self.send_cmd(cmd).strip())

    def InitializeDrive(self, enable_limits=True, vel=5, accel=10):
        logger.info('Initializing motor drive')
        if self.serialport:
            self.send_cmd('')                 # Force prompt
            self.send_cmd('')

        self.send_cmd('ECHO0')            # Disable echoing of sent command.
        self.send_cmd('DMODE12')          # Steping Drive Mode
        self.send_cmd('DRES25000')        # Set Drive Resolution 25000 counts/rev
        self.send_cmd(f'V{vel}')               # Set velosity to 5rps
        self.send_cmd(f'A{accel}')        # Set acceleration to 10
        self.send_cmd(f'A{accel}')        # Set deceleration to 10
        self.send_cmd('MA0')              # Set to incremental mode

        # Set positive and negative sofware limits
        self.send_cmd('LSPOS+1000000')
        self.send_cmd('LSNEG-990000')
        if enable_limits:
            self.send_cmd('LS3')
        else:
            self.send_cmd('LS0')

    def MoveDegrees(self, deg):
        logger.info(f'Move: {deg} deg')
        steps = int(self.steps_per_rotation *deg/360)           # Find steps for input degrees

        self.send_cmd('DRIVE1')               # Enable Drive
        self.send_cmd('D{}'.format(steps))    # Set Distance to input degrees
        self.send_cmd('GO')                   # Enable Movment
        self.send_cmd('DRIVE0')               # Disable Drive
        self.send_cmd('TAS')                  # Get Axis Status
        time.sleep(self.post_move_sleep)
        logger.debug('Move complete')
        # The response from the controller will not occur until the command has
        # completed. As such, no need to sleep after sending the 'DRIVE0' command.
        #time.sleep(abs(float(deg))*0.012)


    def GoToDegrees(self, deg):
        logger.info(f'GoToDegrees: {deg}')
        steps = int(self.steps_per_rotation *deg/360)           # Find steps for input degrees

        self.send_cmd('DRIVE1')               # Enable Drive
        self.send_cmd('MA1')                  # Switch to absolute mode.
        self.send_cmd('D{}'.format(steps))    # Set Distance to input degrees
        self.send_cmd('GO')                   # Enable Movment
        self.send_cmd('MA0')                  # Switch back to incremental mode
        self.send_cmd('DRIVE0')               # Disable Drive
        self.send_cmd('TAS')                  # Get Axis Status
        time.sleep(self.post_move_sleep)
        logger.debug('Move complete')


    def Turn360(self, n=1):
        logger.info('Turn360')
        self.send_cmd('DRIVE1')               # Enable Drive
        self.send_cmd(f'D{n*self.steps_per_rotation}') # Set distance to one opposite rev
        self.send_cmd('GO')                   # Enable Movment
        self.send_cmd('DRIVE0')               # Disable Drive
        time.sleep(self.post_move_sleep)


    def GoHome(self):
        logger.info('GoHome')

        self.send_cmd('MC0')
        self.send_cmd('HOMA10')
        self.send_cmd('HOMV7')
        self.send_cmd('HOMVF.3')
        self.send_cmd('HOMBAC1')
        self.send_cmd('HOMDF1')
        self.send_cmd('HOMEDG0')

        self.send_cmd('DRIVE1')               # Enable Drive
        self.send_cmd('HOM0')                 # Enable Movment
        self.send_cmd('DRIVE0')               # Disable Drive
        time.sleep(self.post_move_sleep)


    def SetHome(self):
        '''Set the current position to be "Home".
        '''
        logger.info('SetHome')
        self.send_cmd('DRIVE1')
        self.send_cmd('PSET0')
        self.send_cmd('DRIVE0')

    def close(self):
        if self.serialport:
            self.serialport.close()
            logger.info('serial port closed')

    def Finish(self):
        self.GoToDegrees(0)
        self.close()


if __name__ == '__main__':
  import random
  logging.basicConfig(
    format='%(levelname)s: %(message)s',
    level=logging.DEBUG,
  )

  try:
    sm = StepMotor()
    sm.InitializeDrive()

    sm.SetHome()

    #sm.send_script('dump-settings.prg')

    logger.debug('Test sending unknown command')
    sm.send_cmd('foobar')

    for i in range(2):
      sm.send_cmd('V10') # Go faster!
      sm.MoveDegrees(0-random.randint(135, 225))
      time.sleep(1)
      sm.GoHome()
      time.sleep(2)

    sm.send_cmd('V10') # Go faster!
    sm.Turn360()
    sm.send_cmd('V5')  # Restore default velocity.

    # After the above move, the abs pos is 360 degrees, going to 0 unwinds

    sm.GoToDegrees(0)
    time.sleep(1)
    sm.GoToDegrees(45)
    time.sleep(1)
    sm.GoToDegrees(90)
    time.sleep(1)
    sm.GoToDegrees(0)
    time.sleep(1)

    # Go full circle, in 15 degree increments in opposite direction
    for i in range(24):
      sm.MoveDegrees(-15)

    sm.MoveDegrees(15)
    sm.MoveDegrees(-30)
    sm.MoveDegrees(15)
    sm.GoToDegrees(0)

    sm.Finish()
  except StepMotorError as exc:
    logger.error(exc)
# vim:expandtab:sw=2:ts=2
