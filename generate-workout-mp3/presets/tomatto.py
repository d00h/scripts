from workout import Workout

with Workout.from_cmdline(name="tomatto") as w:
    w.say("breath").wait(seconds=30)
    for _ in range(4):
        w.say("prepare").wait(seconds=3)
        w.say("work").wait(minutes=7)
        w.say("dont sleep").wait(minutes=7)
        w.say("work").wait(minutes=7)
        w.say("stop relax").wait(minutes=1)
        w.say("release, breath and some pushup").wait(minutes=5)
        w.say("stop callback").wait(minutes=4)

    w.say("relax").wait(minutes=1, seconds=30)
