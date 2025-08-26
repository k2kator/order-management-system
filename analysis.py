import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk

class DataAnalyzer:
    """
    Класс для анализа данных и создания визуализаций.
    Обеспечивает построение графиков и диаграмм на основе данных о клиентах, товарах и заказах.
    """
    
    def __init__(self, customer_model, product_model, order_model):
        """
        Инициализация анализатора данных.
        
        Args:
            customer_model: Модель данных клиентов
            product_model: Модель данных товаров
            order_model: Модель данных заказов
        """
        self.customer_model = customer_model
        self.product_model = product_model
        self.order_model = order_model
    
    def show_top_customers(self, parent_frame):
        """
        Отображает топ-5 клиентов по количеству заказов в виде столбчатой диаграммы.
        
        Args:
            parent_frame: Родительский фрейм Tkinter для размещения графика
        """
        # Очистка предыдущего содержимого фрейма
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        try:
            # Преобразование данных в DataFrame для анализа
            orders_df = pd.DataFrame(self.order_model.data)
            customers_df = pd.DataFrame(self.customer_model.data)
            
            # Проверка наличия данных
            if orders_df.empty or customers_df.empty:
                ttk.Label(parent_frame, text="Недостаточно данных для анализа", 
                         font=('Arial', 12)).pack(expand=True)
                return
            
            # Подсчет количества заказов по клиентам (топ-5)
            order_counts = orders_df['customer_id'].value_counts().head(5)
            
            # Формирование списка топ-клиентов с именами и количеством заказов
            top_customers = []
            for customer_id in order_counts.index:
                customer = customers_df[customers_df['id'] == customer_id].iloc[0]
                # Форматирование имени: Фамилия И.О.
                customer_name = f"{customer['last_name']} {customer['first_name'][0]}."
                if pd.notna(customer['middle_name']) and customer['middle_name']:
                    customer_name += f"{customer['middle_name'][0]}."
                top_customers.append({
                    'name': customer_name,
                    'orders': order_counts[customer_id]
                })
            
            # Создание столбчатой диаграммы
            fig, ax = plt.subplots(figsize=(10, 5))
            names = [c['name'] for c in top_customers]
            orders = [c['orders'] for c in top_customers]
            
            bars = ax.bar(names, orders, color=sns.color_palette("husl", len(names)))
            ax.set_title('Топ 5 клиентов по количеству заказов', fontsize=14)
            ax.set_xlabel('Клиенты', fontsize=10)
            ax.set_ylabel('Количество заказов', fontsize=10)
            
            # Добавление числовых значений на столбцы
            for bar, value in zip(bars, orders):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                       f'{value}', ha='center', va='bottom', fontsize=9)
            
            # Настройка отображения подписей
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Встраивание графика в Tkinter интерфейс
            canvas = FigureCanvasTkAgg(fig, parent_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
            plt.close(fig)
            
        except Exception as e:
            # Обработка ошибок при создании графика
            ttk.Label(parent_frame, text=f"Ошибка при создании графика: {str(e)}", 
                     font=('Arial', 12)).pack(expand=True)
    
    def show_orders_dynamics(self, parent_frame):
        """
        Отображает динамику количества заказов по дням в виде линейного графика.
        
        Args:
            parent_frame: Родительский фрейм Tkinter для размещения графика
        """
        # Очистка предыдущего содержимого фрейма
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        try:
            # Преобразование данных заказов в DataFrame
            orders_df = pd.DataFrame(self.order_model.data)
            
            # Проверка наличия данных
            if orders_df.empty:
                ttk.Label(parent_frame, text="Недостаточно данных для анализа", 
                         font=('Arial', 12)).pack(expand=True)
                return
            
            # Преобразование дат и группировка по дням
            orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
            orders_df['date'] = orders_df['order_date'].dt.date
            
            # Агрегация данных по дням
            daily_orders = orders_df.groupby('date').size().reset_index(name='count')
            
            # Создание линейного графика динамики заказов
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(daily_orders['date'], daily_orders['count'], 
                   marker='o', linewidth=2, markersize=4)
            
            ax.set_title('Динамика количества заказов по дням', fontsize=14)
            ax.set_xlabel('Дата', fontsize=10)
            ax.set_ylabel('Количество заказов', fontsize=10)
            
            # Настройка формата отображения дат
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Встраивание графика в Tkinter интерфейс
            canvas = FigureCanvasTkAgg(fig, parent_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
            plt.close(fig)
            
        except Exception as e:
            # Обработка ошибок при создании графика
            ttk.Label(parent_frame, text=f"Ошибка при создании графика: {str(e)}", 
                     font=('Arial', 12)).pack(expand=True)
    
    def show_customer_network(self, parent_frame):
        """
        Строит граф связей между клиентами на основе общих заказанных товаров.
        Узлы - клиенты, связи - общие товары в заказах.
        
        Args:
            parent_frame: Родительский фрейм Tkinter для размещения графика
        """
        # Очистка предыдущего содержимого фрейма
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        try:
            # Получение исходных данных
            orders = self.order_model.data
            order_items = self.order_model.order_items_model.data
            customers = self.customer_model.data
            
            # Проверка наличия необходимых данных
            if not orders or not order_items or not customers:
                ttk.Label(parent_frame, text="Недостаточно данных для анализа", 
                         font=('Arial', 12)).pack(expand=True)
                return
            
            # Инициализация графа
            G = nx.Graph()
            
            # Добавление узлов (клиентов) в граф
            customer_dict = {c['id']: c for c in customers}
            for customer_id, customer in customer_dict.items():
                # Форматирование имени клиента для отображения
                name = f"{customer['last_name']} {customer['first_name'][0]}."
                if customer['middle_name'] and customer['middle_name'].strip():
                    name += f"{customer['middle_name'][0]}."
                G.add_node(customer_id, label=name, size=100)
            
            # Создание словаря товаров по клиентам
            customer_products = {}
            for order in orders:
                customer_id = order['customer_id']
                if customer_id not in customer_products:
                    customer_products[customer_id] = set()
                
                # Получение товаров для текущего заказа
                items = [item for item in order_items if item['order_id'] == order['id']]
                for item in items:
                    customer_products[customer_id].add(item['product_id'])
            
            # Построение связей между клиентами с общими товарами
            customer_ids = list(customer_products.keys())
            for i in range(len(customer_ids)):
                for j in range(i + 1, len(customer_ids)):
                    common_products = customer_products[customer_ids[i]] & customer_products[customer_ids[j]]
                    if common_products:
                        # Вес связи пропорционален количеству общих товаров
                        weight = len(common_products)
                        G.add_edge(customer_ids[i], customer_ids[j], weight=weight)
            
            # Проверка наличия связей в графе
            if not G.edges():
                ttk.Label(parent_frame, text="Нет связей между клиентами", 
                         font=('Arial', 12)).pack(expand=True)
                return
            
            # Визуализация графа
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Позиционирование узлов с помощью spring layout
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # Настройка размеров узлов в зависимости от степени связности
            node_sizes = [150 + 30 * G.degree(node) for node in G.nodes()]
            node_labels = {node: G.nodes[node]['label'] for node in G.nodes()}
            
            # Отрисовка узлов
            nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                                  node_color='lightblue', alpha=0.7, ax=ax)
            
            # Отрисовка связей с толщиной, пропорциональной весу
            edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
            nx.draw_networkx_edges(G, pos, width=[w * 0.3 for w in edge_weights],
                                  alpha=0.6, edge_color='gray', ax=ax)
            
            # Добавление подписей узлов
            nx.draw_networkx_labels(G, pos, node_labels, font_size=7, ax=ax)
            
            # Добавление подписей связей с количеством общих товаров
            edge_labels = {(u, v): f"{w} общ. товаров" 
                          for u, v, w in zip([u for u, v in G.edges()], 
                                           [v for u, v in G.edges()], 
                                           edge_weights)}
            nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=5, ax=ax)
            
            ax.set_title('Граф связей клиентов по общим товарам', fontsize=12)
            ax.axis('off')
            plt.tight_layout()
            
            # Встраивание графика в Tkinter интерфейс
            canvas = FigureCanvasTkAgg(fig, parent_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
            plt.close(fig)
            
        except Exception as e:
            # Обработка ошибок при создании графика
            ttk.Label(parent_frame, text=f"Ошибка при создании графика: {str(e)}", 
                     font=('Arial', 12)).pack(expand=True)