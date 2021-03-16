from .threads import EmptyTask, MainTask


class Application():
    
    def __init__(self, *, debug=False):
        self.debug = debug

    def run(self):
        waiting_thread = EmptyTask()
        main_thread = MainTask(debug=self.debug)
        main_thread.loop = True

        waiting_thread.start()
        main_thread.start()

        waiting_thread.join()
        main_thread.loop = False

        main_thread.join()
