<<<<<<< HEAD
import csv
import json
import os
from models import CustomerModel, ProductModel, OrderModel


class DatabaseManager:
    """
    Менеджер базы данных для работы с CSV и JSON файлами.
    
    Обеспечивает импорт/экспорт данных, а также создание необходимых файлов
    для хранения информации о клиентах, товарах и заказах.
    
    Attributes
    ----------
    customer_model : CustomerModel
        Модель данных клиентов
    product_model : ProductModel
        Модель данных товаров  
    order_model : OrderModel
        Модель данных заказов
    """
    
    def __init__(self):
        """
        Инициализация менеджера базы данных.
        
        Создает экземпляры моделей данных для работы с клиентами,
        товарами и заказами.
        """
        self.customer_model = CustomerModel()
        self.product_model = ProductModel()
        self.order_model = OrderModel()
    
    def create_files_if_not_exist(self):
        """
        Создает необходимые файлы CSV, если они не существуют.
        
        Проверяет наличие файлов customers.csv, products.csv, orders.csv
        и order_items.csv. Если какой-либо файл отсутствует, вызывает
        метод save_data соответствующей модели для создания файла
        с заголовками колонок.
        
        Notes
        -----
        Метод должен вызываться при инициализации приложения для
        обеспечения наличия всех необходимых файлов данных.
        """
        if not os.path.exists('customers.csv'):
            self.customer_model.save_data()
        if not os.path.exists('products.csv'):
            self.product_model.save_data()
        if not os.path.exists('orders.csv'):
            self.order_model.save_data()
        if not os.path.exists('order_items.csv'):
            self.order_model.order_items_model.save_data()
    
    def export_to_csv(self, data, filename, fieldnames):
        """
        Экспортирует данные в CSV файл.
        
        Parameters
        ----------
        data : list of dict
            Список словарей с данными для экспорта. Каждый словарь представляет
            одну строку данных, где ключи соответствуют названиям колонок.
        filename : str
            Имя файла для сохранения (например, 'export.csv').
        fieldnames : list of str
            Список названий колонок в правильном порядке.
        
        Returns
        -------
        bool
            True если экспорт выполнен успешно, False при возникновении ошибки.
        
        Examples
        --------
        >>> data = [{'name': 'John', 'age': 25}, {'name': 'Alice', 'age': 30}]
        >>> fieldnames = ['name', 'age']
        >>> export_to_csv(data, 'people.csv', fieldnames)
        True
        """
        try:
            with open(filename, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Ошибка при экспорте в CSV: {e}")
            return False
    
    def import_from_csv(self, filename, model):
        """
        Импортирует данные из CSV файла в указанную модель данных.
        
        Parameters
        ----------
        filename : str
            Имя файла для импорта (например, 'import.csv').
        model : BaseModel
            Модель данных для добавления элементов. Должна иметь метод add_item().
        
        Returns
        -------
        int
            Количество успешно импортированных записей. Возвращает -1 при ошибке.
        
        Raises
        ------
        FileNotFoundError
            Если указанный файл не существует.
        PermissionError
            Если нет прав на чтение файла.
        
        Notes
        -----
        Метод использует метод add_item модели для валидации и добавления
        каждого элемента данных.
        """
        try:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Файл {filename} не найден")
                
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                imported_data = list(reader)
            
            success_count = 0
            for item in imported_data:
                if model.add_item(item):
                    success_count += 1
            
            return success_count
        except Exception as e:
            print(f"Ошибка при импорте из CSV: {e}")
            return -1
    
    def export_to_json(self, data, filename):
        """
        Экспортирует данные в JSON файл.
        
        Parameters
        ----------
        data : list or dict
            Данные для экспорта. Могут быть списком словарей или словарем.
        filename : str
            Имя файла для сохранения (например, 'export.json').
        
        Returns
        -------
        bool
            True если экспорт выполнен успешно, False при возникновении ошибки.
        
        Notes
        -----
        Файл сохраняется с отступами (indent=4) и поддержкой Unicode
        (ensure_ascii=False).
        """
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Ошибка при экспорте в JSON: {e}")
            return False
    
    def import_from_json(self, filename, model):
        """
        Импортирует данные из JSON файла в указанную модель данных.
        
        Parameters
        ----------
        filename : str
            Имя файла для импорта (например, 'import.json').
        model : BaseModel
            Модель данных для добавления элементов. Должна иметь метод add_item().
        
        Returns
        -------
        int
            Количество успешно импортированных записей. Возвращает -1 при ошибке.
        
        Raises
        ------
        FileNotFoundError
            Если указанный файл не существует.
        JSONDecodeError
            Если файл содержит некорректный JSON.
        
        Notes
        -----
        Метод ожидает, что JSON файл содержит массив объектов или объект,
        который можно итерировать.
        """
        try:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Файл {filename} не найден")
                
            with open(filename, 'r', encoding='utf-8') as file:
                imported_data = json.load(file)
            
            success_count = 0
            # Обрабатываем как списки, так и одиночные объекты
            if not isinstance(imported_data, list):
                imported_data = [imported_data]
                
            for item in imported_data:
                if model.add_item(item):
                    success_count += 1
            
            return success_count
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}")
            return -1
        except Exception as e:
            print(f"Ошибка при импорте из JSON: {e}")
