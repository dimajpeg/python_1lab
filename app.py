from flask import Flask, render_template, request, redirect, url_for, session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Загружаем данные товаров (для примера)
products = [
    {"id": 1, "name": "Футбольный мяч Nike", "price": 100, "image": "american_football.jpg"},
    {"id": 2, "name": "Баскетбольный мяч NBA", "price": 150, "image": "basketball.jpg"},
    {"id": 3, "name": "Гантели 2 кг", "price": 50, "image": "dumbbells.jpg"},
    {"id": 4, "name": "Теннисные мячи", "price": 30, "image": "tennis_balls.jpg"}
]


# Главная страница
@app.route('/')
def index():
    return render_template('index.html', products=products)


# Страница с товарами
@app.route('/products')
def products_page():
    return render_template('products.html', products=products)


# Добавление товара в корзину
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity'))

    # Ищем товар по ID
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        # Если корзина не пуста, добавляем товар
        if 'cart' not in session:
            session['cart'] = []

        # Проверяем, есть ли уже этот товар в корзине
        existing_item = next((item for item in session['cart'] if item['product']['id'] == product_id), None)
        if existing_item:
            # Если товар уже в корзине, просто увеличиваем количество
            existing_item['quantity'] += quantity
        else:
            # Если товара нет в корзине, добавляем новый
            session['cart'].append({'product': product, 'quantity': quantity})

    return redirect(url_for('cart'))


# Страница корзины
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    cart_items = session.get('cart', [])
    total_price = sum([item['product']['price'] * item['quantity'] for item in cart_items])

    if request.method == 'POST':
        # Получаем данные пользователя из формы
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')

        # Печатаем данные заказа (можно дополнить отправкой email или сохранением в базу)
        print(f"Заказ оформлен! Имя: {first_name}, Фамилия: {last_name}, Почта: {email}")

        # Отправка email пользователю
        send_email("Ваш заказ",
                   f"Здравствуйте, {first_name} {last_name}. Ваш заказ успешно оформлен. Мы свяжемся с вами.", email)

        # Отправка email админу
        send_email("Новый заказ",
                   f"Новый заказ от {first_name} {last_name}. Почта: {email}. Содержимое корзины: {cart_items}",
                   "admin@example.com")

        # Перенаправление обратно на страницу корзины (сохранение товара)
        return redirect(url_for('cart'))

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


# Страница "О нас"
@app.route('/about')
def about():
    return render_template('about.html')


# Страница "Контакты"
@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


# Функция для отправки email (по необходимости)
def send_email(subject, body, to_email):
    from_email = "your_email@example.com"
    password = "your_password"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == '__main__':
    app.run(debug=True)
