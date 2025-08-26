from abc import ABC, abstractmethod
import re
from datetime import datetime

try:
    from tkinter import messagebox
except ImportError:
    # Заглушка для messagebox при отсутствии tkinter (для тестирования)
    class MockMessagebox:
        def showerror(self, title, message):
            print(f"ERROR: {title} - {message}")
    
    messagebox = MockMessagebox()
    

class BaseModel(ABC):
    """
    Базовый абстрактный класс для всех моделей данных.
    
    Предоставляет общую функциональность для работы с CSV файлами:
    загрузка, сохранение, добавление, удаление и поиск элементов.
    
    Attributes
    ----------
    filename : str
        Имя CSV файла для хранения данных
    fieldnames : list of str
        Заголовки столбцов CSV файла
    data : list of dict
        Список словарей для хранения данных в памяти
    selected_product_in_table : any
        Переменная для отслеживания выбранного товара в UI таблице
    selected_customer_in_table : any
        Переменная для отслеживания выбранного клиента в UI таблице
    """
    
    def __init__(self, filename, fieldnames):
        """
        Инициализация базовой модели.
        
        Parameters
        ----------
        filename : str
            Имя CSV файла для хранения данных
        fieldnames : list of str
            Список названий колонок CSV файла
        """
        self.filename = filename
        self.fieldnames = fieldnames
        self.data = []
        self.selected_product_in_table = None
        self.selected_customer_in_table = None

    @abstractmethod
    def validate(self, item):
        """
        Абстрактный метод для валидации данных элемента.
        
        Parameters
        ----------
        item : dict
            Словарь с данными элемента для валидации
            
        Returns
        -------
        bool
            True если данные валидны, False в противном случае
            
        Notes
        -----
        Должен быть реализован в дочерних классах.
        """
        pass
    
    def load_data(self):
        """
        Загрузка данных из CSV файла с поддержкой разных кодировок.
        
        Returns
        -------
        list of dict
            Загруженные данные в виде списка словарей
            
        Notes
        -----
        Автоматически определяет кодировку файла (UTF-8 или Windows-1251).
        Если файл не существует, возвращает пустой список.
        """
        self.data = []
        try:
            import os
            import csv
            if os.path.exists(self.filename):
                try:
                    with open(self.filename, 'r', encoding='utf-8') as file:
                        reader = csv.DictReader(file)
                        for row in reader:
                            self.data.append(row)
                except UnicodeDecodeError:
                    with open(self.filename, 'r', encoding='cp1251') as file:
                        reader = csv.DictReader(file)
                        for row in reader:
                            self.data.append(row)
        except Exception as e:
            print(f"Ошибка при загрузке {self.filename}: {e}")
        return self.data
    
    def save_data(self):
        """
        Сохранение данных в CSV файл в кодировке UTF-8.
        
        Returns
        -------
        bool
            True если сохранение успешно, False при ошибке
        """
        try:
            import csv
            with open(self.filename, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerows(self.data)
            return True
        except Exception as e:
            print(f"Ошибка при сохранении {self.filename}: {e}")
            return False
    
    def get_next_id(self):
        """
        Генерация следующего уникального идентификатора.
        
        Returns
        -------
        str
            Следующий доступный ID в виде строки
        """
        if not self.data:
            return "1"
        max_id = max(int(item['id']) for item in self.data)
        return str(max_id + 1)
    
    def add_item(self, item):
        """
        Добавление нового элемента с автоматической генерацией ID.
        
        Parameters
        ----------
        item : dict
            Словарь с данными элемента для добавления
            
        Returns
        -------
        bool
            True если элемент успешно добавлен и сохранен, False при ошибке
        """
        if self.validate(item):
            item['id'] = self.get_next_id()
            self.data.append(item)
            return self.save_data()
        return False
    
    def get_all(self):
        """
        Получение всех элементов модели.
        
        Returns
        -------
        list of dict
            Все данные модели в виде списка словарей
        """
        return self.data
    
    def find_by_id(self, item_id):
        """
        Поиск элемента по ID.
        
        Parameters
        ----------
        item_id : str or int
            Идентификатор элемента для поиска
            
        Returns
        -------
        dict or None
            Найденный элемент или None если не найден
        """
        for item in self.data:
            if item['id'] == str(item_id):
                return item
        return None
    
    def delete_item(self, item_id):
        """
        Удаление элемента по ID.
        
        Parameters
        ----------
        item_id : str or int
            Идентификатор элемента для удаления
            
        Returns
        -------
        bool
            True если элемент успешно удален и сохранен, False при ошибке
        """
        item_to_delete = None
        for item in self.data:
            if item['id'] == str(item_id):
                item_to_delete = item
                break
        
        if item_to_delete:
            self.data.remove(item_to_delete)
            return self.save_data()
        return False


class CustomerModel(BaseModel):
    """
    Модель для работы с данными покупателей.
    
    Наследует от BaseModel и добавляет специфичную для покупателей
    валидацию и функциональность поиска.
    """
    
    def __init__(self):
        """
        Инициализация модели покупателей.
        
        Notes
        -----
        Автоматически загружает данные из файла 'customers.csv'
        """
        super().__init__('customers.csv', 
                        ['id', 'last_name', 'first_name', 'middle_name', 'phone', 'email'])
        self.load_data()
    
    def validate_phone(self, phone):
        """
        Валидация номера телефона с помощью регулярного выражения.
        
        Parameters
        ----------
        phone : str
            Номер телефона для валидации
            
        Returns
        -------
        bool
            True если номер телефона соответствует формату, False в противном случае
            
        Notes
        -----
        Поддерживает форматы: +7(999)123-45-67, 89991234567, +7 999 123 45 67
        """
        phone_pattern = r'^(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'
        return re.match(phone_pattern, phone) is not None
    
    def validate_email(self, email):
        """
        Валидация email адреса с помощью регулярного выражения.
        
        Parameters
        ----------
        email : str
            Email адрес для валидации
            
        Returns
        -------
        bool
            True если email соответствует формату, False в противном случае
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    def validate(self, customer):
        """
        Валидация данных покупателя.
        
        Parameters
        ----------
        customer : dict
            Словарь с данными покупателя
            
        Returns
        -------
        bool
            True если данные валидны, False в противном случае
            
        Raises
        ------
        Shows messagebox with validation errors
        """
        errors = []
        
        if not customer.get('last_name', '').strip():
            errors.append("Фамилия обязательна для заполнения")
        if not customer.get('first_name', '').strip():
            errors.append("Имя обязательно для заполнения")
        
        phone = customer.get('phone', '').strip()
        if not phone:
            errors.append("Телефон обязателен для заполнения")
        elif not self.validate_phone(phone):
            errors.append("Некорректный формат телефона. Пример: +7(999)123-45-67 или 89991234567")
        
        email = customer.get('email', '').strip()
        if email and not self.validate_email(email):
            errors.append("Некорректный формат email. Пример: example@mail.ru")
        
        if errors:
            messagebox.showerror("Ошибка валидации", "\n".join(errors))
            return False
        return True
    
    def search(self, search_text):
        """
        Поиск покупателей по всем текстовым полям.
        
        Parameters
        ----------
        search_text : str
            Текст для поиска (регистронезависимый)
            
        Returns
        -------
        list of dict
            Список найденных покупателей, соответствующих критерию поиска
            
        Notes
        -----
        Ищет по всем текстовым полям: фамилия, имя, отчество, телефон, email
        """
        search_text = search_text.lower().strip()
        if not search_text:
            return self.data.copy()
        
        return [
            customer for customer in self.data
            if (search_text in customer['last_name'].lower() or
                search_text in customer['first_name'].lower() or
                search_text in customer['middle_name'].lower() or
                search_text in customer['phone'].lower() or
                search_text in customer['email'].lower())
        ]


class ProductModel(BaseModel):
    """
    Модель для работы с данными товаров.
    
    Наследует от BaseModel и добавляет специфичную для товаров
    валидацию и функциональность поиска.
    """
    
    def __init__(self):
        """
        Инициализация модели товаров.
        
        Notes
        -----
        Автоматически загружает данные из файла 'products.csv'
        """
        super().__init__('products.csv', ['id', 'name', 'price', 'unit'])
        self.load_data()
    
    def validate(self, product):
        """
        Валидация данных товара.
        
        Parameters
        ----------
        product : dict
            Словарь с данными товара
            
        Returns
        -------
        bool
            True если данные валидны, False в противном случае
            
        Raises
        ------
        Shows messagebox with validation errors
        """
        errors = []
        if not product.get('name', '').strip():
            errors.append("Название товара обязательно для заполнения")
        if not product.get('unit', '').strip():
            errors.append("Единица измерения обязательна для заполнения")
        
        try:
            price = float(product.get('price', 0))
            if price <= 0:
                errors.append("Цена должна быть больше 0")
        except ValueError:
            errors.append("Цена должна быть числом")
        
        if errors:
            messagebox.showerror("Ошибка валидации", "\n".join(errors))
            return False
        return True
    
    def search(self, search_text):
        """
        Поиск товаров по названию и единицам измерения.
        
        Parameters
        ----------
        search_text : str
            Текст для поиска (регистронезависимый)
            
        Returns
        -------
        list of dict
            Список найденных товаров, соответствующих критерию поиска
        """
        search_text = search_text.lower().strip()
        if not search_text:
            return self.data.copy()
        
        return [
            product for product in self.data
            if (search_text in product['name'].lower() or
                search_text in product['unit'].lower())
        ]


class OrderModel(BaseModel):
    """
    Модель для работы с заказами.
    
    Наследует от BaseModel и добавляет функциональность для работы
    с товарами заказов и сортировкой.
    """
    
    def __init__(self):
        """
        Инициализация модели заказов.
        
        Notes
        -----
        Автоматически загружает данные из файла 'orders.csv'
        и инициализирует модель товаров заказов.
        """
        super().__init__('orders.csv', 
                        ['id', 'customer_id', 'total_amount', 'order_date', 'customer_info'])
        self.order_items_model = OrderItemsModel()
        self.load_data()
    
    def validate(self, order):
        """
        Валидация данных заказа.
        
        Parameters
        ----------
        order : dict
            Словарь с данными заказа
            
        Returns
        -------
        bool
            True если данные валидны, False в противном случае
            
        Raises
        ------
        Shows messagebox with validation errors
        """
        if not order.get('customer_id'):
            messagebox.showerror("Ошибка", "Не указан покупатель")
            return False
        if float(order.get('total_amount', 0)) <= 0:
            messagebox.showerror("Ошибка", "Сумма заказа должна быть больше 0")
            return False
        return True
    
    def create_order(self, customer_id, total_amount, customer_info, order_items):
        """
        Создание нового заказа с привязкой товаров.
        
        Parameters
        ----------
        customer_id : str
            ID покупателя
        total_amount : float
            Общая сумма заказа
        customer_info : str
            Информация о покупателе
        order_items : list of dict
            Список товаров в заказе
            
        Returns
        -------
        bool
            True если заказ успешно создан, False при ошибке
        """
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        order_data = {
            'customer_id': customer_id,
            'total_amount': f"{total_amount:.2f}",
            'order_date': order_date,
            'customer_info': customer_info
        }
        
        if self.validate(order_data):
            order_data['id'] = self.get_next_id()
            self.data.append(order_data)
            
            if self.save_data():
                for item in order_items:
                    item_data = {
                        'order_id': order_data['id'],
                        'product_id': item['product_id'],
                        'quantity': str(item['quantity']),
                        'price': f"{item['price']:.2f}",
                        'total': f"{item['total']:.2f}"
                    }
                    self.order_items_model.add_item(item_data)
                
                return True
        return False
    
    def get_order_items(self, order_id):
        """
        Получение всех товаров для конкретного заказа.
        
        Parameters
        ----------
        order_id : str
            ID заказа
            
        Returns
        -------
        list of dict
            Список товаров в указанном заказе
        """
        return self.order_items_model.get_items_by_order(order_id)
    
    def sort_orders(self, sort_by='date', ascending=True):
        """
        Сортировка заказов по различным критериям.
        
        Parameters
        ----------
        sort_by : {'date', 'amount', 'id'}, optional
            Критерий сортировки (по умолчанию 'date')
        ascending : bool, optional
            Направление сортировки (по умолчанию True - по возрастанию)
            
        Returns
        -------
        list of dict
            Отсортированный список заказов
            
        Notes
        -----
        Использует алгоритм быстрой сортировки (quick sort)
        """
        get_key = lambda x: (
            datetime.strptime(x['order_date'], "%Y-%m-%d %H:%M:%S") if sort_by == 'date' else
            float(x['total_amount']) if sort_by == 'amount' else
            int(x['id'])
        )
        
        def quick_sort(arr):
            if len(arr) <= 1:
                return arr
            pivot = arr[len(arr) // 2]
            left = [x for x in arr if get_key(x) < get_key(pivot)]
            middle = [x for x in arr if get_key(x) == get_key(pivot)]
            right = [x for x in arr if get_key(x) > get_key(pivot)]
            return quick_sort(left) + middle + quick_sort(right)
        
        sorted_data = quick_sort(self.data.copy())
        
        if not ascending:
            sorted_data.reverse()
            
        return sorted_data


class OrderItemsModel(BaseModel):
    """
    Модель для работы с товарами в заказах.
    
    Наследует от BaseModel и добавляет специфичную для товаров заказов
    функциональность.
    """
    
    def __init__(self):
        """
        Инициализация модели товаров заказов.
        
        Notes
        -----
        Автоматически загружает данные из файла 'order_items.csv'
        """
        super().__init__('order_items.csv', 
                        ['id', 'order_id', 'product_id', 'quantity', 'price', 'total'])
        self.load_data()
    
    def validate(self, item):
        """
        Валидация данных товара заказа.
        
        Parameters
        ----------
        item : dict
            Словарь с данными товара заказа
            
        Returns
        -------
        bool
            True если данные валидны, False в противном случае
            
        Raises
        ------
        Shows messagebox with validation errors
        """
        try:
            float(item.get('price', 0))
            float(item.get('total', 0))
            int(item.get('quantity', 0))
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные товара")
            return False
        return True
    
    def get_items_by_order(self, order_id):
        """
        Получение всех товаров для конкретного заказа.
        
        Parameters
        ----------
        order_id : str
            ID заказа
            
        Returns
        -------
        list of dict
            Список товаров в указанном заказе
        """
        return [item for item in self.data if item['order_id'] == str(order_id)]