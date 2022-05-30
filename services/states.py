from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import dp, bot
from aiogram import types
import buttons as btn
import services
import pickle
from handlers.admin import IsAdmin

""" User states """


class Change_answer(StatesGroup):
    last_msg = State()
    quest = State()
    answer = State()


# Нажатие на кнопку "Все окей"
@dp.callback_query_handler(lambda c: c.data == 'all_right',
                           state=Change_answer.last_msg)
async def change_quest(call, state: FSMContext):
    async with state.proxy() as data:
        last_msg = data['last_msg'].text

    answer = call.message.text.split('|')[0]
    await services.db.insert_qa_verif(last_msg, answer)
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text='Спасибо, я стал умнее',
                                reply_markup=btn.plug)


# Нажатие на кнопку "Ерунду сказал"
@dp.callback_query_handler(lambda c: c.data == 'change',
                           state=Change_answer.last_msg)
async def change_quest(call, state: FSMContext):
    async with state.proxy() as data:
        last_msg = data['last_msg'].text
    await state.update_data(quest=last_msg)

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text='Введите ответ на свой вопрос,'
                                     ' и я стану умнее!',
                                reply_markup=btn.plug)
    await Change_answer.next()
    await Change_answer.next()


# Ввод своего ответа на вопрос
@dp.message_handler(content_types=['text'],
                    state=Change_answer.answer)
async def insert_qa(message: types.Message,
                    state: FSMContext):
    await state.update_data(answer=message.text)
    async with state.proxy() as data:
        q = data['quest']
        a = data['answer']
    print(q, a)
    await services.db.insert_qa_verif(q, a)
    await message.answer('Спасибо, твой ответ попадёт в базу после модерации')
    await state.finish()


""" Admin states """


@dp.message_handler(IsAdmin(),
                    commands=['finish'],
                    state='*')
async def moderate(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Вы вышли из режима модерации')


class Moder_verif(StatesGroup):
    msg_id = State()
    q = State()
    a = State()


@dp.callback_query_handler(lambda c: c.data.startswith('moder'),
                           state=Moder_verif.msg_id)
async def change_quest(call):
    cmd = call.data.split('_')[1]
    message = call.message
    await services.moder.moderate(message, cmd)


@dp.message_handler(content_types=['text'], state=Moder_verif.msg_id)
async def change_answer(message: types.Message):
    await message.answer('Нажмите на предложенную кнопку, или введите /finish'
                         ' для выхода из режима модератора')


class Insert_faq(StatesGroup):
    quest = State()
    answer = State()


@dp.message_handler(content_types=['text'], state=Insert_faq.quest)
async def change_answer(message: types.Message, state: FSMContext):
    await state.update_data(quest=message.text)
    await message.answer('Теперь введите ответ на написанный вопрос')
    await Insert_faq.next()


@dp.message_handler(content_types=['text'], state=Insert_faq.answer)
async def change_answer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        q = data['quest']
    vec = pickle.dumps(await services.vectors.find_vector(q.lower()))
    await services.db.insert_question_faq(q, message.text, vec)
    await message.answer('Отлично, ваш вопрос занесён в базу')
    await state.finish()


class Delete_faq(StatesGroup):
    ident = State()
    check = State()
    msq_id = State()


@dp.message_handler(lambda msg: msg.text.isdigit(),
                    content_types=['text'],
                    state=Delete_faq.ident)
async def choose_faq(message: types.Message,
                     state: FSMContext):
    try:
        await state.update_data(ident=message.text)
        quest, answer = await services.db.select_faq_from_id(int(message.text))
        msg = await message.answer(f'Вы уверены что хотите удалить: '
                                   f'\nВопрос - {quest} '
                                   f'\nОтвет - {answer}',
                                   reply_markup=btn.del_q)
        await state.update_data(msq_id=msg.message_id)
        await Delete_faq.next()
    except TypeError:
        await message.answer('Некорректный id, проверьте есть ли он в списке')


@dp.message_handler(content_types=['text'], state=Delete_faq.ident)
async def delete_faq_text_input(message: types.Message):
    await message.answer('Необходимо ввести целое число - id вопроса \n'
                         'Что бы выйти из режима модерации введите /finish')


@dp.callback_query_handler(state=Delete_faq.check)
async def delete_or_cancel(call, state: FSMContext):
    cmd = call.data
    async with state.proxy() as data:
        quest_id = data['ident']
        msg_id = data['msq_id']
    if cmd == 'delete':
        await services.db.delete_faq_from_id(int(quest_id))
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=msg_id,
                                    text='Вопрос успешно удалён')
    elif cmd == 'cancel':
        await Delete_faq.previous()
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=msg_id,
                                    text='Выберите другой вопрос для удаления, '
                                         'или введите /finish для выхода из '
                                         'режима удаления')

