import os
import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = os.getenv("ADMIN_ID", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-domain.com")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class ProductState(StatesGroup):
    waiting_for_photo_and_caption = State()

@dp.message(CommandStart())
async def start_cmd(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Каталог", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )
    await message.answer("У меня есть товар", reply_markup=keyboard)

@dp.message(Command("create_product"))
@dp.message(F.text == "Создать товар")
async def create_product_cmd(message: Message, state: FSMContext):
    if str(message.from_user.id) != str(ADMIN_ID):
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    await state.set_state(ProductState.waiting_for_photo_and_caption)
    await message.answer("Отправьте фото с названием товара в одном сообщении (caption).")

@dp.message(ProductState.waiting_for_photo_and_caption, F.photo)
async def process_photo_and_caption(message: Message, state: FSMContext):
    if not message.caption:
        await message.answer("Пожалуйста, отправьте фото с подписью (названием товара).")
        return

    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file_info.file_path)

    form_data = aiohttp.FormData()
    form_data.add_field('title', message.caption)
    form_data.add_field('file', file_bytes, filename=f"{photo.file_id}.jpg", content_type='image/jpeg')

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BACKEND_URL}/products", data=form_data) as resp:
            if resp.status == 200:
                await message.answer("Товар успешно добавлен!")
            else:
                await message.answer("Ошибка при сохранении товара на сервере.")
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
