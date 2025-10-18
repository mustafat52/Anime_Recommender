import os
import pandas as pd
from google.cloud import storage
from src.logger import get_logger
from src.custm_exception import CustomException
from utils.common_func import read_yaml
from config.path_config import *


logger = get_logger(__name__)

class DataIngestion:

    def __init__(self,config_path=CONFIG_PATH):
        try:
            self.config = read_yaml(config_path)
            self.bucket_name = self.config['data_ingestion']['bucket_name']
            self.file_names = self.config['data_ingestion']['bucket_file_name']
            
            os.makedirs(RAW_DIR,exist_ok=True)
            
            logger.info("Data Ingestion Started")

        except Exception as e:
            logger.error("Error in reading the config file")
            raise CustomException("Failed to read the config file",e)

           
    def download_csv_from_gcp(self):
        try:

            client = storage.Client()
            bucket = client.bucket(self.bucket_name)

            for file_name in self.file_names:
                file_path = os.path.join(RAW_DIR,file_name)

                if file_name=="animelist.csv":
                    blob = bucket.blob(file_name)
                    blob.download_to_filename(file_path)

                    data = pd.read_csv(file_path, nrows=5000000)
                    data.to_csv(file_path, index=False)

                    logger.info("Large file Detected, only downloading 50lakh rows")

                else:
                    blob = bucket.blob(file_name)

                    blob.download_to_filename(file_path)

                    logger.info("Downloading the other two files")

        except Exception as e:

            logger.info(f"Error while downloading the file : {e}")
            raise CustomException("Erroe dusring file download",e)



    def run(self):
        try:
            logger.info("Starting the data ingestion process")

            self.download_csv_from_gcp()
            logger.info("Data Ingestion COmpleted")

        except CustomException as ce:

            logger.info(f"CustomeException : {str(ce)}")

        finally:
            logger.info("Data Ingestion DONE")


if __name__ == "__main__":

    data_ingestion = DataIngestion(CONFIG_PATH)
    data_ingestion.run()





    
    