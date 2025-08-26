import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Добавляем путь к проекту для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock messagebox для тестов
class MockMessagebox:
    """
    Mock-класс для замены messagebox в тестах.
    
    Methods
    -------
    showerror(title, message)
        Выводит сообщение об ошибке в консоль вместо показа диалогового окна.
    """
    
    @staticmethod
    def showerror(title, message):
        """
        Выводит сообщение об ошибке в консоль.
        
        Parameters
        ----------
        title : str
            Заголовок ошибки.
        message : str
            Текст сообщения об ошибке.
        """
        print(f"{title} - {message}")

# Подменяем messagebox перед импортом моделей
import models
models.messagebox = MockMessagebox()

from models import BaseModel, CustomerModel, ProductModel, OrderModel, OrderItemsModel


class TestBaseModel(unittest.TestCase):
    """
    Тесты для базового класса BaseModel.
    
    Methods
    -------
    setUp()
        Подготовка тестового окружения для BaseModel.
    test_load_data()
        Тестирование загрузки данных.
    test_save_data()
        Тестирование сохранения данных.
    test_get_next_id()
        Тестирование генерации следующего ID.
    test_add_item()
        Тестирование добавления элемента.
    test_find_by_id()
        Тестирование поиска по ID.
    test_delete_item()
        Тестирование удаления элемента.
    """
    
    def setUp(self):
        """Подготовка тестового окружения для BaseModel."""
        # Создаем mock-модель без абстрактных методов
        with patch.object(BaseModel, '__abstractmethods__', set()):
            self.model = BaseModel('test.csv', ['id', 'name'])
            self.model.data = [{'id': '1', 'name': 'Test'}]
            # Mock методы, которые работают с файловой системой
            self.model.load_data = MagicMock(return_value=self.model.data)
            self.model.save_data = MagicMock(return_value=True)
            self.model.validate = MagicMock(return_value=True)
    
    def test_load_data(self):
        """Тестирование загрузки данных."""
        result = self.model.load_data()
        self.assertIsInstance(result, list)
        self.model.load_data.assert_called_once()
    
    def test_save_data(self):
        """Тестирование сохранения данных."""
        result = self.model.save_data()
        self.assertTrue(result)
        self.model.save_data.assert_called_once()
    
    def test_get_next_id(self):
        """Тестирование генерации следующего ID."""
        next_id = self.model.get_next_id()
        self.assertEqual(next_id, '2')
    
    def test_add_item(self):
        """Тестирование добавления элемента."""
        new_item = {'name': 'New'}
        result = self.model.add_item(new_item)
        self.assertTrue(result)
        self.assertIn({'id': '2', 'name': 'New'}, self.model.data)
    
    def test_find_by_id(self):
        """Тестирование поиска по ID."""
        found = self.model.find_by_id('1')
        self.assertEqual(found, {'id': '1', 'name': 'Test'})
        
        not_found = self.model.find_by_id('999')
        self.assertIsNone(not_found)
    
    def test_delete_item(self):
        """Тестирование удаления элемента."""
        result = self.model.delete_item('1')
        self.assertTrue(result)
        self.assertNotIn({'id': '1', 'name': 'Test'}, self.model.data)


