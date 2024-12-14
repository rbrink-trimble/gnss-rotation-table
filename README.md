# Rotation Table

This repo is based on the FCI spin-test repo (ssh://git@bitbucket.trimble.tools/fci-mfg/spin-test.git).
But, with some significant differences - enogh that it might be considered more
than just a fork.  All the networking, report generation, and phased array stuff
has been removed. Mostly, just the StepMotor.py code has been kept, and coverted
from python 2.7 to python 3.x

# Install

Do something like:

   ```
   brew install python-tk
   python -m venv env_spin
   . env_spin/bin/activate
   pip install pyserial fastapi uvicorn jinja2
   ```

Run the GUI: `uvicorn main:app --reload`

Connect to the web UI at: [localhost:8080](http://localhost:8080)

*-- OR --*

Run the CLI: `python back_forth.py`

# Spin Test

The Spin Test uses a turntable and a 'parnter station' to test a Phocus Array
or DF System. For either piece of equipment, one goal is to provide a functional
test. For the DF Systems, an additional goal is the measure the Angle of Arrival
(AoA) accuracy.

A serial port, typically a USB adapter that shows up as `/dev/ttyUSB0` is used
communicate with the stepper motor controller.
