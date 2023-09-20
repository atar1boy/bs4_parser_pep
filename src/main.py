import re
import logging
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_STATUS_URL
)
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    # Полуаем ответ от сайта и готовим супчик.
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return response
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')

    # Ищем нужный тэг.
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'})

    # Подготавливаем переменные и проходимся циклом по тэгам.
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        session = requests_cache.CachedSession()
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        result.append((version_link, h1.text, dl_text))

    return result


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return response
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        link = a_tag['href']
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, 'a', {
        'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    """
    Функция парсер для получения статистики PEP.
    """

    # Полуаем ответ от сайта и готовим супчик.
    response = get_response(session, PEP_STATUS_URL)
    if response is None:
        return response
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')

    # Ищем нужные теги.
    section_tag = find_tag(
        soup, 'section', {'id': 'numerical-index'})
    tbody_tag = find_tag(section_tag, 'tbody')
    tr_tags = tbody_tag.find_all('tr')

    # Подготавливаем переменные и проходимся циклом по PEP-ам.
    results = [('Статус', 'Количество')]
    total_pep = 0
    statistics = {
        'A': 0,
        'D': 0,
        'F': 0,
        'P': 0,
        'R': 0,
        'S': 0,
        'W': 0,
        '': 0,
    }
    for tr_tag in tr_tags:

        # Получаем статус и тип PEP-a из таблицы.
        abbr_tag = find_tag(tr_tag, 'abbr')
        if len(abbr_tag.text) == 2:
            status_on_table = abbr_tag.text[-1]
        else:
            status_on_table = ''

        # Переходим на страницу PEP и получаем статус и тип.
        a_tag = find_tag(tr_tag, 'a', {'class': 'pep reference internal'})
        link = urljoin(PEP_STATUS_URL, a_tag['href'])
        session = requests_cache.CachedSession()
        response = get_response(session, link)
        if response is None:
            logging.info(f'Ссылка {link}, не доступна')
            continue
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        dl_tag = find_tag(soup, 'dl', {'class': 'rfc2822 field-list simple'})
        status_on_page = dl_tag.find('abbr').text

        # Сравним полученные данные.
        if status_on_page not in EXPECTED_STATUS[status_on_table]:
            logging.info(
                f'Несовпадающие статусы: '
                f'{link} '
                f'Cтатус в карточке: {status_on_page} '
                f'Ожидаемые статусы: {EXPECTED_STATUS[status_on_table]}'
            )

        # Собираем статистику
        total_pep += 1
        statistics[status_on_table] += 1

    # Подготавливаем ответ функции.
    for key in statistics.keys():
        results.append(
            (EXPECTED_STATUS[key], statistics[key])
        )
    results.append(('Total', total_pep))

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    else:
        logging.info('Ошибка при выполнении.')
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
