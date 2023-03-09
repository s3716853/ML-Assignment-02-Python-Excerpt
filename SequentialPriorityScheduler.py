from .Scheduler import Scheduler
class SequentialPriorityScheduler(Scheduler):  
    
    QUEUE_INDEX = "Queue_Index"
    QUEUE_DELAY = "Queue_Delay"
    BEST_EFFORT = 0
    EMPTY_PACKET = -1
    
    def __init__(self, packetScheduler, queueDelayRequirements=None, debug=False):
        if queueDelayRequirements is None:
            queueDelayRequirements = packetScheduler.get_queue_delays()
        self.queueDelayRequirements = self._delayRequirementsAsSortedListOfDictionaries(queueDelayRequirements)
        super().__init__(packetScheduler, debug)
        
    def _selectQueue(self, state):
        queueToTakeFrom = 0
        
        queues = self.get_queues_from_state(state)
        
        #Goes down the sorted list, and will use the first queue with a packet it finds
        for queueSpecification in self.queueDelayRequirements:
            if(queues[queueSpecification[self.QUEUE_INDEX]][0] != self.EMPTY_PACKET):
                queueToTakeFrom = queueSpecification[self.QUEUE_INDEX]
                break
            
        return queueToTakeFrom
    
    #Turns the delay requirements list into a list of dicitonaries
    #Each dictionary has:
    #QUEUE_INDEX: Represents the queues index in packetScheduler and is used to interact with packetScheduler
    #QUEUE_DELAY: The delay for the queue at the index
    #The list is sorted from smallest delay requirement, to largest
    def _delayRequirementsAsSortedListOfDictionaries(self, queueDelayRequirements):
        queueDelayRequirementsAsDictionary = []
        
        bestEffortQueueRequirements = []
        
        for queueIndex, queueDelay in enumerate(queueDelayRequirements):
            if(queueDelay == self.BEST_EFFORT):
                bestEffortQueueRequirements.append({
                    self.QUEUE_INDEX: queueIndex,
                    self.QUEUE_DELAY: queueDelay
                })
            else:
                queueDelayRequirementsAsDictionary.append({
                    self.QUEUE_INDEX: queueIndex,
                    self.QUEUE_DELAY: queueDelay
                })
        
        def sortingFunction(delayRequirement):
            return delayRequirement[self.QUEUE_DELAY]
        
        queueDelayRequirementsAsDictionary.sort(key=sortingFunction)
        
        #best effort queues are represented with delay 0, which would put them at the top of the sorted list
        #however, they should be at the bottom as they have no delay requirment
        #therefore I'm appending them after the rest have been sorted
        for bestEffortRequiremnt in bestEffortQueueRequirements:
            queueDelayRequirementsAsDictionary.append(bestEffortRequiremnt)
        
        return queueDelayRequirementsAsDictionary