import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import json
from models import CustomerModel, ProductModel, OrderModel
from db import DatabaseManager
from analysis import DataAnalyzer

class OrderApp:
    """
    Основной класс приложения для управления заказами.
    
    Attributes
    ----------
    root : tk.Tk
        Главное окно приложения
    customer_model : CustomerModel
        Модель для работы с покупателями
    product_model : ProductModel
        Модель для работы с товарами
    order_model : OrderModel
        Модель для работы с заказами
    db_manager : DatabaseManager
        Менеджер базы данных
    analyzer : DataAnalyzer
        Анализатор данных для визуализации
    current_order_total : float
        Текущая общая сумма заказа
    order_items : list
        Список товаров в текущем заказе
    selected_customer_index : int
        Индекс выбранного покупателя
    selected_product_index : int
        Индекс выбранного товара
    selected_order_item_index : int
        Индекс выбранного элемента заказа
    filtered_customers : list
        Отфильтрованный список покупателей
    filtered_products : list
        Отфильтрованный список товаров
    """
    
    def __init__(self, root):
        """
        Инициализация главного окна приложения.
        
        Parameters
        ----------
        root : tk.Tk
            Главное окно приложения
        """
        self.root = root
        self.root.title("Система управления заказами")
        
        # Центрирование окна на экране
        window_width = 1000
        window_height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Инициализация моделей данных
        self.customer_model = CustomerModel()
        self.product_model = ProductModel()
        self.order_model = OrderModel()
        self.db_manager = DatabaseManager()
        self.analyzer = DataAnalyzer(self.customer_model, self.product_model, self.order_model)
        
        # Переменные состояния
        self.current_order_total = 0
        self.order_items = []
        self.selected_customer_index = -1
        self.selected_product_index = -1
        self.selected_order_item_index = -1
        self.selected_product_in_table = None
        self.selected_customer_in_table = None
        self.last_customer_selection = 0
        self.last_product_selection = 0
        
        # Фильтрованные данные
        self.filtered_customers = self.customer_model.get_all().copy()
        self.filtered_products = self.product_model.get_all().copy()
        
        # Переменные поиска
        self.customer_search_var = tk.StringVar()
        self.product_search_var = tk.StringVar()
        
        # Инициализация БД и UI
        self.db_manager.create_files_if_not_exist()
        self._setup_ui()
        self._initialize_data()
    
    def _setup_ui(self):
        """
        Настройка пользовательского интерфейса с вкладками.
        
        Создает и настраивает основные элементы интерфейса:
        - Вкладки для различных функций приложения
        - Элементы управления на каждой вкладке
        """
        self.tab_control = ttk.Notebook(self.root)
        
        # Создание вкладок
        self.tab_order = ttk.Frame(self.tab_control)
        self.tab_history = ttk.Frame(self.tab_control)
        self.tab_products = ttk.Frame(self.tab_control)
        self.tab_customers = ttk.Frame(self.tab_control)
        self.tab_analytics = ttk.Frame(self.tab_control)
        
        # Добавление вкладок
        self.tab_control.add(self.tab_order, text='Создать заказ')
        self.tab_control.add(self.tab_history, text='История заказов')
        self.tab_control.add(self.tab_products, text='Управление товарами')
        self.tab_control.add(self.tab_customers, text='Управление покупателями')
        self.tab_control.add(self.tab_analytics, text='Визуализация и анализ')
        
        self.tab_control.pack(expand=1, fill='both')
        
        # Инициализация содержимого вкладок
        self.init_order_tab()
        self.init_history_tab()
        self.init_products_tab()
        self.init_customers_tab()
        self.init_analytics_tab()
    
    def _initialize_data(self):
        """
        Первоначальная загрузка данных в интерфейс.
        
        Загружает данные о покупателях и товарах в соответствующие
        элементы интерфейса при запуске приложения.
        """
        self.update_customer_listbox()
        self.update_product_listbox()
    
    def _create_scrollable_frame(self, parent):
        """
        Создание фрейма с прокруткой.
        
        Parameters
        ----------
        parent : tk.Widget
            Родительский виджет
        
        Returns
        -------
        ttk.Frame
            Прокручиваемый фрейм
        """
        frame = ttk.Frame(parent)
        frame.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return scrollable_frame
    
    def _create_search_frame(self, parent, label_text, search_var, clear_callback, filter_callback):
        """
        Создание фрейма поиска с полем ввода и кнопкой очистки.
        
        Parameters
        ----------
        parent : tk.Widget
            Родительский виджет
        label_text : str
            Текст метки поиска
        search_var : tk.StringVar
            Переменная для хранения поискового запроса
        clear_callback : callable
            Функция для очистки поиска
        filter_callback : callable
            Функция для фильтрации данных
        
        Returns
        -------
        ttk.Entry
            Поле ввода для поиска
        """
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text=label_text).pack(side='left', padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        clear_btn = ttk.Button(search_frame, text="X", width=2, command=clear_callback)
        clear_btn.pack(side='left')
        
        search_var.trace('w', filter_callback)
        
        return search_entry
    
    def _create_listbox_with_scrollbar(self, parent, height=8, bind_callback=None):
        """
        Создание списка с полосой прокрутки.
        
        Parameters
        ----------
        parent : tk.Widget
            Родительский виджет
        height : int, optional
            Высота списка (по умолчанию 8)
        bind_callback : callable, optional
            Функция обработки выбора элемента
        
        Returns
        -------
        tk.Listbox
            Список с прокруткой
        """
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        listbox = tk.Listbox(list_frame, height=height)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        if bind_callback:
            listbox.bind('<<ListboxSelect>>', bind_callback)
        
        return listbox
    
    def _create_treeview(self, parent, columns_config, show='headings', height=None):
        """
        Создание таблицы Treeview с указанными колонками.
        
        Parameters
        ----------
        parent : tk.Widget
            Родительский виджет
        columns_config : list of tuples
            Конфигурация колонок в формате [(id, heading, width), ...]
        show : str, optional
            Режим отображения (по умолчанию 'headings')
        height : int, optional
            Высота таблицы
        
        Returns
        -------
        ttk.Treeview
            Таблица Treeview
        """
        columns, headings, widths = zip(*columns_config)
        
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill='both', expand=True)
        
        tree = ttk.Treeview(tree_frame, columns=columns, show=show, height=height)
        
        for col, heading, width in zip(columns, headings, widths):
            tree.heading(col, text=heading)
            tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        return tree
    
    def _update_listbox(self, listbox, data, format_func, last_selection, update_callback=None):
        """
        Обновление содержимого Listbox с сохранением выделения.
        
        Parameters
        ----------
        listbox : tk.Listbox
            Обновляемый список
        data : list
            Данные для отображения
        format_func : callable
            Функция форматирования элементов
        last_selection : int
            Последний выбранный индекс
        update_callback : callable, optional
            Функция обновления после изменения выбора
        """
        current_selection = listbox.curselection()
        listbox.delete(0, tk.END)
        
        for item in data:
            listbox.insert(tk.END, format_func(item))
        
        if data:
            if current_selection and current_selection[0] < len(data):
                new_selection = current_selection[0]
            else:
                new_selection = min(last_selection, len(data) - 1)
            
            listbox.selection_set(new_selection)
            if update_callback:
                update_callback()
        else:
            if hasattr(self, 'customer_info_label'):
                self.customer_info_label.config(text="Покупатель: не выбран")
            if hasattr(self, 'price_label'):
                self.price_label.config(text="0.00")
                self.sum_label.config(text="0.00")
    
    def _validate_and_add(self, add_func, data, success_message, clear_entries=None):
        """
        Универсальный метод для валидации и добавления данных.
        
        Parameters
        ----------
        add_func : callable
            Функция добавления данных
        data : dict
            Данные для добавления
        success_message : str
            Сообщение об успешном добавлении
        clear_entries : list, optional
            Список полей для очистки
        
        Returns
        -------
        bool
            Результат операции добавления
        """
        try:
            if add_func(data):
                messagebox.showinfo("Успех", success_message)
                self._refresh_data()
                if clear_entries:
                    self._clear_entries(clear_entries)
                return True
            return False
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении: {str(e)}")
            return False
    
    def _clear_entries(self, entries):
        """
        Очистка полей ввода.
        
        Parameters
        ----------
        entries : list
            Список полей для очистки
        """
        for entry in entries:
            entry.delete(0, 'end')
    
    def _refresh_data(self):
        """
        Обновление всех данных в интерфейсе.
        
        Вызывает обновление всех списков и таблиц в приложении.
        """
        self.update_customer_listbox()
        self.update_product_listbox()
        if hasattr(self, 'refresh_products'):
            self.refresh_products()
        if hasattr(self, 'refresh_customers'):
            self.refresh_customers()
        if hasattr(self, 'refresh_history'):
            self.refresh_history()
    
    def update_customer_listbox(self):
        """Обновление списка покупателей с учетом фильтрации."""
        if hasattr(self, 'customer_listbox'):
            self._update_listbox(
                self.customer_listbox, 
                self.filtered_customers,
                lambda customer: f"{customer['last_name']} {customer['first_name']} {customer['middle_name']} - {customer['phone']}",
                self.last_customer_selection,
                self.update_customer_info
            )
    
    def update_product_listbox(self):
        """Обновление списка товаров с учетом фильтрации."""
        if hasattr(self, 'product_listbox'):
            self._update_listbox(
                self.product_listbox,
                self.filtered_products,
                lambda product: f"{product['name']} - {product['price']} руб./{product['unit']}",
                self.last_product_selection,
                self.update_product_price
            )
    
    def filter_customers(self, *args):
        """
        Фильтрация списка покупателей по поисковому запросу.
        
        Parameters
        ----------
        *args
            Аргументы для совместимости с trace
        """
        search_text = self.customer_search_var.get().lower()
        all_customers = self.customer_model.get_all()
        
        if not search_text:
            self.filtered_customers = all_customers.copy()
        else:
            self.filtered_customers = [
                customer for customer in all_customers
                if (search_text in customer['last_name'].lower() or
                    search_text in customer['first_name'].lower() or
                    search_text in customer['phone'].lower() or
                    search_text in customer['email'].lower())
            ]
        self.update_customer_listbox()
    
    def filter_products(self, *args):
        """
        Фильтрация списка товаров по поисковому запросу.
        
        Parameters
        ----------
        *args
            Аргументы для совместимости с trace
        """
        search_text = self.product_search_var.get().lower()
        all_products = self.product_model.get_all()
        
        if not search_text:
            self.filtered_products = all_products.copy()
        else:
            self.filtered_products = [
                product for product in all_products
                if search_text in product['name'].lower()
            ]
        self.update_product_listbox()
    
    def clear_customer_search(self):
        """Очистка поля поиска покупателей."""
        self.customer_search_var.set("")
    
    def clear_product_search(self):
        """Очистка поля поиска товаров."""
        self.product_search_var.set("")
    
    def update_customer_info(self):
        """Обновление информации о выбранном покупателе."""
        if (hasattr(self, 'customer_info_label') and 
            self.selected_customer_index >= 0 and 
            self.filtered_customers):
            
            customer = self.filtered_customers[self.selected_customer_index]
            customer_info = f"{customer['last_name']} {customer['first_name']} {customer['middle_name']} - {customer['phone']}"
            self.customer_info_label.config(text=f"Покупатель: {customer_info}")
    
    def update_product_price(self):
        """Обновление цены выбранного товара."""
        if (hasattr(self, 'price_label') and 
            self.selected_product_index >= 0 and 
            self.filtered_products):
            
            product = self.filtered_products[self.selected_product_index]
            self.price_label.config(text=f"{product['price']} руб.")
            self.calculate_sum()
    
    def _export_data(self, data, file_types, title, export_func):
        """
        Универсальный метод экспорта данных.
        
        Parameters
        ----------
        data : list
            Данные для экспорта
        file_types : list of tuples
            Типы файлов для диалога сохранения
        title : str
            Заголовок диалогового окна
        export_func : callable
            Функция экспорта данных
        """
        if not data:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=file_types[0][1],
            filetypes=file_types,
            title=title
        )
        
        if file_path:
            try:
                export_func(data, file_path)
                messagebox.showinfo("Успех", f"Данные успешно экспортированы в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")
    
    def _import_data(self, file_types, title, import_func, required_fields, success_message, add_func):
        """
        Универсальный метод импорта данных.
        
        Parameters
        ----------
        file_types : list of tuples
            Типы файлов для диалога открытия
        title : str
            Заголовок диалогового окна
        import_func : callable
            Функция импорта данных
        required_fields : list
            Обязательные поля в импортируемых данных
        success_message : str
            Сообщение об успешном импорте
        add_func : callable
            Функция добавления данных
        """
        file_path = filedialog.askopenfilename(filetypes=file_types, title=title)
        
        if file_path:
            try:
                imported_data = import_func(file_path)
                
                if not imported_data:
                    messagebox.showwarning("Предупреждение", "Файл не содержит данных!")
                    return
                
                for item in imported_data:
                    for field in required_fields:
                        if field not in item:
                            messagebox.showerror("Ошибка", f"В файле отсутствует обязательное поле: {field}")
                            return
                
                success_count = 0
                for item in imported_data:
                    if add_func(item):
                        success_count += 1
                
                messagebox.showinfo("Успех", success_message.format(success_count))
                self._refresh_data()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при импорте: {str(e)}")
    
    def _export_csv(self, data, file_path, fieldnames):
        """
        Экспорт данных в CSV формат.
        
        Parameters
        ----------
        data : list of dict
            Данные для экспорта
        file_path : str
            Путь к файлу
        fieldnames : list
            Заголовки колонок
        """
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    def _import_csv(self, file_path):
        """
        Импорт данных из CSV файла.
        
        Parameters
        ----------
        file_path : str
            Путь к файлу
        
        Returns
        -------
        list of dict
            Импортированные данные
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return list(csv.DictReader(file))
    
    def _export_json(self, data, file_path):
        """
        Экспорт данных в JSON формат.
        
        Parameters
        ----------
        data : list of dict
            Данные для экспорта
        file_path : str
            Путь к файлу
        """
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    
    def _import_json(self, file_path):
        """
        Импорт данных из JSON файла.
        
        Parameters
        ----------
        file_path : str
            Путь к файлу
        
        Returns
        -------
        list of dict
            Импортированные данные
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    def init_order_tab(self):
        """Инициализация вкладки создания заказов."""
        main_container = ttk.Frame(self.tab_order)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Фрейм выбора покупателя
        customer_frame = ttk.LabelFrame(left_panel, text="Выбор покупателя")
        customer_frame.pack(fill='x', pady=(0, 10))
        
        self._create_search_frame(customer_frame, "Поиск:", self.customer_search_var, 
                                self.clear_customer_search, self.filter_customers)
        
        self.customer_listbox = self._create_listbox_with_scrollbar(customer_frame, 8, self.on_customer_select)
        
        # Фрейм выбора товара
        product_frame = ttk.LabelFrame(left_panel, text="Выбор товара")
        product_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self._create_search_frame(product_frame, "Поиск:", self.product_search_var, 
                                self.clear_product_search, self.filter_products)
        
        self.product_listbox = self._create_listbox_with_scrollbar(product_frame, 8, self.on_product_select)
        
        # Фрейм управления заказом
        control_frame = ttk.LabelFrame(left_panel, text="Управление заказом")
        control_frame.pack(fill='x', pady=(0, 10))
        
        quantity_price_frame = ttk.Frame(control_frame)
        quantity_price_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(quantity_price_frame, text="Количество:").grid(row=0, column=0, padx=2, pady=5, sticky='e')
        self.quantity_spinbox = tk.Spinbox(quantity_price_frame, from_=1, to=100, width=7, command=self.calculate_sum)
        self.quantity_spinbox.grid(row=0, column=1, padx=2, pady=5)
        
        ttk.Label(quantity_price_frame, text="Цена:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.price_label = ttk.Label(quantity_price_frame, text="0.00 руб.")
        self.price_label.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(quantity_price_frame, text="Сумма:").grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.sum_label = ttk.Label(quantity_price_frame, text="0.00 руб.")
        self.sum_label.grid(row=0, column=5, padx=5, pady=5)
        
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill='x', padx=5, pady=5)
        
        self.add_button = ttk.Button(buttons_frame, text="Внести товар", command=self.add_product_to_order)
        self.add_button.pack(side='left', padx=5)
        
        ttk.Frame(buttons_frame).pack(side='left', fill='x', expand=True)
        
        self.remove_button = ttk.Button(buttons_frame, text="Удалить товар", command=self.remove_product_from_order)
        self.remove_button.pack(side='right', padx=5)
        
        self.quantity_spinbox.bind('<KeyRelease>', self.calculate_sum)
        self.quantity_spinbox.bind('<ButtonRelease>', self.calculate_sum)
        
        # Информационная панель
        info_frame = ttk.Frame(left_panel)
        info_frame.pack(fill='x', pady=(0, 10))
        
        self.customer_info_label = ttk.Label(info_frame, text="Покупатель: не выбран", font=("Arial", 8, "bold"))
        self.customer_info_label.pack(anchor='w', padx=5, pady=2)
        
        self.total_label = ttk.Label(info_frame, text=f"Общая сумма: {self.current_order_total:.2f} руб.")
        self.total_label.pack(anchor='w', padx=5, pady=2)
        
        # Кнопка создания заказа
        order_button_frame = ttk.Frame(left_panel)
        order_button_frame.pack(fill='x')
        
        self.create_order_button = ttk.Button(order_button_frame, text="Создать заказ", command=self.create_order)
        self.create_order_button.pack(pady=5)
        
        # Таблица текущего заказа
        order_table_frame = ttk.LabelFrame(right_panel, text="Текущий заказ")
        order_table_frame.pack(fill='both', expand=True)
        
        columns_config = [
            ('product', 'Товар', 200),
            ('quantity', 'Количество', 100),
            ('unit', 'Ед. изм.', 80),
            ('price', 'Цена', 100),
            ('total', 'Сумма', 100)
        ]
        
        self.order_tree = self._create_treeview(order_table_frame, columns_config)
        self.order_tree.bind('<<TreeviewSelect>>', self.on_order_item_select)
    
    def on_customer_select(self, event):
        """
        Обработчик выбора покупателя из списка.
        
        Parameters
        ----------
        event : tk.Event
            Событие выбора
        """
        selection = self.customer_listbox.curselection()
        if selection:
            self.selected_customer_index = selection[0]
            self.last_customer_selection = self.selected_customer_index
            self.update_customer_info()
    
    def on_product_select(self, event):
        """
        Обработчик выбора товара из списка.
        
        Parameters
        ----------
        event : tk.Event
            Событие выбора
        """
        selection = self.product_listbox.curselection()
        if selection:
            self.selected_product_index = selection[0]
            self.last_product_selection = self.selected_product_index
            self.update_product_price()
    
    def on_order_item_select(self, event):
        """
        Обработчик выбора товара в таблице заказа.
        
        Parameters
        ----------
        event : tk.Event
            Событие выбора
        """
        selection = self.order_tree.selection()
        if selection:
            self.selected_order_item_index = self.order_tree.index(selection[0])
        else:
            self.selected_order_item_index = -1
    
    def calculate_sum(self, event=None):
        """
        Расчет суммы для выбранного товара и количества.
        
        Parameters
        ----------
        event : tk.Event, optional
            Событие изменения (по умолчанию None)
        """
        try:
            quantity = int(self.quantity_spinbox.get())
            if self.selected_product_index >= 0 and self.filtered_products:
                price = float(self.filtered_products[self.selected_product_index]['price'])
                total = quantity * price
                self.sum_label.config(text=f"{total:.2f} руб.")
        except ValueError:
            self.sum_label.config(text="0.00 руб.")
    
    def add_product_to_order(self):
        """Добавление товара в текущий заказ."""
        try:
            if self.selected_customer_index < 0:
                messagebox.showerror("Ошибка", "Выберите покупателя!")
                return
            
            if self.selected_product_index < 0:
                messagebox.showerror("Ошибка", "Выберите товар!")
                return
            
            quantity = int(self.quantity_spinbox.get())
            if quantity <= 0:
                messagebox.showerror("Ошибка", "Количество должно быть больше 0!")
                return
            
            product = self.filtered_products[self.selected_product_index]
            price = float(product['price'])
            total = quantity * price
            
            # Добавление в таблицу
            self.order_tree.insert('', 'end', values=(
                product['name'],
                quantity,
                product['unit'],
                f"{price:.2f} руб.",
                f"{total:.2f} руб."
            ))
            
            # Добавление во внутренний список
            self.order_items.append({
                'product_id': product['id'],
                'product_name': product['name'],
                'quantity': quantity,
                'unit': product['unit'],
                'price': price,
                'total': total
            })
            
            # Обновление общей суммы
            self.current_order_total += total
            self.total_label.config(text=f"Общая сумма: {self.current_order_total:.2f} руб.")
            
            # Сброс количества
            self.quantity_spinbox.delete(0, 'end')
            self.quantity_spinbox.insert(0, '1')
            self.calculate_sum()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных данных!")
    
    def remove_product_from_order(self):
        """Удаление товара из текущего заказа."""
        if self.selected_order_item_index < 0:
            messagebox.showerror("Ошибка", "Выберите товар для удаления!")
            return
        
        selected_item = self.order_tree.selection()
        if not selected_item:
            return
        
        if 0 <= self.selected_order_item_index < len(self.order_items):
            item_to_remove = self.order_items[self.selected_order_item_index]
            total_to_remove = item_to_remove['total']
            
            self.order_tree.delete(selected_item)
            self.order_items.pop(self.selected_order_item_index)
            
            self.current_order_total -= total_to_remove
            self.total_label.config(text=f"Общая сумма: {self.current_order_total:.2f} руб.")
            
            self.selected_order_item_index = -1
    
    def create_order(self):
        """Создание и сохранение заказа."""
        if not self.order_items:
            messagebox.showerror("Ошибка", "Добавьте товары в заказ!")
            return
        
        if self.selected_customer_index < 0:
            messagebox.showerror("Ошибка", "Выберите покупателя!")
            return
        
        try:
            customer = self.filtered_customers[self.selected_customer_index]
            customer_info = f"{customer['last_name']} {customer['first_name']} {customer['middle_name']} - {customer['phone']} - {customer['email']}"
            
            if self.order_model.create_order(customer['id'], self.current_order_total, customer_info, self.order_items):
                messagebox.showinfo("Успех", "Заказ успешно создан и сохранен!")
                
                # Очистка формы
                self.order_tree.delete(*self.order_tree.get_children())
                self.order_items = []
                self.current_order_total = 0
                self.total_label.config(text=f"Общая сумма: {self.current_order_total:.2f}")
                
                self.refresh_history()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать заказ!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении заказа: {str(e)}")
    
    def init_history_tab(self):
        """Инициализация вкладки истории заказов."""
        frame = ttk.Frame(self.tab_history)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Фрейм сортировки
        sort_frame = ttk.Frame(frame)
        sort_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(sort_frame, text="Сортировать по:").pack(side='left', padx=5)
        
        self.sort_var = tk.StringVar(value='дате')
        sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var, 
                                 values=['дате', 'сумме'], state='readonly', width=10)
        sort_combo.pack(side='left', padx=5)
        
        self.sort_order_var = tk.StringVar(value='возрастанию')
        sort_order_combo = ttk.Combobox(sort_frame, textvariable=self.sort_order_var, 
                                       values=['возрастанию', 'убыванию'], state='readonly', width=12)
        sort_order_combo.pack(side='left', padx=5)
        
        sort_button = ttk.Button(sort_frame, text="Применить сортировку", command=self.apply_sorting)
        sort_button.pack(side='left', padx=5)
        
        # Таблица истории заказов
        table_container = ttk.Frame(frame)
        table_container.pack(fill='both', expand=True)
        
        columns_config = [
            ('id', 'ID заказа', 5),
            ('customer_info', 'Покупатель', 300),
            ('total_amount', 'Сумма', 100),
            ('order_date', 'Дата заказа', 150)
        ]
        
        self.history_tree = self._create_treeview(table_container, columns_config)
        self.history_tree.column('id', anchor='center')
        self.history_tree.column('total_amount', anchor='center')
        self.history_tree.column('order_date', anchor='center')
        self.history_tree.bind("<Double-1>", self.open_order_details)
        
        self.refresh_history()
    
    def apply_sorting(self):
        """Применение сортировки к истории заказов."""
        sort_mapping = {'дате': 'date', 'сумме': 'amount', 'ID': 'id'}
        order_mapping = {'возрастанию': True, 'убыванию': False}
        
        sort_by = sort_mapping.get(self.sort_var.get(), 'date')
        ascending = order_mapping.get(self.sort_order_var.get(), True)
        
        sorted_orders = self.order_model.sort_orders(sort_by, ascending)
        
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        for order in sorted_orders:
            self.history_tree.insert('', 'end', values=(
                order['id'],
                order['customer_info'],
                order['total_amount'],
                order['order_date']
            ))
    
    def open_order_details(self, event):
        """
        Открытие окна с деталями заказа.
        
        Parameters
        ----------
        event : tk.Event
            Событие двойного клика
        """
        selection = self.history_tree.selection()
        if not selection:
            return
            
        item = self.history_tree.item(selection[0])
        values = item['values']
        
        if not values or len(values) < 4:
            return
            
        order_id = str(values[0])
        order_details = self.order_model.find_by_id(order_id)
        
        if order_details is None:
            messagebox.showerror("Ошибка", f"Заказ с ID {order_id} не найден!")
            return
            
        details_window = tk.Toplevel(self.root)
        details_window.title(f'Детали заказа №{order_id}')
        details_window.geometry("700x500")
        
        # Центрирование окна
        details_window.update_idletasks()
        width = details_window.winfo_width()
        height = details_window.winfo_height()
        x = (details_window.winfo_screenwidth() // 2) - (width // 2)
        y = (details_window.winfo_screenheight() // 2) - (height // 2)
        details_window.geometry(f"{width}x{height}+{x}+{y}")
        
        main_frame = ttk.Frame(details_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Информация о заказе
        info_frame = ttk.LabelFrame(main_frame, text="Информация о заказе")
        info_frame.pack(fill='x', pady=(0, 10))
        
        info_texts = [
            f"ID заказа: {order_details['id']}",
            f"Покупатель: {order_details['customer_info']}",
            f"Дата заказа: {order_details['order_date']}",
            f"Общая сумма: {order_details['total_amount']} руб."
        ]
        
        for text in info_texts:
            ttk.Label(info_frame, text=text).pack(anchor='w', padx=5, pady=2)
        
        # Товары в заказе
        items_frame = ttk.LabelFrame(main_frame, text="Товары в заказе")
        items_frame.pack(fill='both', expand=True)
        
        columns_config = [
            ('product', 'Товар', 200),
            ('quantity', 'Количество', 80),
            ('unit', 'Ед. изм.', 80),
            ('price', 'Цена', 100),
            ('total', 'Сумма', 100)
        ]
        
        items_tree = self._create_treeview(items_frame, columns_config, height=8)
        
        items_tree.column('quantity', anchor='center')
        items_tree.column('unit', anchor='center')
        items_tree.column('price', anchor='center')
        items_tree.column('total', anchor='center')
        
        order_items = self.order_model.get_order_items(order_id)
        
        for item in order_items:
            product = self.product_model.find_by_id(item['product_id'])
            product_name = product['name'] if product else "Неизвестный товар"
            product_unit = product['unit'] if product else "шт."
            
            items_tree.insert('', 'end', values=(
                product_name,
                item['quantity'],
                product_unit,
                f"{float(item['price']):.2f} руб.",
                f"{float(item['total']):.2f} руб."
            ))
        
        # Кнопка закрытия
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Закрыть", command=details_window.destroy).pack()
        
    def refresh_history(self):
        """Обновление истории заказов в таблице."""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        orders = self.order_model.get_all()
        orders.sort(key=lambda x: x['order_date'], reverse=False)
        
        for order in orders:
            self.history_tree.insert('', 'end', values=(
                order['id'],
                order['customer_info'],
                order['total_amount'],
                order['order_date']
            ))
    
    def init_products_tab(self):
        """Инициализация вкладки управления товарами."""
        frame = ttk.Frame(self.tab_products)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Кнопки импорта/экспорта
        import_export_frame = ttk.Frame(frame)
        import_export_frame.pack(fill='x', pady=(0, 10))
        
        buttons_config = [
            ("Экспорт данных", self.export_products),
            ("Импорт данных", self.import_products)
        ]
        
        for text, command in buttons_config:
            ttk.Button(import_export_frame, text=text, command=command).pack(side='left', padx=5)
        
        # Форма добавления товара
        add_frame = ttk.LabelFrame(frame, text="Управление товарами")
        add_frame.pack(fill='x', pady=5)
        
        labels = ["Название:", "Цена:", "Ед. изм.:"]
        entries = []
        
        for i, label_text in enumerate(labels):
            ttk.Label(add_frame, text=label_text).grid(row=0, column=i*2, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(add_frame, width=20 if i == 0 else 10)
            entry.grid(row=0, column=i*2+1, padx=5, pady=5)
            entries.append(entry)
        
        self.product_name_entry, self.product_price_entry, self.product_unit_entry = entries
        
        ttk.Button(add_frame, text="Добавить", command=self.add_product).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(add_frame, text="Удалить товар", command=self.delete_product).grid(row=0, column=7, padx=5, pady=5)
        
        # Таблица товаров
        table_container = ttk.Frame(frame)
        table_container.pack(fill='both', expand=True, pady=5)
        
        columns_config = [
            ('id', 'ID', 5),
            ('name', 'Название', 250),
            ('price', 'Цена', 100),
            ('unit', 'Ед. изм.', 80)
        ]
        
        self.products_tree = self._create_treeview(table_container, columns_config)
        self.products_tree.bind('<<TreeviewSelect>>', self.on_product_select_in_table)
        
        self.refresh_products()
    
    def export_products(self):
        """Экспорт товаров с выбором формата (CSV/JSON)."""
        if not self.product_model.get_all():
            messagebox.showwarning("Предупреждение", "Нет товаров для экспорта!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ],
            title="Экспорт товаров"
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self._export_csv(self.product_model.get_all(), file_path, ['id', 'name', 'price', 'unit'])
                    messagebox.showinfo("Успех", "Товары успешно экспортированы в CSV!")
                elif file_path.endswith('.json'):
                    self._export_json(self.product_model.get_all(), file_path)
                    messagebox.showinfo("Успех", "Товары успешно экспортированы в JSON!")
                else:
                    messagebox.showerror("Ошибка", "Неподдерживаемый формат файла!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")
    
    def import_products(self):
        """Импорт товаров с выбором формата (CSV/JSON)."""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ],
            title="Импорт товаров"
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    imported_data = self._import_csv(file_path)
                    required_fields = ['name', 'price', 'unit']
                elif file_path.endswith('.json'):
                    imported_data = self._import_json(file_path)
                    required_fields = ['name', 'price', 'unit']
                else:
                    messagebox.showerror("Ошибка", "Неподдерживаемый формат файла!")
                    return
                
                if not imported_data:
                    messagebox.showwarning("Предупреждение", "Файл не содержит данных!")
                    return
                
                for item in imported_data:
                    for field in required_fields:
                        if field not in item:
                            messagebox.showerror("Ошибка", f"В файле отсутствует обязательное поле: {field}")
                            return
                
                success_count = 0
                for item in imported_data:
                    if self.product_model.add_item(item):
                        success_count += 1
                
                messagebox.showinfo("Успех", f"Успешно импортировано {success_count} товаров!")
                self._refresh_data()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при импорте: {str(e)}")
    
    def on_product_select_in_table(self, event):
        """
        Обработчик выбора товара в таблице.
        
        Parameters
        ----------
        event : tk.Event
            Событие выбора
        """
        selection = self.products_tree.selection()
        self.selected_product_in_table = selection[0] if selection else None
    
    def delete_product(self):
        """Удаление выбранного товара."""
        if not self.selected_product_in_table:
            messagebox.showerror("Ошибка", "Выберите товар для удаления!")
            return
        
        item_data = self.products_tree.item(self.selected_product_in_table)
        product_id = item_data['values'][0]
        product_name = item_data['values'][1]
        
        result = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить товар '{product_name}'?")
        
        if result and self.product_model.delete_item(product_id):
            messagebox.showinfo("Успех", "Товар успешно удален!")
            self._refresh_data()
            self.selected_product_in_table = None
    
    def add_product(self):
        """Добавление нового товара."""
        product_data = {
            'name': self.product_name_entry.get().strip(),
            'price': self.product_price_entry.get().strip(),
            'unit': self.product_unit_entry.get().strip()
        }
        
        self._validate_and_add(
            self.product_model.add_item,
            product_data,
            "Товар успешно добавлен!",
            [self.product_name_entry, self.product_price_entry, self.product_unit_entry]
        )
    
    def refresh_products(self):
        """Обновление таблицы товаров."""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        self.selected_product_in_table = None
        
        for product in self.product_model.get_all():
            self.products_tree.insert('', 'end', values=(
                product['id'],
                product['name'],
                product['price'],
                product['unit']
            ))
    
    def export_products_csv(self):
        """Экспорт товаров в CSV формат."""
        self._export_data(
            self.product_model.get_all(),
            [("CSV files", "*.csv"), ("All files", "*.*")],
            "Сохранить товары как CSV",
            lambda data, path: self._export_csv(data, path, ['id', 'name', 'price', 'unit'])
        )
    
    def import_products_csv(self):
        """Импорт товаров из CSV файла."""
        self._import_data(
            [("CSV files", "*.csv"), ("All files", "*.*")],
            "Выберите CSV файл для импорта товаров",
            self._import_csv,
            ['name', 'price', 'unit'],
            "Успешно импортировано {} товаров!",
            self.product_model.add_item
        )
    
    def export_products_json(self):
        """Экспорт товаров в JSON формат."""
        self._export_data(
            self.product_model.get_all(),
            [("JSON files", "*.json"), ("All files", "*.*")],
            "Сохранить товары как JSON",
            self._export_json
        )
    
    def import_products_json(self):
        """Импорт товаров из JSON файла."""
        self._import_data(
            [("JSON files", "*.json"), ("All files", "*.*")],
            "Выберите JSON файл для импорта товаров",
            self._import_json,
            ['name', 'price', 'unit'],
            "Успешно импортировано {} товаров!",
            self.product_model.add_item
        )
    
    def init_customers_tab(self):
        """Инициализация вкладки управления покупателями."""
        frame = ttk.Frame(self.tab_customers)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Кнопки импорта/экспорта
        import_export_frame = ttk.Frame(frame)
        import_export_frame.pack(fill='x', pady=(0, 10))
        
        buttons_config = [
            ("Экспорт данных", self.export_customers),
            ("Импорт данных", self.import_customers)
        ]
        
        for text, command in buttons_config:
            ttk.Button(import_export_frame, text=text, command=command).pack(side='left', padx=5)
        
        # Форма добавления покупателя
        add_frame = ttk.LabelFrame(frame, text="Управление покупателями")
        add_frame.pack(fill='x', pady=5)
        
        labels_row1 = ["Фамилия:", "Имя:", "Отчество:"]
        entries_row1 = []
        
        for i, label_text in enumerate(labels_row1):
            ttk.Label(add_frame, text=label_text).grid(row=0, column=i*2, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(add_frame, width=20)
            entry.grid(row=0, column=i*2+1, padx=5, pady=5)
            entries_row1.append(entry)
        
        labels_row2 = ["Телефон:", "Email:"]
        entries_row2 = []
        
        for i, label_text in enumerate(labels_row2):
            ttk.Label(add_frame, text=label_text).grid(row=1, column=i*2, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(add_frame, width=20)
            entry.grid(row=1, column=i*2+1, padx=5, pady=5)
            entries_row2.append(entry)
        
        self.last_name_entry, self.first_name_entry, self.middle_name_entry = entries_row1
        self.phone_entry, self.email_entry = entries_row2
        
        ttk.Button(add_frame, text="Добавить", command=self.add_customer).grid(row=1, column=4, padx=5, pady=5)
        ttk.Button(add_frame, text="Удалить покупателя", command=self.delete_customer).grid(row=1, column=5, padx=5, pady=5)
        
        # Таблица покупателей
        table_container = ttk.Frame(frame)
        table_container.pack(fill='both', expand=True, pady=5)
        
        columns_config = [
            ('id', 'ID', 5),
            ('last_name', 'Фамилия', 100),
            ('first_name', 'Имя', 100),
            ('middle_name', 'Отчество', 100),
            ('phone', 'Телефон', 150),
            ('email', 'Email', 150)
        ]
        
        self.customers_tree = self._create_treeview(table_container, columns_config)
        self.customers_tree.bind('<<TreeviewSelect>>', self.on_customer_select_in_table)
        
        self.refresh_customers()
    
    def export_customers(self):
        """Экспорт покупателей с выбором формата (CSV/JSON)."""
        if not self.customer_model.get_all():
            messagebox.showwarning("Предупреждение", "Нет покупателей для экспорта!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ],
            title="Экспорт покупателей"
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self._export_csv(self.customer_model.get_all(), file_path, 
                                   ['id', 'last_name', 'first_name', 'middle_name', 'phone', 'email'])
                    messagebox.showinfo("Успех", "Покупатели успешно экспортированы в CSV!")
                elif file_path.endswith('.json'):
                    self._export_json(self.customer_model.get_all(), file_path)
                    messagebox.showinfo("Успех", "Покупатели успешно экспортированы в JSON!")
                else:
                    messagebox.showerror("Ошибка", "Неподдерживаемый формат файла!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")
    
    def import_customers(self):
        """Импорт покупателей с выбором формата (CSV/JSON)."""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ],
            title="Импорт покупателей"
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    imported_data = self._import_csv(file_path)
                    required_fields = ['last_name', 'first_name', 'phone']
                elif file_path.endswith('.json'):
                    imported_data = self._import_json(file_path)
                    required_fields = ['last_name', 'first_name', 'phone']
                else:
                    messagebox.showerror("Ошибка", "Неподдерживаемый формат файла!")
                    return
                
                if not imported_data:
                    messagebox.showwarning("Предупреждение", "Файл не содержит данных!")
                    return
                
                for item in imported_data:
                    for field in required_fields:
                        if field not in item:
                            messagebox.showerror("Ошибка", f"В файле отсутствует обязательное поле: {field}")
                            return
                
                success_count = 0
                for item in imported_data:
                    if self.customer_model.add_item(item):
                        success_count += 1
                
                messagebox.showinfo("Успех", f"Успешно импортировано {success_count} покупателей!")
                self._refresh_data()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при импорте: {str(e)}")
        self.refresh_customers()
    
    def on_customer_select_in_table(self, event):
        """
        Обработчик выбора покупателя в таблице.
        
        Parameters
        ----------
        event : tk.Event
            Событие выбора
        """
        selection = self.customers_tree.selection()
        self.selected_customer_in_table = selection[0] if selection else None
    
    def delete_customer(self):
        """Удаление выбранного покупателя."""
        if not self.selected_customer_in_table:
            messagebox.showerror("Ошибка", "Выберите покупателя для удаления!")
            return
        
        item_data = self.customers_tree.item(self.selected_customer_in_table)
        customer_id = item_data['values'][0]
        last_name = item_data['values'][1]
        first_name = item_data['values'][2]
        
        # Проверка наличия заказов у покупателя
        customer_orders = [order for order in self.order_model.data if order['customer_id'] == customer_id]
        
        if customer_orders:
            messagebox.showerror("Ошибка", 
                               "Нельзя удалить покупателя, у которого есть заказы!\n"
                               f"Найдено заказов: {len(customer_orders)}")
            return
        
        result = messagebox.askyesno("Подтверждение", 
                                   f"Вы уверены, что хотите удалить покупателя '{last_name} {first_name}'?")
        
        if result and self.customer_model.delete_item(customer_id):
            messagebox.showinfo("Успех", "Покупатель успешно удален!")
            self._refresh_data()
            self.selected_customer_in_table = None
    
    def add_customer(self):
        """Добавление нового покупателя."""
        customer_data = {
            'last_name': self.last_name_entry.get().strip(),
            'first_name': self.first_name_entry.get().strip(),
            'middle_name': self.middle_name_entry.get().strip(),
            'phone': self.phone_entry.get().strip(),
            'email': self.email_entry.get().strip()
        }
        
        self._validate_and_add(
            self.customer_model.add_item,
            customer_data,
            "Покупатель успешно добавлен!",
            [self.last_name_entry, self.first_name_entry, self.middle_name_entry, self.phone_entry, self.email_entry]
        )
    
    def refresh_customers(self):
        """Обновление таблицы покупателей."""
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        self.selected_customer_in_table = None
        
        for customer in self.customer_model.get_all():
            self.customers_tree.insert('', 'end', values=(
                customer['id'],
                customer['last_name'],
                customer['first_name'],
                customer['middle_name'],
                customer['phone'],
                customer['email']
            ))
    
    def export_customers_csv(self):
        """Экспорт покупателей в CSV формат."""
        self._export_data(
            self.customer_model.get_all(),
            [("CSV files", "*.csv"), ("All files", "*.*")],
            "Сохранить покупателей как CSV",
            lambda data, path: self._export_csv(data, path, ['id', 'last_name', 'first_name', 'middle_name', 'phone', 'email'])
        )
    
    def import_customers_csv(self):
        """Импорт покупателей из CSV файла."""
        self._import_data(
            [("CSV files", "*.csv"), ("All files", "*.*")],
            "Выберите CSV файл для импорта покупателей",
            self._import_csv,
            ['last_name', 'first_name', 'phone'],
            "Успешно импортировано {} покупателей!",
            self.customer_model.add_item
        )
    
    def export_customers_json(self):
        """Экспорт покупателей в JSON формат."""
        self._export_data(
            self.customer_model.get_all(),
            [("JSON files", "*.json"), ("All files", "*.*")],
            "Сохранить покупателей как JSON",
            self._export_json
        )
    
    def import_customers_json(self):
        """Импорт покупателей из JSON файла."""
        self._import_data(
            [("JSON files", "*.json"), ("All files", "*.*")],
            "Выберите JSON файл для импорта покупателей",
            self._import_json,
            ['last_name', 'first_name', 'phone'],
            "Успешно импортировано {} покупателей!",
            self.customer_model.add_item
        )
    
    def init_analytics_tab(self):
        """Инициализация вкладки аналитики и визуализации."""
        main_frame = ttk.Frame(self.tab_analytics)
        main_frame.pack(fill='both', expand=True)
        
        scrollable_frame = self._create_scrollable_frame(main_frame)
        
        # Кнопки для управления графиками
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill='x', pady=(10, 5), padx=10)
        
        buttons_config = [
            ("Топ 5 клиентов", self.show_top_customers),
            ("Динамика заказов", self.show_orders_dynamics),
            ("Граф связей", self.show_customer_network),
            ("Обновить все", self.update_all_charts)
        ]
        
        for text, command in buttons_config:
            ttk.Button(button_frame, text=text, command=command).pack(side='left', padx=5)
        
        # Фрейм для отображения графиков
        self.chart_frame = ttk.Frame(scrollable_frame)
        self.chart_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.init_empty_charts()
    
    def init_empty_charts(self):
        """Инициализация пустых графиков с заглушками."""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        chart_frames = [
            ("Топ 5 клиентов", 400),
            ("Динамика заказов", 400),
            ("Граф связей клиентов", 500)
        ]
        
        self.chart_frames = {}
        
        for title, height in chart_frames:
            frame = ttk.LabelFrame(self.chart_frame, text=title, height=height)
            frame.pack(fill='x', pady=5, padx=5)
            frame.pack_propagate(False)
            
            ttk.Label(frame, text=f"Нажмите '{title}' для отображения графика", 
                     font=('Arial', 12)).pack(expand=True)
            
            self.chart_frames[title] = frame
    
    def update_all_charts(self):
        """Обновление всех графиков аналитики."""
        self.show_top_customers()
        self.show_orders_dynamics()
        self.show_customer_network()
    
    def show_top_customers(self):
        """Отображение графика топ-5 клиентов по сумме заказов."""
        self.analyzer.show_top_customers(self.chart_frames["Топ 5 клиентов"])
    
    def show_orders_dynamics(self):
        """Отображение графика динамики заказов по времени."""
        self.analyzer.show_orders_dynamics(self.chart_frames["Динамика заказов"])
    
    def show_customer_network(self):
        """Отображение графа связей между клиентами."""
        self.analyzer.show_customer_network(self.chart_frames["Граф связей клиентов"])

if __name__ == "__main__":
    """
    Точка входа в приложение.
    
    Создает главное окно приложения и запускает основной цикл обработки событий.
    """
    root = tk.Tk()
    app = OrderApp(root)
    root.mainloop()