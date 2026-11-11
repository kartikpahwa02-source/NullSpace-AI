from agents.all_agents import (
    GameAgent, CommunicationAgent, PhoneAgent, PhotoAgent,
    SmartHomeAgent, AutomationAgent, CallAgent, RecordAgent,
    ResearchAgent, FileAgentClass, BrowserAgentClass, CodeAgent, SystemAgent
)


class AgentRegistry:
    def __init__(self):
        self.agents = [
            GameAgent(), CommunicationAgent(), PhoneAgent(), PhotoAgent(),
            SmartHomeAgent(), AutomationAgent(), CallAgent(), RecordAgent(),
            ResearchAgent(), FileAgentClass(), BrowserAgentClass(), CodeAgent(), SystemAgent(),
        ]

    def find_agent(self, command):
        matches = []
        for a in self.agents:
            if a.can_handle(command):
                score = self._score(a, command)
                matches.append((a, score))
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[0][0]
        return None

    def _score(self, agent, command):
        cmd = command.lower(); s = 0
        km = {
            "Game Agent": ["game","khel","play","bgmi","pubg","gta","minecraft","chess","ludo","free fire","subway"],
            "Communication Agent": ["whatsapp","message","bhejo","sms","telegram"],
            "Phone Agent": ["phone","mobile","android","phone screenshot","phone gallery"],
            "Photo Agent": ["photo","filter","crop","resize","watermark","image search"],
            "SmartHome Agent": ["light","fan","ac ","room","scene","smart"],
            "Automation Agent": ["open","notepad","calculator","type","screenshot"],
            "Call Agent": ["call","ring","dial","contact","call log"],
            "Record Agent": ["record","recording","voice memo"],
            "Code Agent": ["code","program","python","script","coding"],
            "System Agent": ["system","cpu","ram","process","network","wifi","port","startup"],
        }
        for kw in km.get(agent.name, []):
            if kw in cmd: s += 10
        return s

    def get_all_status(self):
        return [a.get_status() for a in self.agents]


_registry = None

def get_registry():
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry