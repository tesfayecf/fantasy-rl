from pipeline import Pipeline

if __name__ == '__main__':
    pipeline = Pipeline()
    pipeline.init()

    for i in range(100):
        pipeline.get_player()   
