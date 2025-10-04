import math
from collections import Counter
from typing import Dict, List, Tuple
import time


class FanoEncoder:
    """Класс для кодирования текста алгоритмом Фано"""
    
    def __init__(self, text: str, verbose: bool = True):
        self.text = text
        self.verbose = verbose
        self.codes = {}
        self.probabilities = {}
        self._build_codes()
    
    def _calculate_probabilities(self) -> List[Tuple[str, float]]:
        """Вычисляет вероятности появления символов"""
        counter = Counter(self.text)
        total = len(self.text)
        probs = [(char, count / total) for char, count in counter.items()]
        # Сортируем по убыванию вероятности
        probs.sort(key=lambda x: x[1], reverse=True)
        return probs
    
    def _med(self, probs: List[Tuple[str, float]], b: int, e: int) -> int:
        """
        Находит медиану - индекс m такой, что сумма P[b..m] наиболее близка
        к сумме P[(m+1)..e]
        """
        if b >= e:
            return b
        
        # Вычисляем суммы для всех возможных разбиений
        total_sum = sum(p for _, p in probs[b:e+1])
        left_sum = 0
        min_diff = float('inf')
        best_m = b
        
        for m in range(b, e):
            left_sum += probs[m][1]
            right_sum = total_sum - left_sum
            diff = abs(left_sum - right_sum)
            
            if diff < min_diff:
                min_diff = diff
                best_m = m
        
        return best_m
    
    def _fano_recursive(self, probs: List[Tuple[str, float]], 
                       codes: Dict[str, str], b: int, e: int, 
                       current_code: str = ""):
        """
        Рекурсивная процедура Фано
        b - начало обрабатываемой части
        e - конец обрабатываемой части
        """
        if e < b:
            return
        
        if e == b:
            # Единственный символ - присваиваем текущий код
            codes[probs[b][0]] = current_code if current_code else "0"
            return
        
        # Находим медиану
        m = self._med(probs, b, e)
        
        # Присваиваем коды
        for i in range(b, m + 1):
            char = probs[i][0]
            codes[char] = current_code + "0"
        
        for i in range(m + 1, e + 1):
            char = probs[i][0]
            codes[char] = current_code + "1"
        
        # Рекурсивно обрабатываем две части
        self._fano_recursive(probs, codes, b, m, current_code + "0")
        self._fano_recursive(probs, codes, m + 1, e, current_code + "1")
    
    def _build_codes(self):
        """Строит коды Фано для всех символов"""
        probs = self._calculate_probabilities()
        
        if self.verbose:
            print("=" * 80)
            print("ПОСТРОЕНИЕ КОДОВ ФАНО")
            print("=" * 80)
            print(f"\nИсходный текст ({len(self.text)} символов):")
            print(f'"{self.text[:100]}{"..." if len(self.text) > 100 else ""}"')
            print(f"\nВероятности символов (отсортированы по убыванию):")
            print(f"{'Символ':<10} {'Вероятность':<15} {'Частота'}")
            print("-" * 40)
        
        for char, prob in probs:
            self.probabilities[char] = prob
            if self.verbose:
                display_char = repr(char) if char in ['\n', '\t', ' '] else char
                count = int(prob * len(self.text))
                print(f"{display_char:<10} {prob:<15.6f} {count}")
        
        # Запускаем рекурсивную процедуру Фано
        self._fano_recursive(probs, self.codes, 0, len(probs) - 1)
        
        if self.verbose:
            print("\n" + "=" * 80)
            print("ПОСТРОЕННЫЕ КОДЫ")
            print("=" * 80)
            print(f"{'Символ':<10} {'Код':<15} {'Длина':<10} p·l")
            print("-" * 50)
            
            avg_length = 0
            for char, code in sorted(self.codes.items(), 
                                    key=lambda x: len(x[1])):
                display_char = repr(char) if char in ['\n', '\t', ' '] else char
                prob = self.probabilities[char]
                weighted = prob * len(code)
                avg_length += weighted
                print(f"{display_char:<10} {code:<15} {len(code):<10} {weighted:.4f}")
            
            print("-" * 50)
            print(f"Средняя длина кода: {avg_length:.4f} бит/символ")
            print("=" * 80 + "\n")
    
    def encode(self) -> str:
        """Кодирует текст и возвращает битовую строку"""
        encoded = ''.join(self.codes[char] for char in self.text)
        
        if self.verbose:
            print("КОДИРОВАНИЕ")
            print("=" * 80)
            preview_len = min(20, len(self.text))
            print(f"Первые {preview_len} символов:")
            for i, char in enumerate(self.text[:preview_len]):
                display_char = repr(char) if char in ['\n', '\t', ' '] else char
                code = self.codes[char]
                print(f"  {display_char} → {code}")
            
            if len(self.text) > preview_len:
                print(f"  ... (еще {len(self.text) - preview_len} символов)")
            
            print(f"\nЗакодированная строка ({len(encoded)} бит):")
            print(f"{encoded[:100]}{'...' if len(encoded) > 100 else ''}")
            print("=" * 80 + "\n")
        
        return encoded
    
    def decode(self, encoded: str) -> str:
        """Декодирует битовую строку обратно в текст"""
        # Создаем обратный словарь
        reverse_codes = {code: char for char, code in self.codes.items()}
        
        decoded = []
        current_code = ""
        
        for bit in encoded:
            current_code += bit
            if current_code in reverse_codes:
                decoded.append(reverse_codes[current_code])
                current_code = ""
        
        result = ''.join(decoded)
        
        if self.verbose:
            print("ДЕКОДИРОВАНИЕ")
            print("=" * 80)
            print(f"Входная битовая строка ({len(encoded)} бит):")
            print(f"{encoded[:100]}{'...' if len(encoded) > 100 else ''}")
            
            preview_len = min(20, len(result))
            print(f"\nПервые {preview_len} декодированных символов:")
            
            pos = 0
            for i in range(preview_len):
                # Находим код для этого символа
                char = result[i]
                code = self.codes[char]
                display_char = repr(char) if char in ['\n', '\t', ' '] else char
                print(f"  {code} → {display_char}")
                pos += len(code)
            
            if len(result) > preview_len:
                print(f"  ... (еще {len(result) - preview_len} символов)")
            
            print(f"\nДекодированный текст ({len(result)} символов):")
            print(f'"{result[:100]}{"..." if len(result) > 100 else ""}"')
            print("=" * 80 + "\n")
        
        return result


