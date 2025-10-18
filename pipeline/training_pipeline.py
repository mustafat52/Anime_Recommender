from config.path_config import *

from src.data_processing import DataProcessor
from src.model_training import ModelTraining
from utils.common_func import read_yaml




if __name__ == "__main__":

    
    DataProcessor = DataProcessor(ANIMELIST_CSV,PROCESSED_DIR)
    DataProcessor.run()

    model_trainer = ModelTraining(PROCESSED_DIR)
    model_trainer.train_model()