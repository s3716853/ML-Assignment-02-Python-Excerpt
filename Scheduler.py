import collections

class Scheduler:
    
    def __init__(self, packetScheduler, debug=False):
        #This class will assume that the packetScheduler passed into it has been fully configured before being passed in
        #queues added, seeding complete
        self.packetScheduler = packetScheduler
        self.debug = debug
    
    def start(self):
        currentState = self.packetScheduler.reset()
        
        removedPacketsAge = [[], [], []]
        
        evaluationEnded = False
        steps = 0

        while(not evaluationEnded):
            queueToTakeFrom = self._selectQueue(currentState)
            
            currentState = self.get_queues_from_state(currentState)
            
            if self.debug:
                print("===Start Step===")
                for queueIndex, queue in enumerate(currentState):
                    print("Queue No: {}: Front of Queue {}".format(queueIndex, queue[0]))
                print("Taking from Queue {}".format(queueToTakeFrom))
                print("===End Step===")
            
            #from my understanding, a -1 means no packet
            #therefore if all queues have a -1 in position 0, no packets are waiting right now    
            if currentState[queueToTakeFrom][0] == -1:
                #I'm not really sure if there is a way to move on without trying to take from a queue?
                #Not sure if trying to take from a queue with nothing in it will cause issues
                currentState, reward, evaluationEnded, message = self.packetScheduler.step(queueToTakeFrom)
            else:
                removedPacketsAge[queueToTakeFrom].append(currentState[queueToTakeFrom][0])
                currentState, reward, evaluationEnded, message = self.packetScheduler.step(queueToTakeFrom)
            steps += 1

        return removedPacketsAge, currentState, steps

    def get_queues_from_state(self, state):
        # Scenario 2 schedulers will recieve a state that is a dictionary 
        # state['queues'] = queues, same value as scenario 1 state
        # state['chosen_queue'] = the current active queue
        # this is to ensure the scheduler class can run in scenario 2
        if type(state) is collections.OrderedDict:
            return state['queues']
        return state

    def print_report(self, policy_name):
        # Turning off debug
        temp_debug = self.debug
        self.debug = False
        
        # Setting varialbes
        calculatedResults = []
        tests = 100
        num_queues = 3

        # Run 100 tests to average results for each policy
        average_steps = 0
        for i in range(tests):
            results, _, steps = self.start()
            average_steps += steps
            calculatedResults.append(Scheduler.evaluationSummary(results, env=self.packetScheduler))

        # Calculate averages
        means = [0] * num_queues
        late_packets = [0] * num_queues
        for test in calculatedResults:
            for i, queue in enumerate(test):
                means[i] += queue['mean']
                late_packets[i] += queue['packets_over_mean_delay']
        means = [i/tests for i in means]
        late_packets = [i/tests for i in late_packets]
        average_steps /= tests

        # Print results
        print(f"Policy: {policy_name}")
        print("Averages of 100 test episodes:")
        print("Steps taken = {0:.2f}".format(average_steps))
        print("---------------------------------------------")
        print("| Queue | Mean Age | No. over required mean |")
        print("---------------------------------------------")
        for i, _ in enumerate(self.packetScheduler.queue_definitions):
            print("| {0:<5} | {1:<8.2f} | {2:<22.2f} |".format(i, means[i], late_packets[i]))
        print("---------------------------------------------")
        print()

        # Retoring debug
        self.debug = temp_debug
            
    #this function must be overwritten by scheduler subclasses
    def _selectQueue(self, state):
        pass
    
    #evaluationResults formatted as the first return from start [queue1_packets_list, queue2_packets_list, queue3_packets_list, ...]
    #meanDelayRequirement is a list of delay requirements eg, [6, 4, 0]
    #associates queue with delay based on idex in array
    @classmethod
    def evaluationSummary(cls, evaluationResults, meanDelayRequirement=None, **kwargs):
        if 'env' in kwargs:
            meanDelayRequirement = kwargs['env'].get_queue_delays()
        elif meanDelayRequirement is None:
            raise ValueError("Must supply meanDelayRequirement list or environment")
        summary = []
        for queueIndex, queueResults in enumerate(evaluationResults):
            try:
                summary.append({
                    "removed_packets": queueResults,
                    "mean": cls._calculateMeanPacketAge(queueResults),
                    "packets_over_mean_delay": cls._calculatePacketsOverMeanDelay(queueResults, meanDelayRequirement[queueIndex])
                })            
            except ZeroDivisionError:
                pass # Not sure what we can do if it has a queue it didn't take packets from
        return summary
    
    @classmethod    
    def _calculateMeanPacketAge(cls, queueResults):
        packetAgeTotal = 0
        for packetAge in queueResults:
            packetAgeTotal += packetAge
        return packetAgeTotal / len(queueResults)
    
    @classmethod       
    def _calculatePacketsOverMeanDelay(cls, queueResults, meanDelayRequirement):
        packetsOverMeanDelayCount = 0
        if meanDelayRequirement == 0:
            return 0
        for packetAge in queueResults:
            if packetAge > meanDelayRequirement:
                packetsOverMeanDelayCount += 1
        
        return packetsOverMeanDelayCount