def compare_with_ascii(text: str, encoded: str, codes: Dict[str, str], 
                       probabilities: Dict[str, float]):
    """Сравнивает эффективность кодирования Фано с ASCII"""
    print("\n" + "=" * 80)
    print("СРАВНИТЕЛЬНЫЙ АНАЛИЗ ЭФФЕКТИВНОСТИ")
    print("=" * 80)
    
    # ASCII кодирование
    ascii_bits = len(text) * 8
    
    # Фано кодирование
    fano_bits = len(encoded)
    
    # Теоретическая энтропия
    entropy = -sum(p * math.log2(p) for p in probabilities.values() if p > 0)
    theoretical_min = entropy * len(text)
    
    # Средняя длина кода
    avg_code_length = sum(probabilities[char] * len(codes[char]) 
                          for char in codes)
    
    # Коэффициент сжатия
    compression_ratio = (1 - fano_bits / ascii_bits) * 100
    
    # Эффективность относительно энтропии
    efficiency = (entropy / avg_code_length) * 100
    
    print(f"\nХарактеристики текста:")
    print(f"  Длина текста: {len(text)} символов")
    print(f"  Уникальных символов: {len(codes)}")
    print(f"  Энтропия: {entropy:.4f} бит/символ")
    
    print(f"\nРазмер закодированных данных:")
    print(f"  ASCII (8 бит/символ):        {ascii_bits:>10} бит ({ascii_bits / 8:.0f} байт)")
    print(f"  Фано:                        {fano_bits:>10} бит ({fano_bits / 8:.2f} байт)")
    print(f"  Теоретический минимум:       {theoretical_min:>10.0f} бит ({theoretical_min / 8:.2f} байт)")
    
    print(f"\nЭффективность кодирования:")
    print(f"  Средняя длина кода Фано: {avg_code_length:.4f} бит/символ")
    print(f"  Коэффициент сжатия: {compression_ratio:.2f}%")
    print(f"  Экономия памяти: {ascii_bits - fano_bits} бит ({(ascii_bits - fano_bits) / 8:.2f} байт)")
    print(f"  Эффективность относительно энтропии: {efficiency:.2f}%")
    
    print(f"\nРаспределение длин кодов:")
    length_dist = {}
    for code in codes.values():
        length = len(code)
        length_dist[length] = length_dist.get(length, 0) + 1
    
    for length in sorted(length_dist.keys()):
        count = length_dist[length]
        print(f"  {length} бит: {count} символов")
    
    print("=" * 80)


