from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton,\
    InlineKeyboardMarkup, KeyboardButton
from messages import btn_text as btn

""" Заглушка """
plug = InlineKeyboardMarkup()


""" Кнопки пользователей """
change_2 = InlineKeyboardMarkup(row_width=2, resize=True)
ch2_num_1 = InlineKeyboardButton(text=btn['button1'], callback_data='change')
ch2_num_2 = InlineKeyboardButton(text=btn['button2'], callback_data='all_right')
change_2.add(ch2_num_1, ch2_num_2)

change_1 = InlineKeyboardMarkup(row_width=2, resize=True)
ch2_num_2 = InlineKeyboardButton(text=btn['button3'], callback_data='change')
change_1.add(ch2_num_2)


""" Кнопки администратора"""
adm_btn = ReplyKeyboardMarkup(resize_keyboard=True)
adm_n1 = KeyboardButton(btn['adm_btn1'])
adm_n2 = KeyboardButton(btn['adm_btn2'])
adm_n3 = KeyboardButton(btn['adm_btn3'])
adm_btn.add(adm_n1).add(adm_n2).add(adm_n3)


del_q = InlineKeyboardMarkup(row_width=2, resize=True)
del_q_n1 = InlineKeyboardButton(text=btn['adm_btn5'], callback_data='delete')
del_q_n2 = InlineKeyboardButton(text=btn['adm_btn6'], callback_data='cancel')
del_q.add(del_q_n1, del_q_n2)


choose_verif = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
ch_v_n1 = InlineKeyboardButton(text=btn['adm_btn4'], callback_data='moder_put')
ch_v_n2 = InlineKeyboardButton(text=btn['adm_btn5'], callback_data='moder_delete')
choose_verif.add(ch_v_n1).add(ch_v_n2)