class TestCustomerModel(unittest.TestCase):
    """
    Тесты для модели клиентов CustomerModel.
    
    Methods
    -------
    setUp()
        Подготовка тестового окружения для CustomerModel.
    test_validate_valid()
        Тестирование валидации корректных данных клиента.
    test_validate_invalid_phone()
        Тестирование валидации некорректного телефона.
    test_validate_invalid_email()
        Тестирование валидации некорректного email.
    test_validate_missing_required_fields()
        Тестирование валидации при отсутствии обязательных полей.
    test_validate_phone_method()
        Тестирование метода validate_phone.
    test_validate_email_method()
        Тестирование метода validate_email.
    test_search()
        Тестирование поиска клиентов.
    """
    
    def setUp(self):
        """Подготовка тестового окружения для CustomerModel."""
        # Mock файловых операций
        self.file_mock = mock_open()
        with patch('builtins.open', self.file_mock), \
             patch('csv.DictWriter'), \
             patch('csv.DictReader'):
            self.customer_model = CustomerModel()
            self.customer_model.data = []
        
        self.valid_customer = {
            'last_name': 'Иванов',
            'first_name': 'Иван', 
            'middle_name': 'Иванович',
            'phone': '+7(999)123-45-67',
            'email': 'ivanov@example.com'
        }
    
    def test_validate_valid(self):
        """Тестирование валидации корректных данных клиента."""
        result = self.customer_model.validate(self.valid_customer)
        self.assertTrue(result)
    
    def test_validate_invalid_phone(self):
        """Тестирование валидации некорректного телефона."""
        invalid_customer = self.valid_customer.copy()
        invalid_customer['phone'] = 'invalid_phone'
        result = self.customer_model.validate(invalid_customer)
        self.assertFalse(result)
    
    def test_validate_invalid_email(self):
        """Тестирование валидации некорректного email."""
        invalid_customer = self.valid_customer.copy()
        invalid_customer['email'] = 'invalid_email'
        result = self.customer_model.validate(invalid_customer)
        self.assertFalse(result)
    
    def test_validate_missing_required_fields(self):
        """Тестирование валидации при отсутствии обязательных полей."""
        invalid_customer = self.valid_customer.copy()
        invalid_customer['last_name'] = ''
        result = self.customer_model.validate(invalid_customer)
        self.assertFalse(result)
        
        invalid_customer = self.valid_customer.copy()
        invalid_customer['first_name'] = ''
        result = self.customer_model.validate(invalid_customer)
        self.assertFalse(result)
    
    def test_validate_phone_method(self):
        """Тестирование метода validate_phone."""
        valid_phones = ['+7(999)123-45-67', '89991234567', '+7 999 123 45 67']
        invalid_phones = ['123', 'abc', '+799912345678', '']
        
        for phone in valid_phones:
            self.assertTrue(self.customer_model.validate_phone(phone))
        
        for phone in invalid_phones:
            self.assertFalse(self.customer_model.validate_phone(phone))
    
    def test_validate_email_method(self):
        """Тестирование метода validate_email."""
        valid_emails = ['test@example.com', 'user.name@domain.ru']
        invalid_emails = ['invalid', 'user@', '@domain.com']
        
        for email in valid_emails:
            self.assertTrue(self.customer_model.validate_email(email))
        
        for email in invalid_emails:
            self.assertFalse(self.customer_model.validate_email(email))
    
    def test_search(self):
        """Тестирование поиска клиентов."""
        # Исправляем данные: добавляем все обязательные поля
        self.customer_model.data = [
            {'id': '1', 'last_name': 'Иванов', 'first_name': 'Иван', 'middle_name': 'Иванович', 'phone': '+79991234567', 'email': 'ivanov@mail.ru'},
            {'id': '2', 'last_name': 'Петров', 'first_name': 'Петр', 'middle_name': 'Петрович', 'phone': '+79998887766', 'email': 'petrov@mail.ru'}
        ]
        
        results = self.customer_model.search('Иванов')
        self.assertEqual(len(results), 1)
        
        results = self.customer_model.search('')
        self.assertEqual(len(results), 2)
        
        results = self.customer_model.search('Петрович')
        self.assertEqual(len(results), 1)


class TestProductModel(unittest.TestCase):
    """
    Тесты для модели товаров ProductModel.
    
    Methods
    -------
    setUp()
        Подготовка тестового окружения для ProductModel.
    test_validate_valid()
        Тестирование валидации корректных данных товара.
    test_validate_negative_price()
        Тестирование валидации отрицательной цены.
    test_validate_non_numeric_price()
        Тестирование валидации нечисловой цены.
    test_validate_missing_fields()
        Тестирование валидации при отсутствии обязательных полей.
    test_search()
        Тестирование поиска товаров.
    """
    
    def setUp(self):
        """Подготовка тестового окружения для ProductModel."""
        self.file_mock = mock_open()
        with patch('builtins.open', self.file_mock), \
             patch('csv.DictWriter'), \
             patch('csv.DictReader'):
            self.product_model = ProductModel()
            self.product_model.data = []
        
        self.valid_product = {
            'name': 'Тестовый продукт',
            'price': '100.00',
            'unit': 'шт.'
        }
    
    def test_validate_valid(self):
        """Тестирование валидации корректных данных товара."""
        result = self.product_model.validate(self.valid_product)
        self.assertTrue(result)
    
    def test_validate_negative_price(self):
        """Тестирование валидации отрицательной цены."""
        invalid_product = self.valid_product.copy()
        invalid_product['price'] = '-100'
        result = self.product_model.validate(invalid_product)
        self.assertFalse(result)
    
    def test_validate_non_numeric_price(self):
        """Тестирование валидации нечисловой цены."""
        invalid_product = self.valid_product.copy()
        invalid_product['price'] = 'not_a_number'
        result = self.product_model.validate(invalid_product)
        self.assertFalse(result)
    
    def test_validate_missing_fields(self):
        """Тестирование валидации при отсутствии обязательных полей."""
        invalid_product = self.valid_product.copy()
        invalid_product['name'] = ''
        result = self.product_model.validate(invalid_product)
        self.assertFalse(result)
        
        invalid_product = self.valid_product.copy()
        invalid_product['unit'] = ''
        result = self.product_model.validate(invalid_product)
        self.assertFalse(result)
    
    def test_search(self):
        """Тестирование поиска товаров."""
        self.product_model.data = [
            {'id': '1', 'name': 'Продукт 1', 'price': '100', 'unit': 'шт.'},
            {'id': '2', 'name': 'Продукт 2', 'price': '200', 'unit': 'кг.'}
        ]
        
        results = self.product_model.search('Продукт')
        self.assertEqual(len(results), 2)
        
        results = self.product_model.search('кг')
        self.assertEqual(len(results), 1)