def test_fano_algorithm():
    """Тестирование алгоритма на разных текстах"""
    
    test_cases = [
        ("Короткий текст", "Hello, World!"),
        ("Средний текст", "Алгоритм Фано строит разделимую префиксную схему " * 5),
        ("Длинный текст", """
        Рекурсивный алгоритм Фано строит разделимую префиксную схему алфавитного 
        кодирования, близкого к оптимальному. Алгоритм Фано использует функцию Med, 
        которая находит медиану указанной части массива. При каждом удлинении кодов 
        в одной части коды удлиняются нулями, а в другой — единицами. Таким образом, 
        коды одной части не могут быть префиксами другой. Удлинение кода заканчивается 
        тогда и только тогда, когда длина части равна 1, то есть остается единственный код.
        """ * 10)
    ]
    
    print("█" * 80)
    print(" " * 25 + "ТЕСТИРОВАНИЕ АЛГОРИТМА ФАНО")
    print("█" * 80 + "\n")
    
    for name, text in test_cases:
        print(f"\n{'▓' * 80}")
        print(f"ТЕСТ: {name} ({len(text)} символов)")
        print(f"{'▓' * 80}\n")
        
        # Создаем кодировщик
        start_time = time.time()
        encoder = FanoEncoder(text, verbose=True)
        
        # Кодируем
        encoded = encoder.encode()
        
        # Декодируем
        decoded = encoder.decode(encoded)
        
        # Проверяем корректность
        is_correct = decoded == text
        encode_time = time.time() - start_time
        
        print(f"ПРОВЕРКА КОРРЕКТНОСТИ:")
        print(f"  Исходный текст == Декодированный текст: {is_correct}")
        print(f"  Время выполнения: {encode_time:.4f} сек")
        
        if not is_correct:
            print("  ⚠ ОШИБКА: Декодированный текст не совпадает с исходным!")
        else:
            print("  ✓ Алгоритм работает корректно!")
        
        # Сравнительный анализ
        compare_with_ascii(text, encoded, encoder.codes, encoder.probabilities)
        
        print("\n")


if __name__ == "__main__":
    test_fano_algorithm()
    
    # Интерактивный режим
    print("\n" + "=" * 80)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("=" * 80)
    print("\nВведите свой текст для кодирования (или оставьте пустым для выхода):")
    
    user_text = input("> ")
    
    if user_text.strip():
        print("\n")
        encoder = FanoEncoder(user_text, verbose=True)
        encoded = encoder.encode()
        decoded = encoder.decode(encoded)
        compare_with_ascii(user_text, encoded, encoder.codes, encoder.probabilities)
        
        print(f"\nПроверка: текст корректно {'декодирован ✓' if decoded == user_text else 'НЕ декодирован ✗'}")