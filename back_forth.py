#!/usr/bin/env python

import os
import sys
import time
import argparse
import logging

import StepMotor

CFG_FILE_NAME = "back_forth.ini"

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
          description="Move the stepper motor.",
          formatter_class=argparse.ArgumentDefaultsHelpFormatter,
          epilog= f'Change defaults with {CFG_FILE_NAME} in current directory.',
          )
    motorp = parser.add_argument_group('Motor Parameters')
    motorp.add_argument('-L', "--limits",
                        action=argparse.BooleanOptionalAction,
                        default=False,
                        help="Enable travel limits",
                        )
    motorp.add_argument('-V', "--velocity",
                        type=float,
                        default=3,
                        help="Motor Velocity",
                        )
    motorp.add_argument('-A', "--accel",
                        type=float,
                        default=2,
                        help="Motor Velocity",
                        )
    fb_p = parser.add_argument_group('Forward Back')
    fb_p.add_argument("-f", "--degrees-fwd",
                        type=float,
                        default=30,
                        help="angular step size. positive =CW, negative = CCW",
                        )
    fb_p.add_argument("-b", "--degrees-back",
                        type=float,
                        default=30,
                        help="angular step size. positive =CW, negative = CCW",
                        )
    fb_p.add_argument("-n", "--number",
                        type=int,
                        default=1,
                        help="Number of times to do the movement.",
                        )
    fb_p.add_argument("-t", "--sleep-time",
                        type=float,
                        default=1.0,
                        help="Sleep time (secs) between each fwd and each back"
                        )
    initp = parser.add_argument_group('Initialization')
    initp.add_argument("--home-start",
                        action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Go Home, before moving",
                        )
    initp.add_argument("--home-end",
                        action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Go Home, at the end of all movements",
                        )
    initp.add_argument("--enable-limits",
                        action=argparse.BooleanOptionalAction,
                        default=False,
                        help="Enable software extent limits",
                        )
    initp.add_argument("--dryrun",
                        action=argparse.BooleanOptionalAction,
                        default=False,
                        help="Don't do anything. Just log the would be movements",
                        )
    parser.add_argument(
        "--verbose", "-v",
        action='count',
        default=0,
        help="use multiple -v for more detailed messages."
    )

    if os.path.isfile(CFG_FILE_NAME):
        config = configparser.ConfigParser()
        config.read(CFG_FILE_NAME)
        defaults = dict(config.items("Defaults"))
        parser.set_defaults(**defaults)
    args = parser.parse_args()

    logging.basicConfig(
          format='%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
          datefmt='%Y-%m-%d:%H:%M:%S',
          level=logging.WARNING - (10 * args.verbose),
          )
    logger.info('Started')


    #-- Initialize serial comms, motor drive, and table position

    do_back_forth(args.dryrun, args.enable_limits,
                  args.velocity, args.accel,
                  args.number,
                  args.degrees_fwd, args.degrees_back,
                  args.sleep_time,
                  args.home_start, args.home_end
                  )


def do_back_forth(
    dryrun: bool,
    limits: bool,
    velocity: float, accel: float,
    number: int,
    degrees_fwd: float, degrees_back: float,
    sleep_time: float,
    home_start: bool, home_end: bool,
):
    if dryrun:
        print('Init dry run')
        motor = StepMotor.StepMotor('dryrun')
    else:
        print('Go for it')
        motor = StepMotor.StepMotor()
    motor.InitializeDrive(enable_limits=limits,
                          vel=velocity,
                          accel=accel,
                          )
    if home_start:
        motor.GoHome()
        log_sleep(sleep_time)
    for n in range(number):
        logging.info(f'{n=}/{number}')
        logging.info(f'Move: {degrees_fwd} deg')
        motor.MoveDegrees(degrees_fwd)
        log_sleep(sleep_time)
        logging.info(f'Move: {degrees_back} deg')
        motor.MoveDegrees(-1 * degrees_back)
        log_sleep(sleep_time)
    if home_end:
        motor.GoHome()

    return "\nDone\n"

def log_sleep(t):
    logging.debug(f'Sleeping {t}')
    time.sleep(t)

if __name__ == '__main__':
    main()
# vim:expandtab:sw=4:ts=4
