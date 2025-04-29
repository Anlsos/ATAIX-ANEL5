import json
import requests
import time

API_KEY = 'ваш_API_ключ'
API_SECRET = 'ваш_SECRET_ключ'
BASE_URL = 'https://api.ataix.com'

HEADERS = {
    'X-API-KEY': API_KEY,
    'Content-Type': 'application/json'
}

# Загрузка исходного файла с ордерами
with open("orders_lab5.json", "r") as f:
    orders = json.load(f)

new_orders = []

for order in orders:
    order_id = order["order_id"]
    status_url = f"{BASE_URL}/api/orders/{order_id}"

    # Получение статуса ордера
    response = requests.get(status_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Ошибка при получении ордера {order_id}")
        continue

    data = response.json()
    status = data.get("status", "")
    price = float(data.get("price", order["price"]))  # цена из API или из файла

    if status.lower() == "filled":
        order["status"] = "filled"
        print(f"Ордера {order_id} выполнен.")
        new_orders.append(order)
    else:
        # Удаляем старый ордер
        cancel_url = f"{BASE_URL}/api/orders/{order_id}"
        cancel_response = requests.delete(cancel_url, headers=HEADERS)
        if cancel_response.status_code == 200:
            print(f"Ордера {order_id} удалён.")
            order["status"] = "cancelled"
        else:
            print(f"Не удалось удалить ордер {order_id}")
            continue

        # Создаём новый ордер по цене на 1% выше
        new_price = round(price * 1.01, 6)
        payload = {
            "symbol": "BTC_USDT",  # замените на свою торговую пару
            "side": "buy",
            "type": "limit",
            "price": str(new_price),
            "quantity": "1"
        }

        new_order_response = requests.post(f"{BASE_URL}/api/orders", headers=HEADERS, json=payload)

        if new_order_response.status_code == 200:
            new_order_data = new_order_response.json()
            new_order_id = new_order_data.get("orderId")
            print(f"Создан новый ордер: {new_order_id} по цене {new_price}")

            # Сохраняем оба ордера: отменённый и новый
            new_orders.append(order)
            new_orders.append({
                "order_id": new_order_id,
                "status": "NEW",
                "price": new_price
            })
        else:
            print(f"Ошибка при создании нового ордера на {new_price}")

    time.sleep(1)  # пауза, чтобы избежать ограничения по запросам

# Сохраняем обновлённые данные в новый JSON
with open("orders_updated.json", "w") as f:
    json.dump(new_orders, f, indent=4)

print("Обработка завершена. Результаты сохранены в orders_updated.json.")
