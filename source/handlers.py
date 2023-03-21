import os
from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputFile
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from source.bot_init import bot


def register_handlers(dp: Dispatcher):
	dp.register_callback_query_handler(upload_ticket, Text('upload'), state='*')
	dp.register_callback_query_handler(get_subject, state=Bilet.subject)
	dp.register_callback_query_handler(get_teacher, state=Bilet.teacher)
	dp.register_callback_query_handler(show_tickets, Text('view'))

	dp.register_message_handler(welcome, commands='start', state='*')
	dp.register_message_handler(get_bilet_number, state=Bilet.number)
	dp.register_message_handler(get_photo_content, content_types='photo', state=Bilet.content)
	dp.register_message_handler(get_text_content, content_types='text', state=Bilet.content)
	dp.register_message_handler(welcome)


class Bilet(StatesGroup):
	subject = State()
	number = State()
	teacher = State()
	content = State()


def create_subject_menu(with_setting=False) -> InlineKeyboardMarkup:
	menu = InlineKeyboardMarkup(row_width=1)
	if not with_setting:
		menu.add(
			InlineKeyboardButton('Алгебра', callback_data='sb_algebra'),
			InlineKeyboardButton('Геометрия', callback_data='sb_geometry'),
			InlineKeyboardButton('Матанализ', callback_data='sb_analyse')
		)
		return menu
	is_empty_algebra = (len(os.listdir("source/Algebra")) == 0)
	is_empty_geometry = (len(os.listdir("source/Geometry")) == 0)
	is_empty_analyse = (len(os.listdir("source/Analyse")) == 0)
	menu.add(
		InlineKeyboardButton(f'Алгебра (Пусто)' if is_empty_algebra else 'Алгебра', callback_data='sb_algebra'),
		InlineKeyboardButton(f'Геометрия (Пусто)' if is_empty_geometry else 'Геометрия', callback_data='sb_geometry'),
		InlineKeyboardButton(f'Матанализ (Пусто)' if is_empty_analyse else 'Матанализ', callback_data='sb_analyse')
	)
	return menu


def create_teacher_menu_by_subject(subject: str) -> InlineKeyboardMarkup:
	menu = InlineKeyboardMarkup(row_width=1)
	if subject == 'algebra':
		menu.add(
			InlineKeyboardButton('Екимов (1 поток)', callback_data='ekimov'),
			InlineKeyboardButton('Курбатова (2 поток)', callback_data='kurbatova'),
			InlineKeyboardButton('Михеев (3 поток)', callback_data='miheev')
		)
	elif subject == 'analyse':
		menu.add(
			InlineKeyboardButton("Александров (1 поток)", callback_data='alex'),
			InlineKeyboardButton('Шмыров (2 поток)', callback_data='shmirov'),
			InlineKeyboardButton('Камачкин (3 поток)', callback_data='kamachkin')

		)
	elif subject == 'geometry':
		menu.add(
			InlineKeyboardButton('Полякова (1 поток)', callback_data='polykova'),
			InlineKeyboardButton('Коровкин (2 поток)', callback_data='korovkin'),
			InlineKeyboardButton('Ведякова(Сотникова) (3 поток)', callback_data='vedykova')
		)
	return menu


def create_main_menu() -> InlineKeyboardMarkup:
	menu = InlineKeyboardMarkup(row_width=1)
	menu.add(
		InlineKeyboardButton('Посмотреть загруженные билеты', callback_data='view'),
		InlineKeyboardButton('Загрузить билет', callback_data='upload')
	)
	return menu


async def welcome(msg: Message, state: FSMContext):
	await state.reset_state()
	await msg.answer(
		'Привет! Я могу показать тебе загруженные билеты студентов 1 курса ПМ-ПУ или ты можешь сам загрузить свои билеты.',
		reply_markup=create_main_menu())


async def show_tickets(call: CallbackQuery, state: FSMContext):
	await call.message.answer('Выбери интересующий предмет', reply_markup=create_subject_menu(with_setting=True))
	await state.set_data({'to_send': False})
	await Bilet.subject.set()


async def upload_ticket(call: CallbackQuery, state: FSMContext):
	await call.message.edit_text(text='Выбери предмет и введи номер билета по предмету, '
	                                  'затем отправь текст или фотографию, которая относится к этому билету.',
	                             reply_markup=create_subject_menu())
	await state.set_data({'to_send': True})
	await Bilet.subject.set()


