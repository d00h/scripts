from workout import Workout

with Workout.from_cmdline(name="bboy-monkey") as w:
    w.say("prepare").wait(seconds=5)

    for _ in range(5):
        w.say("down").wait(seconds=5)
        w.say("up").wait(seconds=5)

    w.say("relax").wait(minutes=1)

    for _ in range(5):
        w.say("down", "monkey right", "up").wait(seconds=30)
        w.say("down", "monkey left", "up").wait(seconds=30)
