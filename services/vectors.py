import requests
import json
from numpy import linalg
import numpy as np
import services
import pickle
import random
from sklearn.neighbors import KDTree


async def find_vector(word: str):
    r = requests.get(f'https://api.ivanvlasov.ru/search?string={word}')
    b_new = json.loads(r.json()['result'])
    return np.array(b_new)


async def cosine(vector1: np.ndarray, vector2: np.ndarray):
    cos = np.dot(vector1, vector2) / (linalg.norm(vector1) * linalg.norm(vector2))
    return cos


async def search_close_vector(data: list, needVec: np.ndarray, count=5):
    vectors = np.array([pickle.loads(np.asarray([el[1]])) for el in data])
    kdtree = KDTree(vectors, leaf_size=30)
    dest, idn = kdtree.query([needVec], k=count)
    if 0 not in dest[0]:
        index = idn[0][0]
    else:
        s_elems = [1 if el < 0.2 else 0 for el in dest[0]]
        index = idn[0][random.randint(0, sum(s_elems) - 1)] if s_elems != [] else 0
    return index, vectors[index]


async def create_answer(question: str):
    quest_vector = await find_vector(question.lower())
    faq_data_vectors, all_data_vectors = \
        await services.db.select_all_vectors()

    all_index, all_vec = \
        await search_close_vector(all_data_vectors, quest_vector)
    faq_index, faq_vec = \
        await search_close_vector(faq_data_vectors, quest_vector, 2)

    all_cos_vectors = await cosine(all_vec, quest_vector)
    faq_cos_vectors = await cosine(faq_vec, quest_vector)

    if all_cos_vectors > faq_cos_vectors:
        answer = all_data_vectors[all_index][2]
        cos = all_cos_vectors
        qa_type = 'speak'

    else:
        answer = faq_data_vectors[faq_index][2]
        cos = faq_cos_vectors
        qa_type = 'faq'

    return answer, cos, qa_type
