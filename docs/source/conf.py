import os
import sys

# Добавьте путь к корневой директории проекта
sys.path.insert(0, os.path.abspath('../..'))

# Расширения
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

# Настройки
templates_path = ['_templates']
exclude_patterns = []

# HTML тема
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Язык
language = 'ru'

# Autodoc настройки
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# Mock импорты для зависимостей
autodoc_mock_imports = [
    'tkinter', 'matplotlib', 'pandas', 'seaborn', 'networkx',
    'unittest', 'unittest.mock'
]