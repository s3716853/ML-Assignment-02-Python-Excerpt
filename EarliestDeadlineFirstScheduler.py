from .Scheduler import Scheduler
class EarliestDeadlineFirstScheduler(Scheduler):
    def __init__(self, packetScheduler, queueDelayRequirements=None, debug=False):
        if queueDelayRequirements is None:
            queueDelayRequirements = packetScheduler.get_queue_delays()
        self.queueDelayRequirements = queueDelayRequirements
        super().__init__(packetScheduler, debug)
            
    def _selectQueue(self, state):
        queueToTakeFrom = 0
        
        queues = self.get_queues_from_state(state)
        
        for queueIndex, queue in enumerate(queues):
            delayPacketAgeDifference = self._getDelayRequirementPacketAgeDifference(queue, queueIndex)
            prevDelayPacketAgeDifference = self._getDelayRequirementPacketAgeDifference(queues[queueToTakeFrom], queueToTakeFrom)
            #-1 signifieis no packet, therefore means no packet in front of queue
            if(queue[0] == -1):
                continue
            #No packet in front of previous best chosen one either
            #deals with the loop starting with queueToTakeFrom = 0, where queue zero could have nothing in it
            #making age comparison not work (as the maths will treat -1 as an age)
            elif(queues[queueToTakeFrom][0] == -1):
                queueToTakeFrom = queueIndex
            elif(delayPacketAgeDifference < prevDelayPacketAgeDifference):
                queueToTakeFrom = queueIndex
            
        return queueToTakeFrom
    
    def _getDelayRequirementPacketAgeDifference(self, queue, queueIndex):
        packetAge = queue[0]
        delayRequirement = self.queueDelayRequirements[queueIndex]
        
        #not too sure about this right now
        #issue I was having is that one queue is 'best effort' so I wasnt sure how you implement that into an
        #earliest deadline first algorithm, since it has no deadline.
        #opted for dealing with the other queues first, and once those have nothing in them, 'best effort' queues can be dealt with
        if(delayRequirement == 0):
            #2147483647 is the max python integer value (which isnt really a thing in python 3 since you can go over and python turns it into a long)
            #however, I had to pick some large number to say "this queue is not a priority, deal with the other first" 
            #that wouldnt be the delay requirement for another queue
            return 2147483647
        
        delayPacketAgeDifference = delayRequirement - packetAge
        return delayPacketAgeDifference
        