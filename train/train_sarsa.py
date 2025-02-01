from algorithms.SARSA.train import train
from pipeline import Pipeline
from environment import Environment

if __name__ == "__main__":
    # Initialize your pipeline
    pipeline = Pipeline() 
    pipeline.init()
    # # Initialize your environment
    env = Environment(pipeline)

    train(env, 5000)