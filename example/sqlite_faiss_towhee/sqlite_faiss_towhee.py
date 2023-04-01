import os
import time

from gptcache.view import openai
from gptcache.core import cache
from gptcache.cache.factory import get_si_data_manager
from gptcache.similarity_evaluation.simple import pair_evaluation
from gptcache.embedding import Towhee


def run():
    towhee = Towhee()
    # chinese model
    # towhee = Towhee(model="uer/albert-base-chinese-cluecorpussmall")

    sqlite_file = "sqlite.db"
    faiss_file = "faiss.index"
    has_data = os.path.isfile(sqlite_file) and os.path.isfile(faiss_file)
    data_manager = get_si_data_manager("sqlite", "faiss",
                                       dimension=towhee.dimension(), max_size=2000)
    cache.init(embedding_func=towhee.to_embeddings,
               data_manager=data_manager,
               evaluation_func=pair_evaluation,
               similarity_threshold=10000,
               similarity_positive=False)

    if not has_data:
        question = "what do you think about chatgpt"
        answer = "chatgpt is a good application"
        cache.data_manager.save(question, answer, cache.embedding_func(question))

    # distance 77
    mock_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "what do you feel like chatgpt"}
    ]

    # distance 21
    # mock_messages = [
    #     {"role": "system", "content": "You are a helpful assistant."},
    #     {"role": "user", "content": "what do you think chatgpt"}
    # ]

    start_time = time.time()
    answer = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=mock_messages,
    )
    end_time = time.time()
    print("cache hint time consuming: {:.2f}s".format(end_time - start_time))

    print(answer)


if __name__ == '__main__':
    run()
