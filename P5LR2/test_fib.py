"""
Тесты для лабораторной работы по ряду Фибоначчи.

Содержит тесты для:
1. Сопрограммы my_genn() из gen_fib.py
2. Итератора FibonacchiLst из fib_iterator.py

Для запуска тестов выполните: python test_fib.py
"""

# Импортируем необходимые модули
from gen_fib import my_genn
from fib_iterator import FibonacchiLst


# ============================================================================
# ТЕСТЫ ДЛЯ ЗАДАНИЯ 1: СОПРОГРАММА
# ============================================================================

def test_fib_1():
    """
    Тест из ТЗ: тривиальный случай n = 3, список [0, 1, 1]
    
    Проверяем, что сопрограмма корректно работает для минимального
    нетривиального случая.
    """
    # Создаем экземпляр сопрограммы
    gen = my_genn()
    
    # Отправляем число 3 и получаем результат
    result = gen.send(3)
    
    # Проверяем, что результат соответствует ожидаемому
    assert result == [0, 1, 1], f"Ожидалось [0, 1, 1], получено {result}"
    
    print("✓ test_fib_1: Тривиальный случай n=3 - ПРОЙДЕН")


def test_fib_2():
    """
    Тест из ТЗ: пять первых членов ряда [0, 1, 1, 2, 3]
    
    Проверяем стандартный случай.
    """
    gen = my_genn()
    result = gen.send(5)
    
    # Важно: после каждого send() нужно вызвать next() для подготовки
    # к следующему send(), но в тестах мы создаем новый генератор каждый раз
    
    assert result == [0, 1, 1, 2, 3], f"Ожидалось [0, 1, 1, 2, 3], получено {result}"
    
    print("✓ test_fib_2: Пять первых членов - ПРОЙДЕН")


def test_fib_3():
    """
    Тест из ТЗ: восемь первых членов ряда [0, 1, 1, 2, 3, 5, 8, 13]
    
    Проверяем более длинную последовательность.
    """
    gen = my_genn()
    result = gen.send(8)
    
    expected = [0, 1, 1, 2, 3, 5, 8, 13]
    assert result == expected, f"Ожидалось {expected}, получено {result}"
    
    print("✓ test_fib_3: Восемь первых членов - ПРОЙДЕН")


def test_fib_4():
    """
    Граничный случай: n = 1 (только первое число)
    
    Проверяем минимально возможный список.
    """
    gen = my_genn()
    result = gen.send(1)
    
    assert result == [0], f"Ожидалось [0], получено {result}"
    
    print("✓ test_fib_4: Граничный случай n=1 - ПРОЙДЕН")


def test_fib_5():
    """
    Граничный случай: n = 2 (первые два числа)
    
    Проверяем список из двух элементов.
    """
    gen = my_genn()
    result = gen.send(2)
    
    assert result == [0, 1], f"Ожидалось [0, 1], получено {result}"
    
    print("✓ test_fib_5: Граничный случай n=2 - ПРОЙДЕН")


def test_fib_6():
    """
    Граничный случай: n = 0 (пустой список)
    
    Проверяем, что функция корректно обрабатывает запрос на 0 элементов.
    """
    gen = my_genn()
    result = gen.send(0)
    
    assert result == [], f"Ожидался пустой список [], получено {result}"
    
    print("✓ test_fib_6: Граничный случай n=0 - ПРОЙДЕН")


def test_fib_7():
    """
    Проверка последовательных вызовов сопрограммы.
    
    Важная особенность сопрограмм - они сохраняют состояние между вызовами.
    После отправки значения и получения результата, нужно вызвать next()
    чтобы подготовить сопрограмму к следующему send().
    """
    gen = my_genn()
    
    # Первый вызов: получаем 3 числа
    result1 = gen.send(3)
    assert result1 == [0, 1, 1]
    
    # Подготавливаем генератор для следующего вызова
    next(gen)
    
    # Второй вызов: получаем следующие 2 числа
    # Важно: генератор помнит свое состояние, поэтому продолжает с того же места
    result2 = gen.send(2)
    assert result2 == [2, 3], f"Ожидалось [2, 3], получено {result2}"
    
    print("✓ test_fib_7: Последовательные вызовы - ПРОЙДЕН")