async def get_subject(call: CallbackQuery, state=FSMContext):
	data = await state.get_data()

	subject = call.data.split('_')[1]
	data['subject'] = subject
	await state.set_data(data)
	await call.message.edit_text('Предмет выбран. Выбери преподавателя.',
	                             reply_markup=create_teacher_menu_by_subject(subject))

	await Bilet.teacher.set()


async def get_teacher(call: CallbackQuery, state=FSMContext):
	data = await state.get_data()
	teacher = call.data
	data['teacher'] = teacher
	await call.message.edit_text('Преподаватель выбран. Введи номер билета')
	await state.set_data(data)
	await Bilet.number.set()


async def get_bilet_number(msg: Message, state=FSMContext):
	msg_text = msg.text
	if not msg_text.isnumeric():
		await msg.answer('Номер билета должен быть числом.')
		await state.reset_state()
		await msg.answer('Выбери предмет и введи номер билета по предмету, '
		                 'затем отправь текст или картинку, которая относится к этому билету.',
		                 reply_markup=create_subject_menu())
		return
	number = int(msg_text)
	if number < 0 or number > 100:
		await msg.answer('Введи номер билета в диапазоне от 1 до 99')
		await state.reset_state()
		await msg.answer('Выбери предмет и введи номер билета по предмету, '
		                 'затем отправь текст или картинку, которая относится к этому билету.',
		                 reply_markup=create_subject_menu())
		return

	data = await state.get_data()
	data['number'] = number
	subject = data['subject']
	teacher = data['teacher']
	if data.get('to_send', True):
		await msg.answer('Номер билета получен. '
		                 'Теперь отправь фрагмент текста по билету или картинку. В одном экземляре на каждый тип.'
		                 'Если закончил, введи /stop')
		await Bilet.content.set()
		await state.set_data(data)
		return
	if len(os.listdir("source/" + data['subject'].title())) == 0:
		await msg.answer('По этому предмету ничего нет =(\nПопробуй другой.',
		                 reply_markup=create_subject_menu(with_setting=True))
		await Bilet.subject.set()
		return
	path = os.path.join(subject.title())
	for teachers in os.listdir("source/" + path):
		if teachers == teacher.title():
			founded_file = teachers
			break
	else:
		await msg.answer('Еще не существует файлов этого преподавателя =( Попробуй другое.',
		                 reply_markup=create_subject_menu(with_setting=True))
		await Bilet.subject.set()
		return
	sended = False
	path = os.path.join(path, founded_file)
	for file in os.listdir("source/" + path):
		if file.startswith(str(number)):
			print(file)
			if file.endswith('.jpg'):
				photo = InputFile(os.path.join("source/" + path, file))
				await bot.send_photo(photo=photo, chat_id=msg.chat.id,
				                     caption=f'{subject.title()}, {teacher.title()}, Билет №{number}.')
				await state.reset_state()
				sended = True
			else:
				with open(os.path.join("source/" + path, file), 'r', encoding='utf-8') as txt:
					file_text = txt.read()
				if not sended:
					await msg.answer(f'{subject.title()}, {teacher.title()}, Билет №{number}.')
				await msg.answer(file_text)
				await state.reset_state()
				sended = True

	else:
		if not sended:
			await msg.answer('К сожалению, еще нет данных по этому билету =( Попробуй другой.',
			                 reply_markup=create_subject_menu(with_setting=True))
			await Bilet.subject.set()
			return


async def get_photo_content(msg: Message, state: FSMContext):
	data = await state.get_data()
	subject, teacher, number = data['subject'], data['teacher'], data['number']
	path = "source/" + subject.title() + "/" + teacher.title()
	if not os.path.exists(path):
		os.mkdir(path)
	await msg.photo[-1].download(
		destination_file=os.path.join(path, f"{number}.jpg"))
	await msg.answer('Фото принято')
	await Bilet.content.set()


async def get_text_content(msg: Message, state: FSMContext):
	if msg.text == '/stop':
		await msg.answer('Отправка завершена.')
		await state.reset_state()
		return
	data = await state.get_data()
	subject, teacher, number = data['subject'], data['teacher'], data['number']
	path = "source/" + subject.title() + "/" + teacher.title()
	if not os.path.exists(path):
		os.mkdir(path)
	with open(os.path.join(path, f'{number}.txt'), 'w', encoding='utf-8') as file:
		file.write(msg.text)
	await msg.answer('Текст принят.')
	await Bilet.content.set()


async def stop_sending(msg: Message, state: FSMContext):
	await state.reset_state()
	await msg.answer('Отправка завершена.')
