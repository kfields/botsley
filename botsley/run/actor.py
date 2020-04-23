from botsley.run.policy import Policy

class Actor(Policy):
    def __init__(self, agency):
        self.agency = agency
        self.queue = asyncio.Queue()
        self.active = True

    def send(self, msg):
        pass

    async def receive(self):
        await self.queue.get()

    async def call(self, msg):
        self.agency.post(msg)
        await self.queue.get()