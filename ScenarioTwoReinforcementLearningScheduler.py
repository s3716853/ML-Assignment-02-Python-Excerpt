import numpy as np

from .ReinforcementLearningScheduler import ReinforcementLearningScheduler
class ScenarioTwoReinforcementLearningScheduler(ReinforcementLearningScheduler):
    
    #Initial Q Table Config
    INITIAL_Q_TABLE_REWARD_MIN = -3
    INITIAL_Q_TABLE_REWARD_MAX = -1
    
    def __init__(self, packetScheduler, maxPacketAge, noQueues=None, debug=False):
        super().__init__(packetScheduler, maxPacketAge, noQueues, debug)
        
    def resetQTable(self, min=INITIAL_Q_TABLE_REWARD_MIN, max=INITIAL_Q_TABLE_REWARD_MAX):
        #Scenario two has the extra variable of queue switching
        #therefore we need an extra dimension in this q_table
        self.qTable = np.random.uniform(low=min, high=max, size=([self.maxPacketAge] * self.noQueues + [self.noQueues] + [self.noQueues]))

    def _discretiseState(self, state):
        currentActiveQueue = state['chosen_queue']
        queues = state['queues']
        firstPacketInStates = []
        for queue in queues:
            index = queue[0] + 1
            if index < self.maxPacketAge:
                firstPacketInStates.append(index)
            else:
                firstPacketInStates.append(self.maxPacketAge - 1)
        firstPacketInStates.append(currentActiveQueue)
        return tuple(firstPacketInStates)