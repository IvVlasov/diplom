from config import dp, spec_simbol
from aiogram import types
import services
from messages import adm, btn_text
import buttons as btn
from aiogram.dispatcher.filters import Filter


class IsAdmin(Filter):
    async def check(self, message: types.Message):
        return await services.db.find_status(message.chat.id) == 'admin'


async def create_answer():
    result = ''
    all_questons = await services.database.select_all_faq()
    for el in all_questons:
        result += f'id - {el[0]} \nВопрос - {el[1]} \nОтвет - {el[2]} \n\n'
    return result


class IsAdmin(Filter):
    async def check(self, message: types.Message):
        return await services.db.find_status(message.chat.id) == \
               'admin'


@dp.message_handler(IsAdmin(),
                    commands=['adm'],
                    state='*')
async def admin_panel(message: types.Message):
    await message.answer(adm['panel'], reply_markup=btn.adm_btn)



@dp.message_handler(lambda msg: msg.text.startswith(spec_simbol),
                    IsAdmin(),
                    content_types=['text'],
                    state='*')
async def admin_text_message(message: types.message):
    if message.text == btn_text['adm_btn1']:
        """Занесение вопрос-ответа в базу faq"""
        await services.states.Insert_faq.quest.set()
        await message.answer('Вы захотели добавить вопрос в FAQ таблицу, для этого введите вопрос, который необходимо занести. Следущим сообщением введите ответ на ваш вопрос. Если вы хотите отвенить ввод, введите /finish')

    elif message.text == btn_text['adm_btn2']:
        """Модерация ответов"""
        await message.answer(adm['moder'], reply_markup=types.ReplyKeyboardRemove())
        await message.answer(adm['moder2'])
        await services.moder.start_moderate(message)

    elif message.text == btn_text['adm_btn3']:
        """Удаление вопросoв Faq"""
        await services.states.Delete_faq.ident.set()
        await message.answer(adm['moder4'])
        answer = await create_answer()
        await message.answer(answer)







