import VirtualKeyboard as VK
import cv2
import mediapipe as mp

# создаём объекты клавиш
a = VK.Key('a', 'a')
b = VK.Key('b', 'b')
c = VK.Key('c', 'c')
d = VK.Key('d', 'd')
e = VK.Key('e', 'e')
f = VK.Key('f', 'f')
g = VK.Key('g', 'g')
h = VK.Key('h', 'h')
i = VK.Key('i', 'i')
j = VK.Key('j', 'j')
k = VK.Key('k', 'k')
l = VK.Key('l', 'l')
backspace = VK.Key('delete', 'delete')

# клавиатура
kb = VK.Keyboard(a, b, c, d, e, f, g, h, i, j, k, l, backspace)

# получаем видео
video = cv2.VideoCapture(0)

# используем модуль .hands
mp_hands = mp.solutions.hands

# инициализируем трекер рук без параметров
hands = mp_hands.Hands()

while True:
    success, frame = video.read()

    if not success:
        break

    # BGR -> RGB; отражение по оси y
    frameEdit = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frameEdit = cv2.flip(frameEdit, 1)

    # обрабатываем изображение и возвращаем
    # данные каждой руки
    results = hands.process(frameEdit)

    # проверяем, нажата ли клавиша
    kb.check_press(results, frameEdit)

    # выводим клавиатуру
    frameEdit = kb.show_keybrd(frameEdit)
    
    # RGB -> BGR
    frameEdit = cv2.cvtColor(frameEdit, cv2.COLOR_RGB2BGR)

    cv2.imshow("Frame", frameEdit)
    cv2.waitKey(1)
