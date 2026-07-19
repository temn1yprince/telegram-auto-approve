from aiogram import Bot, Dispatcher, F
from aiogram.types import ChatJoinRequest
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(TOKEN)
dp = Dispatcher()


@dp.chat_join_request()
async def approve_join(request: ChatJoinRequest):
    await bot.approve_chat_join_request(
        chat_id=request.chat.id,
        user_id=request.from_user.id
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
