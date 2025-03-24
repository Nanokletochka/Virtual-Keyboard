from copy import deepcopy
import cv2
from math import hypot
import time


class Keyboard:
    """Организует расположение клавиш и клавиатуры.


    Аргументы:
    [1] args: Объекты клавиш
    [2] start: Начальная позиция клавиатуры
    [3] klen: Длина клавиатуры
    Поля:
    [1] start_x, cls.start_y: Начальная позиция клавиатуры -
        (x,y)
    [2] klen: Длина клавиатуры
    [3] keys: Упорядоченный массив объектов клавиш -
        [[строка_клавиш_1],[строка_клавиш_2],[...],[...], ...]
    [4] row_coords: Упорядоченный массив координат строк клавиатуры -
        [[(x),(y)],[],[], ...]
    [5] currText: Текущий набранный текст
    [6] startTime: Время, прошедшее с последнего нажатия клавиши
    Методы:
    [1] sort_keys: Сортировка клавиш по строкам
    [2] set_rows_coords: Определение позиции строк клавиш
    [3] show_keybrd: Отрисовка клавиатуры
    [4] check_press: Проверка на нажатие клавиши
    [5] two_fingers: Извлечение координат двух пальцев
    """

    currText = None
    row_coords = None
    startTime = None
    klen = None
    keys = None
    start_y = None
    start_x = None
    _instance = None

    def __new__(cls, *args, klen=400, start=(50, 50)):
        if not cls._instance:
            cls._instance = super().__new__(cls)

            # начальная точка клавиатуры
            cls.start_x, cls.start_y = start
            # длина клавиатуры
            cls.klen = klen
            # упорядоченный массив объектов клавиш
            cls.keys = cls.sort_keys(args)
            # упорядоченный массив координат строк клавиатуры
            cls.row_coords = cls.set_rows_coords(args)
            # текущий набранный текст
            cls.currText = ""
            # время, прошедшее с последнего нажатия клавиши
            cls.startTime = 0

        return cls._instance

    @classmethod
    def set_rows_coords(cls, args):
        """Определение позиции строк клавиатуры."""

        # Находим начальную x,y точку строки клавиатуры (левый верхний угол
        # прямоугольнка) и конечную точку (правый нижний). В итоге будет
        # - [[start_coord, end_coord],[координаты_строки_2],[...], ...]

        row_coords = []
        start_x = cls.start_x
        start_y = cls.start_y - 60
        end_x, end_y = cls.start_x, cls.start_y

        for row in cls.keys:
            # складываем ширину каждой клавиши строки
            # чтобы добраться до координаты конца строки
            for key in row:
                end_x += key.size_w

            start_y += 60
            end_y += 60

            row_coords.append(deepcopy([(start_x, start_y), (end_x, end_y)]))

            end_x = cls.start_x

        return row_coords

    @classmethod
    def sort_keys(cls, all_keys):
        """Сортирует и компанует клавиши в клавиатуре."""

        key_list = []
        # все клавиши определённой строки
        row_keys = []
        # длина строки
        row_len = 0
        for key in all_keys:
            # условия перехода на новую строку
            if row_len > cls.klen:
                key_list.append(deepcopy(row_keys))
                row_keys.clear()
                row_len = 0

            row_keys.append(key)
            row_len += key.size_w
        else:
            # если остались не добавленные клавиши
            if row_keys:
                key_list.append(deepcopy(row_keys))

        return key_list
    
    @classmethod
    def show_keybrd(cls, image):
        """Отображает клавиатуру."""

        # координаты клавиш относительно начала клавиатуры
        key_coord_x, key_coord_y = cls.start_x, cls.start_y
        color = (0, 255, 255)
        thickness = 2

        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        text_color = (0, 255, 255)

        for row in cls.keys:
            for key in row:
                # отрисовка формы клавиши
                cv2.rectangle(
                    image,
                    (key_coord_x, key_coord_y),
                    (key_coord_x + key.size_w, key_coord_y + key.size_h),
                    color,
                    thickness
                )
                # текст клавиши
                cv2.putText(
                    image, key.logo,
                    (key_coord_x + 5, key_coord_y + 30),
                    font, fontScale, text_color, 1
                )
                # после отрисовки клавиши увеличиваем координату x до следующей клавиши в строке
                key_coord_x += key.size_w

            # переход на новую строку

            # "обнуляем" координату x
            key_coord_x = cls.start_x
            # увеличиваем координату y до следующей строки
            key_coord_y += 60  # 60 - высота клавиши

        return image

    @classmethod
    def check_press(cls, results, image):
        """Проверяет, нажата ли какая-либо клавиша."""

        # координаты указ. и больш. пальцев
        two_fing = cls.two_fingers(results, image)

        # если координаты определены ...
        if two_fing:

            big_fing, index_fing = two_fing

            # вычисление расстояния между пальцами
            distance = hypot(big_fing[0] - index_fing[0], big_fing[1] - index_fing[1])

            # индекс строки клавиатуры
            index = 0

            # если расстояние достаточно мало ...
            if distance < 20:
                elapsed_time = time.time() - cls.startTime

            # если расстояние достаточно мало и
            # время с последнего нажатия НЕ достаточно мало ...
            if (distance < 20) and (elapsed_time > 0.8):

                # проверяем координаты указ. пальца на
                # вхождение в какую-либо из строк клавиатуры
                for row in cls.row_coords:
                    index_fing_x, index_fing_y = index_fing

                    # координаты начала строки n
                    row_start_x, row_start_y = row[0]
                    # координаты конца строки n
                    row_end_x, row_end_y = row[1]

                    # если есть вхождение в строку...
                    if (
                            row_start_x < index_fing_x < row_end_x
                    ) and (
                            row_start_y < index_fing_y < row_end_y
                    ):
                        # ..., то теперь будет проверять на какую
                        # клавишу из данной строки нажал пользователь

                        # ищем клавишу, нажатую пользователем
                        # задаём стартовую координату x для клавиши
                        key_x = cls.start_x
                        # задаём стартовую координату y для клавиши:
                        # y = стартовая_y_клавиатуры + номер_строки * высота клавиши (рис.)
                        key_y = cls.start_y + index * 60

                        # проходимся по клавишам строки № index
                        for key in cls.keys[index]:
                            # проверяем на вхождение
                            if (
                                    key_x < index_fing_x < key_x + key.size_w
                            ) and (
                                    key_y < index_fing_y < key_y + key.size_h
                            ):
                                # применяем метод, который реализрует работу клавиши,
                                # к набранному тексту
                                cls.currText = key.activateValue(cls.currText)
                                # выводим набранный текст
                                print(cls.currText)
                                # засекает время нажатия
                                cls.startTime = time.time()
                                break
                            # если нажатая клавиша не найдена
                            key_x += key.size_w

                    # увеличиваем индекс (номер) строки
                    # при переходе на новую строку (в цикле for)
                    index += 1

    @staticmethod
    def two_fingers(results, image):
        """Возвращает координаты указ. и большого пальцев."""

        # Координаты большого и указательного пальцев
        big_fing_coord = ()
        index_fing_coord = ()
        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                # проходимся по каждой точке
                for id, lm in enumerate(hand.landmark):
                    if id == 4:
                        h, w, _ = image.shape
                        dot_x, dot_y = int(lm.x * w), int(lm.y * h)
                        big_fing_coord = dot_x, dot_y
                    if id == 8:
                        h, w, _ = image.shape
                        dot_x, dot_y = int(lm.x * w), int(lm.y * h)
                        index_fing_coord = dot_x, dot_y

            if big_fing_coord and index_fing_coord:
                return big_fing_coord, index_fing_coord
            else:
                return None


