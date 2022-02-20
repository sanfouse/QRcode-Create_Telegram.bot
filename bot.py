import qrcode
from datetime import datetime

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


random_val = 'QRcode'


class setQRcodeState(StatesGroup):

  user_link = State()

@dp.message_handler(commands='start')
async def start(message: types.Message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
      types.KeyboardButton(text=random_val)
      )
  await message.answer(text=f'Привет, {message.from_user.full_name}\n\n', reply_markup=markup)

def qrcode_sets(link):
  qr = qrcode.make(str(link))
  qr.save('qrcode.png')

@dp.message_handler(lambda f: f.text == 'QRcode')
async def create_QRcode(message: types.message):

  markup = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text='Отмена', callback_data='cancel'))

  await message.answer('Введите ссылку...', reply_markup=markup)
  await setQRcodeState.user_link.set()

@dp.message_handler(state=setQRcodeState.user_link)
async def set_qrcode(message: types.message, state: FSMContext):
  async with state.proxy() as date:
    date['user_link'] = message.text
    user_link = date['user_link']


  try:
    qrcode_sets(user_link)
    photo = types.InputFile('qrcode.png')
    await bot.send_photo(chat_id=message.chat.id, photo=photo)

    await state.finish()
  except ValueError:
    await message.answer('Неверный ввод, пока пока...')

    await state.finish()

@dp.callback_query_handler(lambda m: m.data == 'cancel',state=setQRcodeState.user_link)
async def cancel_check_age(message: types.CallbackQuery, state: FSMContext):
  await message.message.delete()
  await message.answer('отменили')
  await state.finish()


if __name__ == '__main__':
  executor.start_polling(dp)