# ============================================================================
# ТЕСТЫ ДЛЯ ЗАДАНИЯ 2: ИТЕРАТОР
# ============================================================================

def test_fib_iterator_1():
    """
    Основной тест из ТЗ для итератора.
    
    Для lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1]
    FibonacchiLst должен вернуть [0, 1, 2, 3, 5, 8, 1]
    """
    # Тестовый список из ТЗ
    lst = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1]
    
    # Создаем итератор и преобразуем в список
    fib_iter = FibonacchiLst(lst)
    result = list(fib_iter)
    
    # Ожидаемый результат из ТЗ
    expected = [0, 1, 2, 3, 5, 8, 1]
    
    assert result == expected, f"Ожидалось {expected}, получено {result}"
    
    print("✓ test_fib_iterator_1: Основной тест из ТЗ - ПРОЙДЕН")


def test_fib_iterator_2():
    """
    Тест с отрицательными числами.
    
    Проверяем, что отрицательные числа корректно отфильтровываются
    (не являются числами Фибоначчи).
    """
    lst = [-5, -1, 0, 1, 2, -8]
    fib_iter = FibonacchiLst(lst)
    result = list(fib_iter)
    
    expected = [0, 1, 2]
    assert result == expected, f"Ожидалось {expected}, получено {result}"
    
    print("✓ test_fib_iterator_2: Тест с отрицательными числами - ПРОЙДЕН")


def test_fib_iterator_3():
    """
    Тест с большими числами Фибоначчи.
    
    Проверяем, что алгоритм корректно определяет большие числа Фибоначчи.
    """
    # 55, 89, 144 - это числа Фибоначчи
    # 100, 200 - не являются числами Фибоначчи
    lst = [55, 89, 144, 100, 200]
    fib_iter = FibonacchiLst(lst)
    result = list(fib_iter)
    
    expected = [55, 89, 144]
    assert result == expected, f"Ожидалось {expected}, получено {result}"
    
    print("✓ test_fib_iterator_3: Тест с большими числами - ПРОЙДЕН")


def test_fib_iterator_4():
    """
    Тест с пустым списком.
    
    Проверяем, что итератор корректно работает с пустым списком.
    """
    lst = []
    fib_iter = FibonacchiLst(lst)
    result = list(fib_iter)
    
    expected = []
    assert result == expected, f"Ожидался пустой список [], получено {result}"
    
    print("✓ test_fib_iterator_4: Тест с пустым списком - ПРОЙДЕН")


def test_fib_iterator_5():
    """
    Тест без чисел Фибоначчи.
    
    Проверяем, что итератор возвращает пустой список, когда в исходном
    списке нет чисел Фибоначчи.
    """
    # 4, 6, 7, 10, 11 - не являются числами Фибоначчи
    lst = [4, 6, 7, 10, 11]
    fib_iter = FibonacchiLst(lst)
    result = list(fib_iter)
    
    expected = []
    assert result == expected, f"Ожидался пустой список [], получено {result}"
    
    print("✓ test_fib_iterator_5: Тест без чисел Фибоначчи - ПРОЙДЕН")


def test_fib_iterator_6():
    """
    Тест с повторяющимися числами.
    
    Проверяем, что итератор возвращает все вхождения чисел Фибоначчи,
    включая повторяющиеся.
    """
    lst = [1, 1, 2, 2, 3, 3, 5, 5]
    fib_iter = FibonacchiLst(lst)
    result = list(fib_iter)
    
    expected = [1, 1, 2, 2, 3, 3, 5, 5]
    assert result == expected, f"Ожидалось {expected}, получено {result}"
    
    print("✓ test_fib_iterator_6: Тест с повторяющимися числами - ПРОЙДЕН")


