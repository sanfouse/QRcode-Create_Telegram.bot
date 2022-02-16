import math
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


age = 'Возраст'
random_val = 'QRcode'

class CheckAgeState(StatesGroup):

  user_age = State()

class setQRcodeState(StatesGroup):

  user_link = State()

@dp.message_handler(commands='start')
async def start(message: types.Message):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
      types.KeyboardButton(text=age),
      types.KeyboardButton(text=random_val)
      )
  await message.answer(text=f'Привет, {message.from_user.full_name}\n\n', reply_markup=markup)

def check_year(year: str) -> int:

  now = datetime.strftime(datetime.now(), "%d.%m.%Y")
  delta_year = datetime.strptime(now, "%d.%m.%Y") -     datetime.strptime(year, "%d.%m.%Y")

  age = int(delta_year.days) / 365

  return math.floor(age)

def qrcode_sets(link):
  qr = qrcode.make(str(link))
  qr.save('qrcode.png')

@dp.message_handler(lambda m: m.text == age)
async def check_age(message: types.Message):

  markup = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text='Отмена', callback_data='cancel'))

  await message.answer('Введите свой возраст...', reply_markup=markup)
  await CheckAgeState.user_age.set()

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


@dp.message_handler(state=CheckAgeState.user_age)
async def set_check_age(message: types.Message, state: FSMContext):

  async with state.proxy() as data:
    data['user_age'] = message.text
    user_age = data['user_age']

  try:
    # sticker = types.InputFile('vendor/sticker.webp')
    # audio=types.InputFile('vendor/auidio.mp3')
    if check_year(user_age) >= 18:
      await message.answer('пиво можно!')
      # await message.answer_sticker(sticker=sticker)
      # await message.answer_audio(audio=audio, caption='Лови мудло')

      await state.finish()
    else:
      # await message.answer_sticker(sticker=types.InputFile('vendor/second.webp'))
      await message.answer('К сожалению, идите вы!')

      await state.finish()
  except ValueError:
    # await message.answer_sticker(sticker=types.InputFile('vendor/second.webp'))
    await message.answer('Неверный ввод, пока пока...')

    await state.finish()


@dp.callback_query_handler(lambda m: m.data == 'cancel',state=CheckAgeState.user_age)
async def cancel_check_age(message: types.CallbackQuery, state: FSMContext):
  await message.message.delete()
  await message.answer('отменили')
  await state.finish()
  
@dp.callback_query_handler(lambda m: m.data == 'cancel',state=setQRcodeState.user_link)
async def cancel_check_age(message: types.CallbackQuery, state: FSMContext):
  await message.message.delete()
  await message.answer('отменили')
  await state.finish()


if __name__ == '__main__':
  executor.start_polling(dp)
