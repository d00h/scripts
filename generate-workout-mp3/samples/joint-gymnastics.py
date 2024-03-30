from workout import Workout

with Workout.from_cmdline(name="warmup") as w:
    w.say("warmup").wait(seconds=1)
    w.say("one two three").wait(seconds=1)
    w.say("prepare").wait(seconds=5)
    w.say("breath").wait(seconds=30)
    for part in [
        "legs", "head", "shoulders", "body", "elbows", "hands",
        "hips", "knees", "feet",
    ]:
        w.say(f"prepare {part}").wait(seconds=90)
    w.say("relax").wait(minutes=1, seconds=30)


