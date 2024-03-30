import random

from workout import Workout

with Workout.from_cmdline(name="joint-gymnastics") as w:
    w.say("warmup and joint gymnastic").wait(seconds=1)
    w.say("one two three").wait(seconds=1)
    w.say("prepare").wait(seconds=5)
    w.say("breath").wait(seconds=30)

    for _ in range(50):
        w.say("up").wait(seconds=1)
        w.say("down").wait(seconds=1)

    for part in [
        "head", "shoulders", "body", "elbows", "hands",
        "hips", "knees", "feet",
    ]:
        w.say(f"follow {part}").wait(seconds=30)

    for _ in range(4):
        w.say("next roll down").wait(seconds=15)
        w.say("exile").wait(seconds=5)
        w.say("relax").wait(seconds=30)
        w.say("forward").wait(seconds=15)
        w.say("down").wait(seconds=15)
        w.say("upward facing dog").wait(seconds=20)
        w.say("downward facing dog").wait(seconds=30)
        for _ in range(4):
            w.say("left").wait(seconds=5)
            w.say("right").wait(seconds=5)
        w.say("next roll up").wait(seconds=15)

    w.say("relax").wait(minutes=1, seconds=30)