class TestOrderModel(unittest.TestCase):
    """
    Тесты для модели заказов OrderModel.
    
    Methods
    -------
    setUp()
        Подготовка тестового окружения для OrderModel.
    test_validate_valid()
        Тестирование валидации корректных данных заказа.
    test_validate_missing_customer_id()
        Тестирование валидации при отсутствии customer_id.
    test_validate_invalid_total_amount()
        Тестирование валидации некорректной суммы.
    test_create_order()
        Тестирование создания заказа.
    test_get_order_items()
        Тестирование получения товаров заказа.
    test_sort_orders_by_amount()
        Тестирование сортировки заказов по сумме.
    test_sort_orders_by_date()
        Тестирование сортировки заказов по дате.
    """
    
    def setUp(self):
        """Подготовка тестового окружения для OrderModel."""
        self.file_mock = mock_open()
        with patch('builtins.open', self.file_mock), \
             patch('csv.DictWriter'), \
             patch('csv.DictReader'):
            self.order_model = OrderModel()
            self.order_model.data = []
            
            # Создаем реальный OrderItemsModel с mock-ами
            self.order_items_model = OrderItemsModel()
            self.order_items_model.data = []
            self.order_items_model.save_data = MagicMock(return_value=True)
            self.order_items_model.validate = MagicMock(return_value=True)
            
            self.order_model.order_items_model = self.order_items_model
    
    def test_validate_valid(self):
        """Тестирование валидации корректных данных заказа."""
        valid_order = {
            'customer_id': '1',
            'total_amount': '500.00',
            'order_date': '2024-01-01 10:00:00',
            'customer_info': 'Иван Иванов'
        }
        result = self.order_model.validate(valid_order)
        self.assertTrue(result)
    
    def test_validate_missing_customer_id(self):
        """Тестирование валидации при отсутствии customer_id."""
        invalid_order = {
            'total_amount': '500.00',
            'customer_info': 'Иван Иванов'
        }
        result = self.order_model.validate(invalid_order)
        self.assertFalse(result)
    
    def test_validate_invalid_total_amount(self):
        """Тестирование валидации некорректной суммы."""
        invalid_order = {
            'customer_id': '1',
            'total_amount': '0',
            'customer_info': 'Иван Иванов'
        }
        result = self.order_model.validate(invalid_order)
        self.assertFalse(result)
    
    def test_create_order(self):
        """Тестирование создания заказа."""
        order_items = [
            {'product_id': '1', 'quantity': 2, 'price': 100.0, 'total': 200.0},
            {'product_id': '2', 'quantity': 1, 'price': 300.0, 'total': 300.0}
        ]
        
        # Mock save_data чтобы избежать реального сохранения
        with patch.object(self.order_model, 'save_data', return_value=True):
            result = self.order_model.create_order('1', 500.0, 'Иван Иванов', order_items)
            self.assertTrue(result)
    
    def test_get_order_items(self):
        """Тестирование получения товаров заказа."""
        # Добавляем тестовые данные в order_items_model
        self.order_model.order_items_model.data = [
            {'id': '1', 'order_id': '1', 'product_id': '1', 'quantity': '2', 'price': '100', 'total': '200'},
            {'id': '2', 'order_id': '1', 'product_id': '2', 'quantity': '1', 'price': '300', 'total': '300'},
            {'id': '3', 'order_id': '2', 'product_id': '3', 'quantity': '5', 'price': '50', 'total': '250'}
        ]
        
        items = self.order_model.get_order_items('1')
        self.assertEqual(len(items), 2)
        self.assertIsInstance(items, list)
        
        # Проверяем, что возвращаются только товары для order_id = '1'
        order_ids = [item['order_id'] for item in items]
        self.assertTrue(all(order_id == '1' for order_id in order_ids))
    
    def test_sort_orders_by_amount(self):
        """Тестирование сортировки заказов по сумме."""
        self.order_model.data = [
            {'id': '1', 'total_amount': '300.00', 'order_date': '2024-01-01 10:00:00'},
            {'id': '2', 'total_amount': '100.00', 'order_date': '2024-01-02 10:00:00'},
            {'id': '3', 'total_amount': '200.00', 'order_date': '2024-01-03 10:00:00'}
        ]
        
        # Сортировка по сумме по возрастанию
        sorted_orders = self.order_model.sort_orders(sort_by='amount', ascending=True)
        self.assertEqual(sorted_orders[0]['id'], '2')
        self.assertEqual(sorted_orders[1]['id'], '3')
        self.assertEqual(sorted_orders[2]['id'], '1')
        
        # Сортировка по сумме по убыванию
        sorted_orders = self.order_model.sort_orders(sort_by='amount', ascending=False)
        self.assertEqual(sorted_orders[0]['id'], '1')
        self.assertEqual(sorted_orders[1]['id'], '3')
        self.assertEqual(sorted_orders[2]['id'], '2')
    
    def test_sort_orders_by_date(self):
        """Тестирование сортировки заказов по дате."""
        self.order_model.data = [
            {'id': '1', 'total_amount': '300.00', 'order_date': '2024-01-03 10:00:00'},
            {'id': '2', 'total_amount': '100.00', 'order_date': '2024-01-01 10:00:00'},
            {'id': '3', 'total_amount': '200.00', 'order_date': '2024-01-02 10:00:00'}
        ]
        
        # Сортировка по дате по возрастанию
        sorted_orders = self.order_model.sort_orders(sort_by='date', ascending=True)
        self.assertEqual(sorted_orders[0]['id'], '2')
        self.assertEqual(sorted_orders[1]['id'], '3')
        self.assertEqual(sorted_orders[2]['id'], '1')