class Key:
    """Представляет клавишу.


    Аргументы:
    [1] logo: Отображаемый символ/текст клавиши
    [2] value: Значение клавиши
    Поля:
    [1] logo: Отображаемый символ/текст клавиши
    [2] value: Значение клавиши (строка)
    [3] size_w: Ширина клавиши
    [4] size_h: Высота клавиши
    Методы:
    [1] calcSize: Рассчёт размера клавиши
    [2] delete: Реализация backspace
    [3] letter: Реализация обычной символьной клавиши
    """

    def __init__(self, logo, value):
        # отображаемый символ клавиши
        self.logo = str(logo)
        # значение клавиши
        self.value = str(value)
        # вычисление размера клавиши
        self.size_w, self.size_h = self.calcSize(self.logo)

        # Определяем функционал обычных и спецклавиш
        match value:
            case "delete":
                self.activateValue = self.delete
            case _:
                self.activateValue = self.letter

    # значение спецклавиши delete
    @staticmethod
    def delete(string):
        """Функционал клавиши backspace."""

        return string[:len(string) - 1]

    # значение обычной клавиши
    def letter(self, string):
        """Функционал символьной клавиши."""

        return string + self.value

    @staticmethod
    def calcSize(logo):
        """Высчитывает размер клавиши."""

        # Размер квадратной клавиши 60 x 60;
        # Размер длинной клавиши:
        # на каждый символ (S > 1) по 10 пикселей

        if len(logo) == 1:
            return 60, 60
        else:
            return 60 + (len(logo) - 1) * 10, 60
