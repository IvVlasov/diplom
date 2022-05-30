import asyncpg
import config

async def records_to_tuple(results: asyncpg.Record):
    return [tuple(el) for el in results]


async def create_connection():
    connection = await asyncpg.connect(user=config.user,
                                       database=config.database,
                                       host=config.host,
                                       port=config.port,
                                       password=config.password)
    return connection


"""Блок работы с таблицей qa_speak и qa_faq"""


async def select_all_vectors():
    conn = await create_connection()
    faq_res = await conn.fetch("SELECT id, vector, answer FROM qa_faq")
    speak_res = await conn.fetch("SELECT id, vector, answer FROM qa_speak")
    await conn.close()
    return await records_to_tuple(faq_res), await records_to_tuple(speak_res)


async def select_all_faq():
    conn = await create_connection()
    res = await conn.fetch("SELECT id, quest, answer FROM qa_faq")
    await conn.close()
    return await records_to_tuple(res)


async def select_faq_from_id(ident: int):
    conn = await create_connection()
    res = await conn.fetchrow("SELECT quest, answer FROM qa_faq WHERE id=$1", ident)
    await conn.close()
    return res


async def delete_faq_from_id(ident: int):
    conn = await create_connection()
    res = await conn.fetchrow("DELETE FROM qa_faq WHERE id=$1", ident)
    await conn.close()
    return res


async def insert_question_faq(quest: str, answer: str, vector: bytes):
    conn = await create_connection()
    res = await conn.fetch("INSERT INTO qa_faq (quest, answer, vector)"
                           "VALUES ($1, $2, $3)", quest, answer, vector)
    await conn.close()
    return await records_to_tuple(res)


async def insert_question(quest: str, answer: str, vector: bytes):
    conn = await create_connection()
    res = await conn.fetch("INSERT INTO qa_speak (quest, answer, vector)"
                           " VALUES ($1, $2, $3)", quest, answer, vector)
    await conn.close()
    return await records_to_tuple(res)


"""Блок работы с таблицей qa_verif"""


async def insert_qa_verif(quest: str, answer: str):
    conn = await create_connection()
    await conn.fetch("INSERT INTO qa_verif (quest, answer)"
                     "VALUES ($1, $2)", quest, answer)
    await conn.close()


async def select_last_q_verif(new_id: int):
    conn = await create_connection()
    await conn.fetch("DELETE FROM qa_verif WHERE id=$1", new_id)
    res = await conn.fetchrow(
        "SELECT id, quest, answer  FROM qa_verif "
        "WHERE id= (SELECT min(id) FROM qa_verif)")
    if res is None:
        return 'ENDED', '', ''
    await conn.fetch("UPDATE qa_verif SET id = $1 WHERE id = $2", new_id,
                     res['id'])
    await conn.close()
    return res['id'], res['quest'], res['answer']


"""Блок работы с таблицей users"""


async def find_user(chat_id: int):
    conn = await create_connection()
    res = await conn.fetchrow("SELECT chat_id FROM users WHERE chat_id=$1",
                              chat_id)
    await conn.close()
    return res


async def insert_user(chat_id: int, status: str):
    conn = await create_connection()
    if await find_user(chat_id) is None:
        await conn.fetch("INSERT INTO users (chat_id, status) "
                         "VALUES ($1, $2)", chat_id, status)
        await conn.close()


async def find_status(chat_id: int):
    conn = await create_connection()
    res = await conn.fetchrow("SELECT status FROM users WHERE chat_id=$1",
                              chat_id)
    await conn.close()
    return res['status']
