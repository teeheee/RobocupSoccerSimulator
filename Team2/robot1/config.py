#Konfiguration

#Episoden Einteilung

POPULATING_EPISODES = 100 # populate the model for x episodes before starting with training
LEARNING_EPISODES = 5000 # Train the model for x episodes
TESTING_EPISODES = 100 # Test the model for x episodes
LEARNING_DELAY = 10 #do the training every x episodes

#Memory Config

MEMORY_SIZE = 250000 # Number of random states in Training Memory
MEMORY_SAMPLE_PERCENTAGE = 0.2 # percentage of random states from each episode for Training Memory
REGRED = 0.95
GREEDY = 0.98 # Random movment probability decrease factor

#Neuralnetwork Config

LEARNING_RATE = 0.02 # learning Rate
LEARNING_DEPTH = 100 # Number of learning iterations on same Training Memory
