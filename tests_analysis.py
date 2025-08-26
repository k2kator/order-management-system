import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

# Добавляем путь к проекту для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock для Tkinter компонентов
class MockTkinter:
    """
    Mock-класс для замены Tkinter компонентов в тестах.
    
    Attributes
    ----------
    Frame : class
        Mock-класс для фрейма Tkinter.
    """
    
    class Frame:
        """
        Mock-класс для фрейма Tkinter.
        
        Attributes
        ----------
        children : list
            Список дочерних элементов фрейма.
        """
        
        def __init__(self, *args, **kwargs):
            """
            Инициализация mock-фрейма.
            
            Parameters
            ----------
            *args : tuple
                Позиционные аргументы.
            **kwargs : dict
                Именованные аргументы.
            """
            self.children = []
        
        def winfo_children(self):
            """
            Возвращает дочерние элементы фрейма.
            
            Returns
            -------
            list
                Список дочерних элементов.
            """
            return self.children
        
        def destroy(self):
            """
            Очищает список дочерних элементов.
            """
            self.children = []

# Подменяем Tkinter компоненты перед импортом анализатора
import analysis
analysis.ttk = MagicMock()
analysis.FigureCanvasTkAgg = MagicMock()

from analysis import DataAnalyzer


class TestDataAnalyzer(unittest.TestCase):
    """
    Тесты для класса DataAnalyzer.
    
    Methods
    -------
    setUp()
        Подготовка тестового окружения для DataAnalyzer.
    tearDown()
        Очистка после тестов.
    test_init()
        Тестирование инициализации DataAnalyzer.
    test_show_top_customers_success()
        Тестирование успешного отображения топ клиентов.
    test_show_top_customers_no_data()
        Тестирование отображения топ клиентов при отсутствии данных.
    test_show_orders_dynamics_success()
        Тестирование успешного отображения динамики заказов.
    test_show_orders_dynamics_no_data()
        Тестирование отображения динамики заказов при отсутствии данных.
    test_show_customer_network_success()
        Тестирование успешного построения графа связей клиентов.
    test_show_customer_network_no_data()
        Тестирование построения графа связей при отсутствии данных.
    test_show_customer_network_no_connections()
        Тестирование построения графа связей при отсутствии связей между клиентами.
    test_show_top_customers_exception_handling()
        Тестирование обработки исключений в show_top_customers.
    test_show_orders_dynamics_exception_handling()
        Тестирование обработки исключений в show_orders_dynamics.
    test_show_customer_network_exception_handling()
        Тестирование обработки исключений в show_customer_network.
    """
    
    def setUp(self):
        """
        Подготовка тестового окружения для DataAnalyzer.
        
        Инициализирует mock-модели и настраивает тестовое окружение.
        """
        # Создаем mock-модели
        self.mock_customer_model = MagicMock()
        self.mock_product_model = MagicMock()
        self.mock_order_model = MagicMock()
        
        # Mock для order_items_model
        self.mock_order_items_model = MagicMock()
        self.mock_order_model.order_items_model = self.mock_order_items_model
        
        # Создаем экземпляр анализатора
        self.analyzer = DataAnalyzer(
            self.mock_customer_model,
            self.mock_product_model,
            self.mock_order_model
        )
        
        # Mock для родительского фрейма
        self.mock_parent_frame = MagicMock()
        self.mock_parent_frame.winfo_children.return_value = []
        
        # Mock для FigureCanvasTkAgg
        self.mock_canvas = MagicMock()
        analysis.FigureCanvasTkAgg.return_value = self.mock_canvas
        
        # Сбрасываем все mock-вызовы перед каждым тестом
        self.mock_customer_model.reset_mock()
        self.mock_product_model.reset_mock()
        self.mock_order_model.reset_mock()
        self.mock_order_items_model.reset_mock()
        self.mock_parent_frame.reset_mock()
        self.mock_canvas.reset_mock()
        analysis.ttk.Label.reset_mock()
        analysis.FigureCanvasTkAgg.reset_mock()
    
    def tearDown(self):
        """
        Очистка после тестов.
        
        Закрывает все открытые графики matplotlib.
        """
        plt.close('all')
    
    def test_init(self):
        """
        Тестирование инициализации DataAnalyzer.
        
        Проверяет, что модели корректно присваиваются атрибутам анализатора.
        """
        self.assertEqual(self.analyzer.customer_model, self.mock_customer_model)
        self.assertEqual(self.analyzer.product_model, self.mock_product_model)
        self.assertEqual(self.analyzer.order_model, self.mock_order_model)
    
    @patch('analysis.pd.DataFrame')
    @patch('analysis.plt.subplots')
    def test_show_top_customers_success(self, mock_subplots, mock_dataframe):
        """
        Тестирование успешного отображения топ клиентов.
        
        Parameters
        ----------
        mock_subplots : MagicMock
            Mock для функции plt.subplots.
        mock_dataframe : MagicMock
            Mock для функции pd.DataFrame.
        """
        # Mock данные
        mock_orders_df = MagicMock()
        mock_orders_df.empty = False
        
        # Mock value_counts
        value_counts_mock = MagicMock()
        value_counts_mock.head.return_value = pd.Series([4, 2, 1], index=['1', '2', '3'])
        mock_orders_df.__getitem__.return_value.value_counts.return_value = value_counts_mock
        
        mock_customers_df = MagicMock()
        mock_customers_df.empty = False
        
        # Mock iloc[0] для customer
        mock_customer = MagicMock()
        mock_customer.__getitem__.side_effect = lambda x: {
            'last_name': 'Иванов',
            'first_name': 'Иван',
            'middle_name': 'Иванович'
        }[x]
        
        mock_customers_df.__getitem__.return_value.__eq__.return_value.iloc.__getitem__.return_value = mock_customer
        
        mock_dataframe.side_effect = [mock_orders_df, mock_customers_df]
        
        # Mock matplotlib
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        # Вызов метода
        self.analyzer.show_top_customers(self.mock_parent_frame)
        
        # Проверки
        self.mock_parent_frame.winfo_children.assert_called()
        mock_dataframe.assert_has_calls([
            call(self.mock_order_model.data),
            call(self.mock_customer_model.data)
        ])
        mock_subplots.assert_called_once_with(figsize=(10, 5))
        self.mock_canvas.draw.assert_called_once()
        self.mock_canvas.get_tk_widget.assert_called_once()
    
    @patch('analysis.pd.DataFrame')
    def test_show_top_customers_no_data(self, mock_dataframe):
        """
        Тестирование отображения топ клиентов при отсутствии данных.
        
        Parameters
        ----------
        mock_dataframe : MagicMock
            Mock для функции pd.DataFrame.
        """
        # Mock пустые данные
        mock_df = MagicMock()
        mock_df.empty = True
        mock_dataframe.return_value = mock_df
        
        # Вызов метода
        self.analyzer.show_top_customers(self.mock_parent_frame)
        
        # Проверка, что создается label с сообщением об отсутствии данных
        analysis.ttk.Label.assert_called_once_with(
            self.mock_parent_frame, 
            text="Недостаточно данных для анализа", 
            font=('Arial', 12)
        )
        analysis.ttk.Label.return_value.pack.assert_called_once_with(expand=True)
    
    @patch('analysis.plt.subplots')
    def test_show_orders_dynamics_success(self, mock_subplots):
        """
        Тестирование успешного отображения динамики заказов.
        
        Parameters
        ----------
        mock_subplots : MagicMock
            Mock для функции plt.subplots.
        """
        # Создаем реальные тестовые данные
        test_orders_data = [
            {'id': '1', 'order_date': '2024-01-01 10:00:00', 'customer_id': '1'},
            {'id': '2', 'order_date': '2024-01-01 14:00:00', 'customer_id': '2'},
            {'id': '3', 'order_date': '2024-01-02 11:00:00', 'customer_id': '1'}
        ]
        
        self.mock_order_model.data = test_orders_data
        
        # Mock matplotlib
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        # Вызов метода
        self.analyzer.show_orders_dynamics(self.mock_parent_frame)
        
        # Проверки - теперь pd.DataFrame вызывается внутри метода, но мы не можем точно проверить количество вызовов
        # Вместо этого проверяем, что график был создан и отрисован
        mock_subplots.assert_called_once_with(figsize=(10, 5))
        self.mock_canvas.draw.assert_called_once()
        self.mock_canvas.get_tk_widget.assert_called_once()
    
    @patch('analysis.pd.DataFrame')
    def test_show_orders_dynamics_no_data(self, mock_dataframe):
        """
        Тестирование отображения динамики заказов при отсутствии данных.
        
        Parameters
        ----------
        mock_dataframe : MagicMock
            Mock для функции pd.DataFrame.
        """
        # Mock пустые данные
        mock_df = MagicMock()
        mock_df.empty = True
        mock_dataframe.return_value = mock_df
        
        # Вызов метода
        self.analyzer.show_orders_dynamics(self.mock_parent_frame)
        
        # Проверка сообщения об отсутствии данных
        analysis.ttk.Label.assert_called_once_with(
            self.mock_parent_frame,
            text="Недостаточно данных для анализа", 
            font=('Arial', 12)
        )
        analysis.ttk.Label.return_value.pack.assert_called_once_with(expand=True)
    
    @patch('analysis.nx.Graph')
    @patch('analysis.plt.subplots')
    def test_show_customer_network_success(self, mock_subplots, mock_graph):
        """
        Тестирование успешного построения графа связей клиентов.
        
        Parameters
        ----------
        mock_subplots : MagicMock
            Mock для функции plt.subplots.
        mock_graph : MagicMock
            Mock для функции nx.Graph.
        """
        # Mock данные
        self.mock_order_model.data = [{'id': '1', 'customer_id': '1'}]
        self.mock_order_items_model.data = [{'id': '1', 'order_id': '1', 'product_id': '1'}]
        self.mock_customer_model.data = [{'id': '1', 'last_name': 'Иванов', 'first_name': 'Иван', 'middle_name': 'Иванович'}]
        
        # Mock graph
        mock_G = MagicMock()
        mock_graph.return_value = mock_G
        mock_G.edges.return_value = [('1', '2')]  # Есть связи
        
        # Mock для spring_layout и других методов NetworkX
        mock_pos = {'1': (0, 0), '2': (1, 1)}
        mock_G.nodes.return_value = ['1', '2']
        mock_G.degree.side_effect = lambda node: 1 if node == '1' else 1
        mock_G.edges.return_value = [('1', '2')]
        
        # Mock для NetworkX методов рисования
        with patch('analysis.nx.draw_networkx_nodes'), \
             patch('analysis.nx.draw_networkx_edges'), \
             patch('analysis.nx.draw_networkx_labels'), \
             patch('analysis.nx.draw_networkx_edge_labels'), \
             patch('analysis.nx.spring_layout', return_value=mock_pos):
            
            # Mock matplotlib
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            # Вызов метода
            self.analyzer.show_customer_network(self.mock_parent_frame)
            
            # Проверки
            mock_graph.assert_called_once()
            mock_subplots.assert_called_once_with(figsize=(10, 6))
            self.mock_canvas.draw.assert_called_once()
    
    def test_show_customer_network_no_data(self):
        """
        Тестирование построения графа связей при отсутствии данных.
        """
        # Пустые данные
        self.mock_order_model.data = []
        self.mock_order_items_model.data = []
        self.mock_customer_model.data = []
        
        # Вызов метода
        self.analyzer.show_customer_network(self.mock_parent_frame)
        
        # Проверка сообщения об отсутствии данных
        analysis.ttk.Label.assert_called_once_with(
            self.mock_parent_frame,
            text="Недостаточно данных для анализа", 
            font=('Arial', 12)
        )
        analysis.ttk.Label.return_value.pack.assert_called_once_with(expand=True)
    
    @patch('analysis.nx.Graph')
    def test_show_customer_network_no_connections(self, mock_graph):
        """
        Тестирование построения графа связей при отсутствии связей между клиентами.
        
        Parameters
        ----------
        mock_graph : MagicMock
            Mock для функции nx.Graph.
        """
        # Mock данные
        self.mock_order_model.data = [{'id': '1', 'customer_id': '1'}]
        self.mock_order_items_model.data = [{'id': '1', 'order_id': '1', 'product_id': '1'}]
        self.mock_customer_model.data = [{'id': '1', 'last_name': 'Иванов', 'first_name': 'Иван', 'middle_name': 'Иванович'}]
        
        # Mock graph без связей
        mock_G = MagicMock()
        mock_graph.return_value = mock_G
        mock_G.edges.return_value = []  # Нет связей
        
        # Вызов метода
        self.analyzer.show_customer_network(self.mock_parent_frame)
        
        # Проверка сообщения об отсутствии связей
        analysis.ttk.Label.assert_called_once_with(
            self.mock_parent_frame,
            text="Нет связей между клиентами", 
            font=('Arial', 12)
        )
        analysis.ttk.Label.return_value.pack.assert_called_once_with(expand=True)
    
    @patch('analysis.pd.DataFrame')
    def test_show_top_customers_exception_handling(self, mock_dataframe):
        """
        Тестирование обработки исключений в show_top_customers.
        
        Parameters
        ----------
        mock_dataframe : MagicMock
            Mock для функции pd.DataFrame.
        """
        # Исключение при создании DataFrame
        mock_dataframe.side_effect = Exception("Test error")
        
        # Вызов метода
        self.analyzer.show_top_customers(self.mock_parent_frame)
        
        # Проверка обработки ошибки
        analysis.ttk.Label.assert_called_once_with(
            self.mock_parent_frame,
            text="Ошибка при создании графика: Test error", 
            font=('Arial', 12)
        )
        analysis.ttk.Label.return_value.pack.assert_called_once_with(expand=True)
    
    def test_show_orders_dynamics_exception_handling(self):
        """
        Тестирование обработки исключений в show_orders_dynamics.
        
        Проверяет обработку ошибок при некорректных данных даты.
        """
        # Создаем данные, которые вызовут исключение при обработке
        test_orders_data = [{'id': '1', 'order_date': 'invalid_date', 'customer_id': '1'}]
        self.mock_order_model.data = test_orders_data
        
        # Вызов метода
        self.analyzer.show_orders_dynamics(self.mock_parent_frame)
        
        # Проверка обработки ошибки
        analysis.ttk.Label.assert_called_once()
        call_args = analysis.ttk.Label.call_args[1]
        self.assertIn('Ошибка при создании графика', call_args['text'])
        analysis.ttk.Label.return_value.pack.assert_called_once_with(expand=True)
    
    def test_show_customer_network_exception_handling(self):
        """
        Тестирование обработки исключений в show_customer_network.
        
        Проверяет обработку ошибок при отсутствии обязательных полей в данных.
        """
        # Исключение при обработке данных
        self.mock_order_model.data = [{'id': '1', 'customer_id': '1'}]
        self.mock_order_items_model.data = [{'id': '1', 'order_id': '1', 'product_id': '1'}]
        
        # Создаем исключение при обращении к middle_name
        mock_customer = {'id': '1', 'last_name': 'Иванов', 'first_name': 'Иван'}
        # Убираем middle_name чтобы вызвать KeyError
        self.mock_customer_model.data = [mock_customer]
        
        # Вызов метода
        self.analyzer.show_customer_network(self.mock_parent_frame)
        
        # Проверка обработки ошибки
        analysis.ttk.Label.assert_called_once()
        call_args = analysis.ttk.Label.call_args[1]
        self.assertIn('Ошибка при создании графика', call_args['text'])
        analysis.ttk.Label.return_value.pack.assert_called_once_with(expand=True)


if __name__ == '__main__':
    """
    Точка входа для запуска unit-тестов.
    
    Запускает все тесты с повышенной детализацией вывода (verbosity=2).
    """
   # Создаем test suite и запускаем с подробным выводом
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDataAnalyzer)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим дополнительную информацию
    print(f"\nТестов запущено: {result.testsRun}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Провалов: {len(result.failures)}")
    print(f"Пропущено: {len(result.skipped)}")