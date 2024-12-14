from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import asyncio
import time
import datetime

import StepMotor


# Initialize FastAPI app and Jinja2 templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Global cancel event to signal when the process should stop
cancel_event = asyncio.Event()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main web page with the form, submit, and stop buttons."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/progress")
async def stream_progress(
    dry_run: bool = Query(False),
    velocity: float = Query(1.0),
    accel: float = Query(1.0),
    sleep_seconds: float = Query(0.5),
    number: int = Query(1),
    degrees_fwd: float = Query(0.0),
    degrees_back: float = Query(0.0),
    home_start: bool = Query(True),
    home_end: bool = Query(False),
    ):
    """Stream real-time progress updates from the do_back_forth() function with user input."""
    cancel_event.clear()  # Reset cancel event when a new process starts

    async def event_generator():
        """Yield progress messages from the do_back_forth() function."""
        try:
            for progress in do_back_forth(
                dry_run, velocity, accel, sleep_seconds,
                number, degrees_fwd, degrees_back, home_start, home_end
            ):
                if cancel_event.is_set():  # Check if the process should stop
                    yield "data: Operation stopped by user.\n\n"
                    break
                yield f"data: {progress}\n\n"
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            yield "data: Operation was canceled.\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/stop")
async def stop_process():
    """Stop the do_back_forth process by setting the cancel event."""
    return {"message": "Process stopped"}

def do_back_forth(
    dry_run: bool,
    velocity: float,
    accel: float,
    sleep_seconds: float,
    number: int, degrees_fwd: float, degrees_back: float,
    home_start: bool, home_end: bool
):
    """Simulate a process that provides real-time updates using user-provided parameters."""

    yield f"{dry_run=}\t{velocity=}\t{accel=}\t{sleep_seconds=}"
    yield f"{number=}\t{degrees_fwd=}\t{degrees_back=}"
    yield f"{home_start=}\t{home_end=}\n"
    time.sleep(0.5)

    start_time = datetime.datetime.now()

    deg = 0
    if dry_run:
        print('Init dry run')
        if not dry_run:
            motor = StepMotor.StepMotor('dry_run')
    else:
        print('Go for it')
        if not dry_run:
            motor = StepMotor.StepMotor()

    if velocity and accel:
        print('Initializing Motor Parameters')
        if not dry_run:
            motor.InitializeDrive(enable_limits=False,
                          vel=velocity,
                          accel=accel,
                          )
        print('Done')

    if home_start:
        yield "Homing to start position..."
        if not dry_run:
            motor.GoHome()
        yield f"   Done"
        time.sleep(sleep_seconds)
        yield f"   Sleep Done"

    for i in range(1, number + 1):
        deg += degrees_fwd
        yield f"n:{i} - Fwd {degrees_fwd} — Position {deg} degrees"
        if not dry_run:
            motor.MoveDegrees(degrees_fwd)
        yield f"   Done"
        time.sleep(sleep_seconds)
        yield f"   Sleep Done"

        deg -= degrees_back
        yield f"n:{i} - Rev {degrees_back} — Position {deg} degrees"
        if not dry_run:
            motor.MoveDegrees(-degrees_back)
        yield f"   Done"
        time.sleep(sleep_seconds)
        yield f"   Sleep Done"

    if home_end:
        yield "Homing to end position..."
        if not dry_run:
            motor.GoHome()
        yield f"   Done"
        time.sleep(sleep_seconds)
        yield f"   Sleep Done"

    end_time = datetime.datetime.now()
    yield f'Done. Elapsed time: {end_time - start_time}'
