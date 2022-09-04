from threading import Lock, Thread
import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub
import os
import tensorflow_recommenders as tfrs
import numpy as np
#for singleton architecture
class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances = {}
    _model = None
    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        # Now, imagine that the program has just been launched. Since there's no
        # Singleton instance yet, multiple threads can simultaneously pass the
        # previous conditional and reach this point almost at the same time. The
        # first of them will acquire lock and will proceed further, while the
        # rest will wait here.
        with cls._lock:
            # The first thread to acquire the lock, reaches this conditional,
            # goes inside and creates the Singleton instance. Once it leaves the
            # lock block, a thread that might have been waiting for the lock
            # release may then enter this section. But since the Singleton field
            # is already initialized, the thread won't create a new object.
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]



class RecommenderEngine(metaclass=SingletonMeta):
    """
    RecommenderEngine merupakan singleton yang akan menjadi search engine utama dalam aplikasi ini
    class ini akan mencari text yang secara semantik memiliki kesamaan menggunakan TopK Factorization

    diperlukan index untuk memulai predict
    """
    model = None
    index = None
    """
    We'll use this property to prove that our Singleton really works.
    """

    def __init__(self) -> None:

        self.model = self.build_model_local()
        try:
            # ScaNN is an optional dependency, and might not be present.
            from scann import scann_ops
            _HAVE_SCANN = True
            self.index = tfrs.layers.factorized_top_k.ScaNN(self.model)
        except ImportError:
            _HAVE_SCANN = False
            self.index = tfrs.layers.factorized_top_k.BruteForce(self.model)
        print("INI SINGLE TON")


    def generate_index(self, data: pd.DataFrame, feature: str, identifier: str):
        """

        :param data: data merupakan pandas dataframe dengan 2 kolom yaitu kolom "room_id" dan "vector"
                     Vector merupakan data float32 128 dimensi
        :param feature: fitur merupakan nama kolom dari candidate vector
        :param identifier: identifier merupakan nama kolom dari rows candidate tersebut
        :return: None
        """
        self.index.index(np.array(data[feature].tolist()), data[identifier])
        return 0

    def generate_index_from_ds(self, ds, feature: str, identifier: str):
        raise Exception("Belum di implementasi")
        return 0

    def build_model_local(self):
        """
        For sandbox
        :return: nnlm model
        """
        # this is for getting data in parent directory
        parentDirectory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        hub_layer = tf.keras.models.load_model(os.path.join(parentDirectory, 'resources', 'Model', 'nnlm_128_dim'))
        return hub_layer

    def build_model(self):
        "Return Hub nnlm-id-dim128 model"
        hub_layer = hub.KerasLayer("https://tfhub.dev/google/nnlm-id-dim128/2", output_shape=[50],
                                   input_shape=[], dtype=tf.string)
        return hub_layer

    def predict(self, text: str, k_value: int = 1, exception: list = None):
        """

        :param text: berupa string untuk query semantic terdekat
        :param k_value: jumlah rekomendasi yang akan di munculkan , akan terjadi error ketika data lebih sedikit
                        daripada k value (k value lebih besar dari jumlah data)
        :param exception: exception adalah list id room yang tidak akan termasuk dalam rekomendasi , exception berbentuk list
        :return: return array 1 dimensi ["result1","result2","..."]
        """

        #check apakah index data sudah di buat
        if(self.index is None):
            raise Exception("Index belum di inisialiasasi")
        if exception is None:
            _, recommendation = self.index(np.array([text]), k=k_value)
        else:
            _, recommendation = self.index.query_with_exclusions(np.array([text]), np.array([exception]), k=k_value)

        return recommendation




