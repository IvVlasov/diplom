from config import dp, bot
import buttons as btn
import pickle
import services
from messages import adm
from aiogram.types import Message


async def update_states_qa(quest: str, answer: str):
    state = dp.get_current().current_state()
    async with state.proxy() as data:
        quest_last = data['q']
        answer_last = data['a']
    await state.update_data(q=quest)
    await state.update_data(a=answer)
    return quest_last, answer_last


async def put_or_delete(cmd: str, q: str, a: str):
    """ Удаляем вопрос из qa_verif, либо переносим его в
    базу qa_speaks, находя его вектор"""
    q_lst, a_lst = await update_states_qa(q, a)
    if cmd == 'put':
        vector = pickle.dumps(await services.vectors.find_vector(q_lst.lower()))
        await services.db.insert_question(q_lst, a_lst, vector)
        text_out = f'Добавлено! Следущий:\nВ - {q}\nО - {a}'
    elif cmd == 'delete':
        text_out = f'Удалено! Следущий:\nВ - {q}\nО - {a}'

    return text_out


async def moderate(message: Message, cmd=''):
    """ Фунцкия модерации вопросов qa_verif"""
    ident, quest, answer = await services.db.select_last_q_verif(message.chat.id)
    answer = await put_or_delete(cmd, quest, answer)

    if ident == 'ENDED':
        await message.answer(adm['moder3'])
        return

    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message.message_id,
                                text='-',
                                reply_markup=btn.choose_verif)

    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message.message_id,
                                text=answer,
                                reply_markup=btn.choose_verif)


async def start_moderate(message: Message):
    """ Начало модерации вопросов qa_verif, далее вызывается функция moderate"""

    ident, q, a = await services.db.select_last_q_verif(message.chat.id)
    if ident == 'ENDED':
        await message.answer(adm['moder3'])
        return

    last_msg = await message.answer(f'В - {q}\nО - {a}',
                                    reply_markup=btn.choose_verif)
    await services.states.Moder_verif.msg_id.set()
    state = dp.get_current().current_state()
    await state.update_data(msg_id=last_msg.message_id)
    await state.update_data(q=q)
    await state.update_data(a=a)

