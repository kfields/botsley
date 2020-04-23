TS_INITIAL = "Initial"
TS_RUNNING = "Running"
TS_SUCCESS = "Success"
TS_FAILURE = "Failure"
TS_SUSPENDED = "Suspended"
TS_HALTED = "Halted"

class Runner:
    def __init__(self):
        self.queue = []
        self.callbacks = []

    def schedule(self, task):
        if type(task) is function:
            task = Task()
            task.use(method()
        task.start()
        self.queue.append(task)

    def reschedule(self, task):
        task.status = TS_RUNNING
        self.queue.append(task)

    def step(self):
        queue = self.queue
        self.queue = []
        for task in queue:
            print('task', task)
            print('task.status', task.status)
            try:
                #print(task.coro)
                awaited = task.coro.send(task.awaited.result if task.awaited else None)
                print('awaited', awaited)
                if awaited:
                    task.status = TS_SUSPENDED
                    task.awaited = awaited
                    awaited.awaiter = task
                    self.schedule(awaited)

            except StopIteration as exception:
                result = exception.value
                print('stop result', result)
                task.result = result
                if task.awaiter:
                    print('task.awaiter', task.awaiter)
                    self.reschedule(task.awaiter)

            #except Failure as exception:

        callbacks = self.callbacks
        self.callbacks = []
        for callback in callbacks:
            callback()

    def run(self, task):
        self.schedule(task)
        while len(self.queue) != 0:
            self.step()

runner = Runner()