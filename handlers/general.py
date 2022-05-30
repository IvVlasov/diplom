from config import dp
from aiogram import types
from messages import user as msg
import buttons as btn
import services
import handlers.admin


async def upper_text(stroke):
    ls_str = [el.strip().capitalize() for el in stroke.split('.')]
    return '. '.join(ls_str)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await services.db.insert_user(message.chat.id, 'member')
    await message.answer(msg['hello'])


@dp.message_handler(content_types=['text'], state='*')
async def echo(message: types.message):
    answer, cosine, qa_type = await services.vectors.create_answer(message.text)
    if qa_type == 'faq':
        await message.answer(f'{await upper_text(answer)}')
        return
    if cosine > 0.95:
        await message.answer(f'{await upper_text(answer)}')
        return
    elif cosine < 0.85:
        await message.answer(msg['no_answer'], reply_markup=btn.change_1)
    else:
        await message.answer(f'{await upper_text(answer)}',
                             reply_markup=btn.change_2)

    await services.states.Change_answer.last_msg.set()
    state = dp.get_current().current_state()
    await state.update_data(last_msg=message)