class TestOrderItemsModel(unittest.TestCase):
    """
    Тесты для модели товаров заказов OrderItemsModel.
    
    Methods
    -------
    setUp()
        Подготовка тестового окружения для OrderItemsModel.
    test_validate_valid()
        Тестирование валидации корректных данных товара заказа.
    test_validate_invalid_numeric_fields()
        Тестирование валидации некорректных числовых полей.
    test_get_items_by_order()
        Тестирование получения товаров по ID заказа.
    """
    
    def setUp(self):
        """Подготовка тестового окружения для OrderItemsModel."""
        self.file_mock = mock_open()
        with patch('builtins.open', self.file_mock), \
             patch('csv.DictWriter'), \
             patch('csv.DictReader'):
            self.order_items_model = OrderItemsModel()
            self.order_items_model.data = []
    
    def test_validate_valid(self):
        """Тестирование валидации корректных данных товара заказа."""
        valid_item = {
            'order_id': '1',
            'product_id': '1',
            'quantity': '2',
            'price': '100.00',
            'total': '200.00'
        }
        result = self.order_items_model.validate(valid_item)
        self.assertTrue(result)
    
    def test_validate_invalid_numeric_fields(self):
        """Тестирование валидации некорректных числовых полей."""
        invalid_item = {
            'order_id': '1',
            'product_id': '1',
            'quantity': 'not_a_number',
            'price': '100.00',
            'total': '200.00'
        }
        result = self.order_items_model.validate(invalid_item)
        self.assertFalse(result)
    
    def test_get_items_by_order(self):
        """Тестирование получения товаров по ID заказа."""
        self.order_items_model.data = [
            {'id': '1', 'order_id': '1', 'product_id': '1', 'quantity': '2', 'price': '100', 'total': '200'},
            {'id': '2', 'order_id': '1', 'product_id': '2', 'quantity': '1', 'price': '300', 'total': '300'},
            {'id': '3', 'order_id': '2', 'product_id': '3', 'quantity': '5', 'price': '50', 'total': '250'}
        ]
        
        # Получаем товары для заказа 1
        items = self.order_items_model.get_items_by_order('1')
        self.assertEqual(len(items), 2)
        
        # Получаем товары для заказа 2
        items = self.order_items_model.get_items_by_order('2')
        self.assertEqual(len(items), 1)
        
        # Получаем товары для несуществующего заказа
        items = self.order_items_model.get_items_by_order('999')
        self.assertEqual(len(items), 0)


if __name__ == '__main__':
    """
    Точка входа для запуска unit-тестов.
    
    Запускает все тесты с повышенной детализацией вывода (verbosity=2).
    """
    unittest.main(verbosity=2)