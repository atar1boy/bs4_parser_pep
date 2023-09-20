### Парсер на BS4

## Программа позволяющая парсить python.org и получать полезную информацию ввиде новых обновлений и изменений правил PEP.

# Список технологий:
> [attrs](https://www.attrs.org/en/stable/index.html)
> [beautifulsoup4](https://beautiful-soup-4.readthedocs.io/en/latest/)
> [lxml](https://lxml.de)
> [prettytable](https://pypi.org/project/prettytable/)
> [url-normalize](https://pypi.org/project/url-normalize/)


Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Получить информцию по командам:
```
* Находясь в директории bs4_parser_pep/src

python3 main.py -h
```

Получить информацию о новых обновлениях Python:
```
* Находясь в директории bs4_parser_pep/src

python3 main.py whats-new
```