def test_fibonacci_property():
    """
    Дополнительный тест для проверки математического свойства.
    
    Проверяем, что функция _is_fibonacci корректно определяет
    известные числа Фибоначчи и отсеивает не-числа Фибоначчи.
    """
    # Список известных чисел Фибоначчи
    fibonacci_numbers = [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
    
    # Числа, которые НЕ являются числами Фибоначчи
    non_fibonacci = [4, 6, 7, 9, 10, 11, 12, 14, 15]
    
    # Проверяем числа Фибоначчи
    for num in fibonacci_numbers:
        # Создаем список с одним числом и проверяем
        fib_iter = FibonacchiLst([num])
        result = list(fib_iter)
        assert result == [num], f"{num} должен быть числом Фибоначчи"
    
    # Проверяем не-числа Фибоначчи  
    for num in non_fibonacci:
        fib_iter = FibonacchiLst([num])
        result = list(fib_iter)
        assert result == [], f"{num} не должен быть числом Фибоначчи"
    
    print("✓ test_fibonacci_property: Проверка математического свойства - ПРОЙДЕН")


# ============================================================================
# ОСНОВНАЯ ФУНКЦИЯ ДЛЯ ЗАПУСКА ВСЕХ ТЕСТОВ
# ============================================================================

def run_all_tests():
    """
    Запускает все тесты и выводит результаты.
    
    Returns:
        True если все тесты пройдены, False если есть ошибки
    """
    print("=" * 70)
    print("ЗАПУСК ТЕСТОВ ДЛЯ ЛАБОРАТОРНОЙ РАБОТЫ 2")
    print("=" * 70)
    
    # Список всех тестовых функций
    all_tests = [
        # Тесты для задания 1 (сопрограмма)
        test_fib_1,
        test_fib_2, 
        test_fib_3,
        test_fib_4,
        test_fib_5,
        test_fib_6,
        test_fib_7,
        
        # Тесты для задания 2 (итератор)
        test_fib_iterator_1,
        test_fib_iterator_2,
        test_fib_iterator_3,
        test_fib_iterator_4,
        test_fib_iterator_5,
        test_fib_iterator_6,
        test_fibonacci_property,
    ]
    
    # Счетчики успешных и неуспешных тестов
    passed = 0
    failed = 0
    
    print("\n" + "=" * 70)
    print("ТЕСТЫ ДЛЯ ЗАДАНИЯ 1: СОПРОГРАММА ДЛЯ РЯДА ФИБОНАЧЧИ")
    print("=" * 70)
    
    # Запускаем тесты для задания 1
    for i, test_func in enumerate(all_tests[:7], 1):
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: НЕ ПРОЙДЕН - {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: ОШИБКА - {type(e).__name__}: {e}")
            failed += 1
    
    print(f"\nЗадание 1: {passed} тестов пройдено, {failed} тестов не пройдено")
    
    print("\n" + "=" * 70)
    print("ТЕСТЫ ДЛЯ ЗАДАНИЯ 2: ИТЕРАТОР ДЛЯ ФИЛЬТРАЦИИ ЧИСЕЛ ФИБОНАЧЧИ")
    print("=" * 70)
    
    # Сбрасываем счетчики для задания 2
    passed = 0
    failed = 0
    
    # Запускаем тесты для задания 2
    for i, test_func in enumerate(all_tests[7:], 1):
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: НЕ ПРОЙДЕН - {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: ОШИБКА - {type(e).__name__}: {e}")
            failed += 1
    
    print(f"\nЗадание 2: {passed} тестов пройдено, {failed} тестов не пройдено")
    
    # Общий итог
    total_passed = sum(1 for test in all_tests)
    total_tests = len(all_tests)
    
    print("\n" + "=" * 70)
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("=" * 70)
    print(f"Всего тестов: {total_tests}")
    print(f"Пройдено успешно: {total_passed - (failed if 'failed' in locals() else 0)}")
    print(f"Не пройдено: {failed if 'failed' in locals() else 0}")
    
    if failed == 0:
        print("\n✅ ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
        return True
    else:
        print(f"\n❌ Есть непройденные тесты: {failed}")
        return False


# Точка входа в программу
if __name__ == "__main__":
    # Запускаем все тесты
    success = run_all_tests()
    
    # Завершаем программу с соответствующим кодом выхода
    # 0 - успех, 1 - ошибка (стандартная практика)
    exit(0 if success else 1)