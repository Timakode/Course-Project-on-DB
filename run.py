import asyncio
from create_bot import bot, dp
from handlers import router
#from handlers.admin_panel import router as admin_router
import db
from decouple import config

async def on_startup() -> None:
    await db.initialize_database()
    await bot.send_message(chat_id=config('ADMINS'), text='Бот запущен!') # Отправляется сообщение админу, что бот запущен

# Функция, которая будет вызвана при остановке бота
async def on_shutdown() -> None:
    # Отправляем сообщение администратору о том, что бот был остановлен
    await bot.send_message(chat_id=config('ADMINS'), text='Бот остановлен!')
    await bot.session.close()

async def main():
    dp.include_router(router)
    #dp.include_router(admin_router)

    # Регистрируем функцию, которая будет вызвана при старте бота
    dp.startup.register(on_startup)
    # Регистрируем функцию, которая будет вызвана при остановке бота
    dp.shutdown.register(on_shutdown)


    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())