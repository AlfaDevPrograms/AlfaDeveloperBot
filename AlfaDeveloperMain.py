import telebot
from telebot import types

from User import User

bot = telebot.TeleBot("7568756895:AAEqpyqUH0e9q26VD401ZELgZqMeCZuL_hM")

users = list()


# Начальная команда
@bot.message_handler(commands = ["start"])
def start_bot(message):
	markup = types.InlineKeyboardMarkup()
	button_register = types.InlineKeyboardButton(text = "Регистрация", callback_data = "register")
	markup.add(button_register)
	bot.send_message(message.chat.id, "Привет! 👋 Я бот для знакомств. Давай познакомимся! 🤗", reply_markup = markup)


# Регистрация пользователя
@bot.callback_query_handler(func = lambda call: call.data == "register")
def register_user(call):
	# Удаление старого сообщения и кнопки
	bot.delete_message(call.message.chat.id, call.message.message_id)
	user_id = call.from_user.id
	if_exist = [user for user in users if user.id_user == int(user_id)]
	if if_exist:
		markup = types.InlineKeyboardMarkup()
		button_match = types.InlineKeyboardButton(text = "Найти партнёра", callback_data = "match")
		markup.add(button_match)
		bot.send_message(call.message.chat.id,
		                 "Вы уже зарегистрированы! Используйте кнопку ниже, чтобы найти совпадения.",
		                 reply_markup = markup)
		return
	else:
		users.append(User(id_user = int(user_id)))
	bot.send_message(call.message.chat.id, "Отлично! Давай соберем немного информации о тебе. Как тебя зовут?", )
	bot.register_next_step_handler(call.message, process_name)


def process_name(message):
	user_id = message.from_user.id
	name = message.text
	if_exist = [user for user in users if user.id_user == int(user_id)][0]
	id_in_list = users.index(if_exist)
	users[id_in_list] = User(int(user_id), name, message.from_user.username)
	bot.send_message(message.chat.id, "Сколько тебе лет?")
	bot.register_next_step_handler(message, process_age)


def process_age(message):
	user_id = message.from_user.id
	age = message.text
	if_exist = [user for user in users if user.id_user == int(user_id)][0]
	id_in_list = users.index(if_exist)
	try:
		users[id_in_list].age = int(age)
		bot.send_message(message.chat.id, "Каковы ваши интересы? (например, спорт, музыка, путешествия)\n"
		                                  "перечислите через запятую.")
		bot.register_next_step_handler(message, process_interests)
	except ValueError:
		bot.send_message(message.chat.id, "Пожалуйста, введите корректный возраст (целое число). Попробуйте снова.")
		bot.register_next_step_handler(message, process_age)  # Повторный вызов функции


def process_interests(message):
	user_id = message.from_user.id
	interests = message.text
	if_exist = [user for user in users if user.id_user == int(user_id)][0]
	id_in_list = users.index(if_exist)
	interests_list = str(interests).split(',')
	interests_list = [s.strip().lower() for s in interests_list]
	users[id_in_list].interest = interests_list
	interests_view = ""
	for item in interests_list:
		interests_view += item + ", "
	interests_view = interests_view[:-2] + '.'
	registration_message = (f"Вы зарегистрированы! 🎉\n"
	                        f"Имя: {users[id_in_list].name}\n"
	                        f"Возраст: {users[id_in_list].age}\n"
	                        f"Интересы: {interests_view}\n")
	markup = types.InlineKeyboardMarkup()
	button_match = types.InlineKeyboardButton(text = "Найти партнёра", callback_data = "match")
	markup.add(button_match)
	bot.send_message(message.chat.id, registration_message, reply_markup = markup)


# Нахождение совпадений
@bot.callback_query_handler(func = lambda call: call.data == "match")
def find_matches(call):
	user_id = call.from_user.id
	if len(users) == 0:
		return
	if_exist = [user for user in users if user.id_user == int(user_id)][0]
	id_in_list = users.index(if_exist)
	user = users[id_in_list]
	if not user:
		bot.send_message(call.message.chat.id, "Вы не зарегистрированы! Пожалуйста, зарегистрируйтесь.", )
		return
	match_info = ""
	set1 = set(user.interest)
	# Преобразуем массивы в множества
	if user.count >= len(users) or (user.count == users.index(user) and users.index(user) == len(users) - 1):
		user.count = 0
	for i in range(user.count, len(users)):
		user.count = i + 1
		if user != users[i]:
			set2 = set(users[i].interest)
			common_elements = set1.intersection(set2)
			count = len(common_elements)
			if count > 0:
				interests_view = ""
				for item in users[i].interest:
					interests_view += item + ", "
				interests_view = interests_view[:-2] + '.'
				match_info = (f"Имя: {users[i].name}\nВозраст: {users[i].age}\n"
				              f"Интересы: {interests_view}\nСсылка на профиль: @{users[i].username}")
				break
	markup = types.InlineKeyboardMarkup()
	button_match = types.InlineKeyboardButton(text = "Искать", callback_data = "match")
	markup.add(button_match)
	if match_info != "":
		bot.send_message(call.message.chat.id, f"Вот ваши совпадения: \n{match_info}", reply_markup = markup)
	else:
		bot.send_message(call.message.chat.id, "К сожалению, совпадений не найдено. Попробуйте позже! 🙂",
		                 reply_markup = markup)
	bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = None)


bot.infinity_polling()
