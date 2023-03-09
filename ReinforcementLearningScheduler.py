import numpy as np

from .Scheduler import Scheduler
class ReinforcementLearningScheduler(Scheduler):
    
    #Initial Q Table Config
    INITIAL_Q_TABLE_REWARD_MIN = -3
    INITIAL_Q_TABLE_REWARD_MAX = -1
    
    #For now, these hyperparamater values are being taken straight from the tutes,
    #But tuning should be done later to see if better values can be found
    LEARNING_RATE = 0.1
    DISCOUNT = 0.95
    EPISODES = 5000
    EARLY_FINISH_REWARD_PER_STEP = None

    #parameters for epsilon decay policy
    EPSILON = 1 #not a constant, going to be decayed
    START_EPSILON_DECAYING = 1
    END_EPSILON_DECAYING = EPISODES
    epsilon_decay_value = EPSILON / (END_EPSILON_DECAYING - START_EPSILON_DECAYING)
    
    def __init__(self, packetScheduler, maxPacketAge, noQueues=None, debug=False):
        if noQueues is None:
            noQueues = len(packetScheduler.queue_definitions)
        self.maxPacketAge = maxPacketAge
        self.noQueues = noQueues
        self.resetQTable()
            
        super().__init__(packetScheduler, debug)
    
    def _selectQueue(self, state):
        discreteState = self._discretiseState(state)
        #Select the action that will give the greatest reward
        #as defined by our q learning function
        return np.argmax(self.qTable[discreteState]) 
    
    # packetScheduler: The scheduler environment
    # qTable: Initial Q table (should have random values)

    def resetQTable(self, min=INITIAL_Q_TABLE_REWARD_MIN, max=INITIAL_Q_TABLE_REWARD_MAX):
        # For maxPacketAge = 20, noQueues = 3,
        # The q-table would be dimension 20 x 20 x 20 x 3
        # For maxPacketAge = 20, noQueues = 4,
        # The q-table would be dimension 20 x 20 x 20 x 20 x 4
        self.qTable = np.random.uniform(low=min, high=max, size=([self.maxPacketAge] * self.noQueues + [self.noQueues]))

    def qLearning(self, packetScheduler):

        for episode in range(self.EPISODES):
            done = False

            # get the initial state
            state = packetScheduler.reset()
            discreteState = self._discretiseState(state)

            epsilon = self.EPSILON
            step_count = 0
            while not done:   

                # Determine next action - epsilon greedy strategy for explore vs exploitation
                if np.random.random() < 1 - epsilon:
                    # select the best action according to Qtable (exploitation)
                    action = np.argmax(self.qTable[discreteState]) 
                else:
                    # select a random action (exploration)
                    # Take from random queue, represented by an integer of its location in
                    # queue list
                    action = np.random.randint(len(discreteState)-1)

                # Get next state and reward
                stateNew, reward, done, message = packetScheduler.step(action)
                step_count += 1
                discreteStateNew = self._discretiseState(stateNew)

                # Change reward if finished early and EARLY_FINISH_REWARD is set
                if done and self.EARLY_FINISH_REWARD_PER_STEP is not None and step_count < packetScheduler.simulation_length:
                    reward = self.EARLY_FINISH_REWARD_PER_STEP

                # Update the Q table
                NewMaxQ = np.max(self.qTable[discreteStateNew])
                currentQ = self.qTable[discreteState+(action, )]
                self.qTable[discreteState+(action, )] = (1-self.LEARNING_RATE)*currentQ + self.LEARNING_RATE*(reward + self.DISCOUNT*NewMaxQ)

                # Update variables
                discreteState = discreteStateNew

            # Update epsilon
            if self.END_EPSILON_DECAYING >= episode and episode >= self.START_EPSILON_DECAYING:
                epsilon -= self.epsilon_decay_value
            
            # Print report after the first episode and after every 10%
            if ((episode + 1) % (self.EPISODES/5) == 0) or episode == 0:
                print(f"After {episode + 1} episodes")
                self.print_report("RL")


        return self.qTable
    
    #The Q-Table for the reinforcement learning problem will only deal with the first element in each queue
    #To reduce the Q-Table dimensions
    #This method could be overwritten by a subclass to attempt different dimension minimisation strategies
    #One idea could be basing it on number of elements in queue
    #As a note for the eventual report, could talk about the different possible Q-Table reductions
    def _discretiseState(self, state):
        firstPacketInStates = []
        for queue in state:
            index = queue[0] + 1
            if index < self.maxPacketAge:
                firstPacketInStates.append(index)
            else:
                firstPacketInStates.append(self.maxPacketAge - 1)
        return tuple(firstPacketInStates)