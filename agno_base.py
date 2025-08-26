"""
Simple Agent base class to replace Agno framework dependency
This provides the basic structure needed for the multi-agent system
"""

class Agent:
    """Base Agent class for the multi-agent system"""
    
    def __init__(self, name: str = "", description: str = "", instructions: list = None):
        self.name = name
        self.description = description
        self.instructions = instructions or []
    
    def __str__(self):
        return f"Agent({self.name}: {self.description})"
    
    def __repr__(self):
        return self.__str__()