=======
import csv
import json
import os
from models import CustomerModel, ProductModel, OrderModel


class DatabaseManager:
    """
    Менеджер базы данных для работы с CSV и JSON файлами.
    
    Обеспечивает импорт/экспорт данных, а также создание необходимых файлов
    для хранения информации о клиентах, товарах и заказах.
    
    Attributes
    ----------
    customer_model : CustomerModel
        Модель данных клиентов
    product_model : ProductModel
        Модель данных товаров  
    order_model : OrderModel
        Модель данных заказов
    """
    
    def __init__(self):
        """
        Инициализация менеджера базы данных.
        
        Создает экземпляры моделей данных для работы с клиентами,
        товарами и заказами.
        """
        self.customer_model = CustomerModel()
        self.product_model = ProductModel()
        self.order_model = OrderModel()
    
    def create_files_if_not_exist(self):
        """
        Создает необходимые файлы CSV, если они не существуют.
        
        Проверяет наличие файлов customers.csv, products.csv, orders.csv
        и order_items.csv. Если какой-либо файл отсутствует, вызывает
        метод save_data соответствующей модели для создания файла
        с заголовками колонок.
        
        Notes
        -----
        Метод должен вызываться при инициализации приложения для
        обеспечения наличия всех необходимых файлов данных.
        """
        if not os.path.exists('customers.csv'):
            self.customer_model.save_data()
        if not os.path.exists('products.csv'):
            self.product_model.save_data()
        if not os.path.exists('orders.csv'):
            self.order_model.save_data()
        if not os.path.exists('order_items.csv'):
            self.order_model.order_items_model.save_data()
    
    def export_to_csv(self, data, filename, fieldnames):
        """
        Экспортирует данные в CSV файл.
        
        Parameters
        ----------
        data : list of dict
            Список словарей с данными для экспорта. Каждый словарь представляет
            одну строку данных, где ключи соответствуют названиям колонок.
        filename : str
            Имя файла для сохранения (например, 'export.csv').
        fieldnames : list of str
            Список названий колонок в правильном порядке.
        
        Returns
        -------
        bool
            True если экспорт выполнен успешно, False при возникновении ошибки.
        
        Examples
        --------
        >>> data = [{'name': 'John', 'age': 25}, {'name': 'Alice', 'age': 30}]
        >>> fieldnames = ['name', 'age']
        >>> export_to_csv(data, 'people.csv', fieldnames)
        True
        """
        try:
            with open(filename, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Ошибка при экспорте в CSV: {e}")
            return False
    
    def import_from_csv(self, filename, model):
        """
        Импортирует данные из CSV файла в указанную модель данных.
        
        Parameters
        ----------
        filename : str
            Имя файла для импорта (например, 'import.csv').
        model : BaseModel
            Модель данных для добавления элементов. Должна иметь метод add_item().
        
        Returns
        -------
        int
            Количество успешно импортированных записей. Возвращает -1 при ошибке.
        
        Raises
        ------
        FileNotFoundError
            Если указанный файл не существует.
        PermissionError
            Если нет прав на чтение файла.
        
        Notes
        -----
        Метод использует метод add_item модели для валидации и добавления
        каждого элемента данных.
        """
        try:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Файл {filename} не найден")
                
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                imported_data = list(reader)
            
            success_count = 0
            for item in imported_data:
                if model.add_item(item):
                    success_count += 1
            
            return success_count
        except Exception as e:
            print(f"Ошибка при импорте из CSV: {e}")
            return -1
    
    def export_to_json(self, data, filename):
        """
        Экспортирует данные в JSON файл.
        
        Parameters
        ----------
        data : list or dict
            Данные для экспорта. Могут быть списком словарей или словарем.
        filename : str
            Имя файла для сохранения (например, 'export.json').
        
        Returns
        -------
        bool
            True если экспорт выполнен успешно, False при возникновении ошибки.
        
        Notes
        -----
        Файл сохраняется с отступами (indent=4) и поддержкой Unicode
        (ensure_ascii=False).
        """
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Ошибка при экспорте в JSON: {e}")
            return False
    
    def import_from_json(self, filename, model):
        """
        Импортирует данные из JSON файла в указанную модель данных.
        
        Parameters
        ----------
        filename : str
            Имя файла для импорта (например, 'import.json').
        model : BaseModel
            Модель данных для добавления элементов. Должна иметь метод add_item().
        
        Returns
        -------
        int
            Количество успешно импортированных записей. Возвращает -1 при ошибке.
        
        Raises
        ------
        FileNotFoundError
            Если указанный файл не существует.
        JSONDecodeError
            Если файл содержит некорректный JSON.
        
        Notes
        -----
        Метод ожидает, что JSON файл содержит массив объектов или объект,
        который можно итерировать.
        """
        try:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Файл {filename} не найден")
                
            with open(filename, 'r', encoding='utf-8') as file:
                imported_data = json.load(file)
            
            success_count = 0
            # Обрабатываем как списки, так и одиночные объекты
            if not isinstance(imported_data, list):
                imported_data = [imported_data]
                
            for item in imported_data:
                if model.add_item(item):
                    success_count += 1
            
            return success_count
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}")
            return -1
        except Exception as e:
            print(f"Ошибка при импорте из JSON: {e}")
>>>>>>> 3e84103c2d42b90c7f0d0c382a243a515fcbdfdc
            return -1