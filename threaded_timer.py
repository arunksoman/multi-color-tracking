from threading import Timer
import math
import time

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def job(r, pi):
    print(pi * r * 2)
    
timer = RepeatTimer(1, job, args = (5, 3.14))
timer.start()
time.sleep(6)
timer.cancel()
