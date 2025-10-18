from tensorflow.keras.models import Model
from tensorflow.keras.layers import Layer, Input,Embedding,Dot,Flatten,Dense, Activation, BatchNormalization
from utils.common_func import read_yaml
from src.logger import get_logger
from src.custm_exception import CustomException


logger = get_logger(__name__)


class BaseModel:
    def __init__(self, config_path):
        try:
            self.config_path = read_yaml(config_path)
            logger.info("Loaded from Config Path")
        except Exception as e:
            raise CustomException("Error Loading config path",e)


    def RecommenderNet(self, n_users, n_anime):

        
        try:

            embedding_size = self.config_path["model"]["embedding_size"]

            user = Input(name="user", shape=[1])

            user_embedding = Embedding(name="user_embedding", input_dim=n_users, output_dim=embedding_size)(user)

            anime = Input(name="anime", shape=[1])

            anime_embedding = Embedding(name="anime_embedding", input_dim=n_anime, output_dim=embedding_size)(anime)

            x = Dot(name="dot_product", normalize=True, axes=2)([user_embedding,anime_embedding])

            x = Flatten()(x)


            x = Dense(1, kernel_initializer='he_normal')(x)

            x = BatchNormalization()(x)

            x = Activation("sigmoid")(x)

            model = Model(inputs=[user, anime], outputs=x)

            model.compile(
                loss = self.config_path["model"]["loss"],
                optimizer = self.config_path["model"]["optimizer"],
                metrics = self.config_path["model"]["metrics"]
            )
            logger.info("Model Cretaed Sucessfully.......")
            return model        

        except Exception as e:
            logger.error(f"Error occured during model Architecture : {e}")
            raise CustomException("Error in Model Architecture ",e)

