from botsley.run.agent import Agent

class Agency:
    def __init__(self):
        self.agents = []

    def add_agent(self, agent):
        self.agents.append(agent)

    def run(self, task):
        #self.add_agent()
        agent = Agent()
        agent.run(task)

agency = Agency()