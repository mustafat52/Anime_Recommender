import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custm_exception import CustomException
from config.path_config import *
import sys



logger = get_logger(__name__)

class DataProcessor:
    def __init__(self, input_file, output_dir):

        self.input_file = input_file
        self.output_dir = output_dir

        self.rating_df = None
        self.anime_df = None

        self.X_train_arr = None
        self.X_test_arr = None
        self.y_train = None
        self.y_test = None

        self.user2user_encoded = {}
        self.user2user_decoded = {}
        self.anime2anime_encoded = {}
        self.anime2anime_decoded = {}

        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("-------------------------DATA PROCESSING INITIALIZED-----------------------------")


    def load_data(self, usecols):
        try:
            self.rating_df = pd.read_csv(self.input_file, low_memory=True, usecols=usecols)

            logger.info("Data loaded successfully for data Processing")
       
        except Exception as e:

            logger.error("Failed to load data",e)
            raise CustomException("Failed to load data", sys)


    def filter_users(self,min_rating=400):

        try:
            n_ratings = self.rating_df["user_id"].value_counts()
            self.rating_df = self.rating_df[self.rating_df["user_id"].isin(n_ratings[n_ratings>400].index)].copy()

            logger.info("FIltered users sucessfully")

        except Exception as e:

            logger.error("Failed to filter data",e)
            raise CustomException("Failed to filter data", sys)   


    def scale_ratings(self):
        try:
            min_rating = min(self.rating_df["rating"])
            max_rating = max(self.rating_df["rating"])

            


            self.rating_df["rating"] = self.rating_df["rating"].apply(lambda x :(x-min_rating)/(max_rating-min_rating)).values.astype(np.float64)
            logger.info("Scaling done for processing")


        
        except Exception as e:

            logger.error("Failed to scale data",e)
            raise CustomException("Failed to scale data", sys)   
        

    def encode_data(self):

        try:

            user_ids = self.rating_df["user_id"].unique().tolist()
            self.user2user_encoded = {x : i for i, x in enumerate(user_ids)}
            self.user2user_decoded = {i : x for i, x in enumerate(user_ids)}      
            self.rating_df["user"] = self.rating_df["user_id"].map(self.user2user_encoded)
        


            anime_ids = self.rating_df["anime_id"].unique().tolist()
            self.anime2anime_encoded = {x : i for i, x in enumerate(anime_ids)}
            self.anime2anime_decoded = {i : x for i, x in enumerate(anime_ids)}
            self.rating_df["animeID"] = self.rating_df["anime_id"].map(self.anime2anime_encoded)


            logger.info("Encodings done for anime and users")

        except Exception as e:
            logger.error("Failed to do the enodings",e)
            raise CustomException("Failed to do the encodings",sys)


    def  split_data(self,test_size=1000, random_state=43):

        try:

            self.rating_df = self.rating_df.sample(frac=1,random_state=43).reset_index(drop=True) 
            
            X = self.rating_df[["user","animeID"]]
            y = self.rating_df["rating"]

            
            train_indices = self.rating_df.shape[0]-test_size

            X_train, X_test,y_train,y_test = (
                X[:train_indices],
                X[train_indices:],
                y[:train_indices],
                y[train_indices:]
                )
            
            X_train = X_train.to_numpy()
            X_test = X_test.to_numpy()
            
            self.X_train_array = [X_train[:,0], X_train[:,1]]
            self.X_test_array = [X_test[:,0], X_test[:,1]]

            self.y_test = y_test
            self.y_train = y_train

            logger.info("Data splitting Done")

        except Exception as e:
            logger.error("Failed to split the data",e)
            raise CustomException("Failed to split the data",sys)



    def save_artifacts(self):

        try: 
            artifacts = {
                "user2user_encoded" : self.user2user_encoded,
                "user2user_decoded" : self.user2user_decoded,
                "anime2anime_encoded" : self.anime2anime_encoded,
                "anime2anime_decoded" : self.anime2anime_decoded,
            }

            for name, data in artifacts.items():
                joblib.dump(data, os.path.join(self.output_dir, f"{name}.pkl"))

                logger.info(f"{name} sucessfully in processed directory")

            joblib.dump(self.X_train_array, X_TRAIN_ARRAY )
            joblib.dump(self.X_test_array, X_TEST_ARRAY)
            joblib.dump(self.y_train, Y_TRAIN)
            joblib.dump(self.y_test, Y_TEST)


            self.rating_df.to_csv(RATING_DF, index=False)


            logger.info("All the training testing and rating_df has been saved ")

        except Exception as e:
            logger.error("Failed to save the data",e)
            raise CustomException("Failed to save the data",sys)




    def process_anime_data(self):

        try:
            df = pd.read_csv(ANIME_DF)
            
            COLS = ["MAL_ID", "Name", "Genres", "sypnopsis"]
            synopsis_df = pd.read_csv(ANIME_SYNOPSIS_DF, usecols=COLS)

            df =  df.replace("Unknown", np.nan)
            
            def get_anime_name(anime_id):    
                try:
                    name = df[df.anime_id == anime_id].eng_version.values[0]
                    if name is np.nan:
                        name = df[df.anime_id == anime_id].Name.values[0]
                except:
                    print("error")
                return name


            df["anime_id"] = df["MAL_ID"]
            df["eng_version"] = df["English name"]

            df["eng_version"] = df.anime_id.apply(lambda x : get_anime_name(x))

            df.sort_values(["Score"], 
                        inplace=True, 
                        ascending=False,
                        kind="quicksort",
                        na_position="last"
                        )
            
            df = df[["anime_id", "eng_version", "Score", "Genres","Episodes","Type","Premiered","Members"]]

            df.to_csv(DF, index=False)
            synopsis_df.to_csv(SYNOPSIS_PATH, index=False)


            logger.info("DF and Synopsis_df saved sucessfully")


        except Exception as e:
            logger.error("Failed to save the anime_df and synopsis_df",{e})
            raise CustomException("Failed to save the anime_df and synopsis_df",sys)



    def run(self):
        try:
            self.load_data(usecols=["user_id", "anime_id","rating" ])
            self.filter_users()
            self.scale_ratings()
            self.encode_data()
            self.split_data()
            self.save_artifacts()
            self.process_anime_data()

            logger.info("Data Processing Pipeline Completed Successfuly")

        except Exception as e:

            logger.error("Failure in Pipeline",str(e))
            raise CustomException("Failure in pipleine",sys)




if __name__ == "__main__":
    DataProcessor = DataProcessor(ANIMELIST_CSV,PROCESSED_DIR)
    DataProcessor.run()                       