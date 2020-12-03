import time
from datetime import datetime, timedelta
from multiprocessing import Process

from devices import relay


class PWM:
    def __init__(self, start: datetime, end: datetime, duty_cycle: float):
        self._start = start
        self._end = end
        self._duty_cycle_time = 0
        self.period = timedelta(seconds=0)
        self.state = False
        self.running_time = 0
        self.device = None
        self.current_state = "off"
        self.process_running = None
        if duty_cycle > 1.0:
            self._duty_cycle = duty_cycle / 100.0
            if self._duty_cycle > 1.0:
                raise Exception("the Duty Cycle should be a float 0 < duty_cycle <= 1")
        else:
            self._duty_cycle = duty_cycle

    def set_device(self, device: str, hostname: str, name: str = None):
        if device == "relay":
            self.device = relay.Relay(hostname=hostname, name=name)

    def set_period(
        self, milliseconds=0, seconds=0, minutes=0, hours=0, days=0, weeks=0
    ):
        self.period = timedelta(
            days=days,
            seconds=seconds,
            milliseconds=milliseconds,
            minutes=minutes,
            hours=hours,
            weeks=weeks,
        )
        self._duty_cycle_time = self.period.total_seconds() * self._duty_cycle

    def __on(self):
        self.device.turn_on()

    def __off(self):
        self.device.turn_off()

    def __pwm_loop(self):
        if self.period.total_seconds() <= 0:
            raise Exception(
                "Time expired or period not set -> period = {}".format(
                    self.period.total_seconds()
                )
            )
        self.running_time = time.time()
        while self._start < datetime.now() <= self._end:
            time_now = datetime.fromtimestamp(time.time()) - datetime.fromtimestamp(
                self.running_time
            )
            if time_now.total_seconds() < self.period.total_seconds():
                if time_now.total_seconds() <= self._duty_cycle_time:
                    if self.current_state == "off":
                        print("turning on")
                        self.__on()
                        self.current_state = "on"
                else:
                    if self.current_state == "on":
                        print("turning off")
                        self.__off()
                        self.current_state = "off"

            else:
                self.running_time = time.time()

    def start_pwm(self):
        try:
            pwm_process = Process(target=self.__pwm_loop, daemon=True)
            pwm_process.start()
            self.process_running = pwm_process
        except Exception as error:
            raise Exception("error starting PWM module -> {}".format(error))

    def terminate_process(self):
        self.process_running.terminate()

    def get_config(self):
        return dict(
            start=self._start,
            end=self._end,
            duty_cycle=self._duty_cycle,
            period=self.period,
            current_state=self.current_state,
        )
