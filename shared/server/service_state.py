class ServiceState:
    def __init__(self):
        self.running = True

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True

    def is_running(self) -> bool:
        return self.running