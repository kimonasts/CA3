
from time_conversions import hhmm_to_seconds
from time_conversions import current_time_hhmm
from flask import Flask
from flask import request
from flask import render_template
import pyttsx3
import time
import sched

s = sched.scheduler(time.time, time.sleep)
app = Flask(__name__)
engine = pyttsx3.init()
notifications = []
alarms = []

@app.route('/')
def controller():
    s.run(blocking=False)
    alarm_time = request.args.get("alarm")
    notifications = [{ 'title': 'Module leader', 'content':'ECM1400 Deadline reminder 4th December' }]
    if alarm_time:
        #convert alarm_time to a delay
        alarm_hhmm = alarm_time[-5:-3] + ':' + alarm_time[-2:]
        delay = hhmm_to_seconds(alarm_hhmm) - hhmm_to_seconds(current_time_hhmm())
        s.enter(int(delay), 1, announce, [notifications[0]['content'],])
    return render_template('index.html', title='Daily update', notifications=notifications, image='alarm-meme.jpg')

def announce(announcement):
    try:
        engine.endLoop()
    except:
        pass
    engine.say(announcement)
    engine.runAndWait()

if __name__ == '__main__':
    app.run()
