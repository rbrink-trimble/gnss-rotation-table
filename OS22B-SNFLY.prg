;Gemini GT6 Stepper Drive Setup
;
; All of these commands set values that are stored in NV MEM in the
; GT6 controller and thus remain set after power cycling the controller.
; As such, this file only needs to be loaded into the controller once,
; but will need to be reloaded if someone issues the 'RFS' command
; (Return to Factory Settings).
;
; This file can be fed directly into the controller serial port as is..
; Everything after a ';' is a comment and ignored by the controller.
; White space is ignored by the controller.
; Blank lines are ignored by the controller.
; Lines are delimited by <LF> or <CR> characters.
;
; This file sets up controller for a specific model of stepper.
;

;Motor Setup
DMTR 21		;Motor ID (OS22B-XXFLY Parallel Wiring)
DMTSTT 158.0		;Motor Static Torque (oz-in)
DMTIC 3.36		;Continuous Current (Amps-RMS)
DMTIND 4.2		;Motor Inductance (mH)
DMTRES 0.84		;Motor Winding Resistance (Ohm)
DMTJ 25.420		;Motor Rotor Inertia (kg*m*m*10e-6)
DPOLE 50		;Number of Motor Pole Pairs
DIGNA 2.250		;Current Loop Gain A
DIGNB 0.202		;Current Loop Gain B
DIGNC 0.806		;Current Loop Gain C
DIGND 0.980		;Current Loop Gain D

;Drive Setup
DMODE 12		;Drive Control Mode
DRES 25000		;Drive Resolution (counts/rev)
ORES 0		;Encoder Output Resolution (counts/rev)
DAUTOS 0.00		;Auto Current Standby (% reduction of motor current)
DMVLIM 50.000000	;Velocity Limit (rev/sec)

;Load Setup
LJRAT 0.0		;Load-to-Rotor Inertia Ratio

;Fault Setup
FLTDSB 1		;Fault on Drive Disable Enable
ESK 1			;Fault on Stall Enable
KDRIVE 0		;Disable Drive on Kill
DSTALL 0		;Stall Detect Sensitivity

;Digital Input Setup
INFNC 1-R		;Positive End-of-Travel Input (R)
INFNC 2-S		;Negative End-of-Travel Input (S)
INFNC 3-T		;Home Limit Input (T)
INFNC 4-H		;Trigger Interrupt Input (H)
INFNC 5-A		;General Purpose Input (A)
INFNC 6-A		;General Purpose Input (A)
INFNC 7-A		;General Purpose Input (A)
INFNC 8-A		;General Purpose Input (A)
INLVL 11000000	;Input Active Level
INDEB 50		;Input Debounce Time (milliseconds)
INUFD 0		;Input User Fault Delay Time (milliseconds)
LH 0			;Hardware EOT Limits Enable
LHAD 100.0000	;Hard Limit Deceleration
LHADA 100.0000	;Hard Limit Average Deceleration

;Digital Output Setup
OUTBD 0		;Output Brake Delay Time (milliseconds)
OUTFNC 1-A		;General Purpose Output (A)
OUTFNC 2-F		;Fault Detected Output (F)
OUTFNC 3-D		;End-of-Travel Limit Hit Output (D)
OUTFNC 4-E		;Stall Detected Output - GT6 Only(E)
OUTFNC 5-B		;Moving/Not Moving Output (B)
OUTFNC 6-A		;General Purpose Output (A)
OUTFNC 7-F		;Fault Detected Output (F)
OUTLVL 0000000	;Output Active Level

;Analog Monitor Setup
DMONAV 0		;Analog Monitor A Variable
DMONAS 100		;Analog Monitor A Scaling (% of full scale output)
DMONBV 0		;Analog Monitor B Variable
DMONBS 100		;Analog Monitor B Scaling (% of full scale output)

;Motor Matching
DPHOFA 0.000	;Phase A Current Offset
DPHOFB 0.000	;Phase B Current Offset
DPHBAL 100.0	;Phase Balance
DWAVEF -4.00	;Waveform (% of 3rd harmonic)

;Electronic Damping
DACTDP 4		;Active Damping Level
DDAMPA 0		;Damping During Acceleration Enable
DELVIS 0		;Electronic Viscosity Level
DABSD 0		;ABS Damping Enable
