from threading import Lock, Thread
import pandas as pd
import generate_saved_model
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
    model = generate_saved_model.build_model_local()
    bruteForce = None
    index_data = None
    """
    We'll use this property to prove that our Singleton really works.
    """

    def __init__(self) -> None:
        try:
            # ScaNN is an optional dependency, and might not be present.
            from scann import scann_ops
            _HAVE_SCANN = True
            self.bruteForce = tfrs.layers.factorized_top_k.ScaNN(self.model)
        except ImportError:
            _HAVE_SCANN = False
            self.bruteForce = tfrs.layers.factorized_top_k.BruteForce(self.model)

    def generate_index(data: pd.DataFrame):
        return 0

    def update_index(self, new_data):
        return

    def predict(self, text: str, k_value: int = 1, exception: list = None):
        """

        :param text: berupa string untuk query semantic terdekat
        :param k_value: jumlah rekomendasi yang akan di munculkan , akan terjadi error ketika data lebih sedikit
                        daripada k value (k value lebih besar dari jumlah data)
        :param exception: exception adalah list id room yang tidak akan termasuk dalam rekomendasi , exception berbentuk list
        :return: return array dua dimensi [["result1","result2","..."]]
        """

        #check apakah index data sudah di buat
        if(self.index_data == None):
            raise Exception("Index belum di inisialiasasi")

        if exception == None:
            _, recommendation = self.bruteForce.query_with_exclusions(np.array([text]),np.array([exception]) ,k=k_value)
        else:
            _, recommendation = self.bruteForce(np.array([text]), k=k_value)

        return recommendation




