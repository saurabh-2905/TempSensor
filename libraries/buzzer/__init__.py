from machine import Pin, PWM


class Buzzer:
    def __init__(self, buzzerPin):
        # pwm = PWM(0, frequency=5000)
        self.buzzerPin = buzzerPin
        self.pwm = PWM(0, frequency=0)
        self.buzzerChannel = self.pwm.channel(0, pin=buzzerPin, duty_cycle=0.5)

    def playAlarm(self):
        self.buzzerChannel = PWM(0, frequency=1000).channel(0, pin=self.buzzerPin, duty_cycle=0.5)

    def stopAlarm(self):
        self.buzzerChannel = PWM(0, frequency=0).channel(0, pin=self.buzzerPin, duty_cycle=0)