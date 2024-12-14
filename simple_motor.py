#!/usr/bin/env python

import os
import sys
import time
import argparse
import logging

import StepMotor


logger = logging.getLogger(__name__)

def main():
  parser = argparse.ArgumentParser(
      description="Move the stepper motor.",
      formatter_class=argparse.ArgumentDefaultsHelpFormatter,
      )
  parser.add_argument("-d", "--degrees",
                    type=float,
                    default=1,
                    help="angular step size.",
                    )
  parser.add_argument("-n", "--number",
                    type=int,
                    default=5,
                    help="Number of times to do the movement.",
                    )
  parser.add_argument("--home",
                    action=argparse.BooleanOptionalAction,
                    default=True,
                    help="Go Home, before moving",
                    )
  parser.add_argument("--enable-limits",
                    action=argparse.BooleanOptionalAction,
                    default=False,
                    help="Enable software extent limits",
                    )
      #self.parser.add_option("-d", "--dwell",
      #                action="store", type="string", dest="dwelltime", default="50",
      #                help="dwell time in milliseconds: [default: %default]")
      #self.parser.add_option("-t", "--sleep_time",
      #                action="store", type="float", dest="ang_sleep_time", default="1",
      #                help="angular sleep time in seconds: [default: %default]")
      #self.parser.add_option("-e", "--device",
      #                action="store", type="string", dest="device", default="",
      #                help="device \"mon0\"=directional, \"mon1\" = omni: [default: %default]")
  args = parser.parse_args()

  #formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
  logging.basicConfig(
      #format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
      format='%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
      datefmt='%Y-%m-%d:%H:%M:%S',
      level=logging.DEBUG,
      )
  logger.info('Started')


  #-- Initialize serial comms, motor drive, and table position
  motor = StepMotor.StepMotor()
  motor.InitializeDrive(enable_limits=args.enable_limits)
  if args.home:
    motor.GoHome()
  if args.degrees != 0:
    motor.MoveDegrees(args.degrees)
    for n in range(args.number):
      motor.MoveDegrees(args.degrees)
    #  #motor.MoveDegrees(-1*args.degrees)


#=====================================================================
def SetDegreesHome(self, degreeshome):
#=====================================================================
  try:
    n = int(degreeshome)
    if n >= -360 and n < 360:
      self.degreeshome = degreeshome
      return degreeshome
    else:
      return None
  except ValueError:
    return None

#=====================================================================
def comtool(self, cmd):
#=====================================================================
  cmdline = self.options.com_tool +' ' +cmd
  if self.options.head_baud_rate:
    cmdline += ' -b ' +self.options.head_baud_rate
  return cmdline

##=====================================================================
#def comtool_parse(self, resp):
##=====================================================================
#  self.stdout("comtool_parse: '" +resp +"'")
#  if 'Received:' in resp[0:9]:
#    self.stdout("comtool_parse: found Received")
#    return resp[10:]
#  else:
#    self.stdout("comtool_parse: no prefix")
#    return resp


if __name__ == '__main__':
    main()
# vim:expandtab:sw=2:ts=2
