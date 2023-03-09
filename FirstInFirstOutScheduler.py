from .Scheduler import Scheduler
class FirstInFirstOutScheduler(Scheduler):      
    def _selectQueue(self, state):
        
        queues = self.get_queues_from_state(state)
        
        queueToTakeFrom = 0
        for queueIndex, queue in enumerate(queues):
            #if age of packet first in queue is older than the previously found oldest
            #set that queue as the one to take from instead
            if(queue[0] > queues[queueToTakeFrom][0]):
                queueToTakeFrom = queueIndex
        return queueToTakeFrom