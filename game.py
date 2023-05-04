# Игра "МОРСКОЙ БОЙ" от Остапа Москаленко
# B7.5. Итоговое практическое задание
from random import randrange
import random
import time

# Точка координат
class Point:
    def __init__(self, x:int = -1, y:int = -1):
        self.x = x
        self.y = y
    def getPointKey(self):
        return "{xx}:{yy}".format(xx=self.x, yy=self.y)

# Корабль
class Ship:
    def __init__(self, coordinates_, size:int):
        self.coordinates = []
        # Сделай на случай, если потом допишу вариант ручной расстановки кораблей, сейчас координаты при инициализации корабля не используются
        for point in coordinates_:
            self.coordinates.append(point)
        # Размер корабля
        self.size = size
        # HEALTH
        self.health = self.size

    # Добавить координату расположения у корабля
    def addPoint(self, point: Point):
        self.coordinates.append(point)

    # Очистить координаты коробля
    def clearPoints(self):
        self.coordinates = []

    # Получить урон
    def getDamage(self):
        self.health -= 1
        # ПОДБИТ
        if self.health <= 0:
            print(str.format("{0}-ПАЛУБНЫЙ КОРАБЛЬ УНИЧТОЖЕН!", self.size))
            return self.health
        # РАНЕН
        else:
            print(str.format("КОРАБЛЬ РАНЕН! HEALTH = {0}", self.health))
            return  self.health

# ДОСКА
class FieldMap:
    def __init__(self, width: int = 6, height: int = 6, ships = [], hideSheeps: bool = False):
        # Ширина/высота поля с учетом заголовков
        self.width = width + 1
        self.height = height + 1
        # Скрывать корабли доски
        self.hideShips = hideSheeps
        # Установка кораблей на поле боя
        self.startAddingShips(ships)

    def startAddingShips(self, ships:[]):
        # Карта
        self.map = {}
        # Инициализация пустой карты
        self.initMap()
        # Инициализация списка свободных адресов
        self.availablePointsKeys = []
        for x in range(1,self.width):
            for y in range(1,self.height):
                p = Point(x, y)
                self.availablePointsKeys.append(p.getPointKey())
        # Список кораблей
        self.ships = []
        # Пробегаемся по кораблям и пытаемся их расположить
        for ship in ships:
            # Если не удалось вместить все корабли, повторяем процесс
            if self.addShip(ship) == "BAD ARRANGEMENT":
                # print ("RESTART ADDING SHIPS")
                # Запускаем процесс заново
                self.startAddingShips(ships)

    # Создание пустой карты
    def initMap(self):
        for y in range(0, self.height):
            for x in range(0, self.width):
                key = "{xx}:{yy}".format(xx=x, yy=y)
                if x == 0:
                    self.map[key] = str(y)
                elif y == 0:
                    self.map[key] = str(x)
                else:
                    self.map[key] = "0"

    # При уничтожении корабля метим сразу рядом стоящие клетки, я так обычно делаю, когда играю)
    def markPointsNearDestroyedShip(self, ship:Ship):
        xNumbers = []
        yNumbers = []
        shipKeys = []
        for point in ship.coordinates:
            xNumbers.append(point.x)
            yNumbers.append(point.y)
            shipKeys.append(GameEngine.makePointKey(int(point.x), int(point.y)))

        xMin = min(xNumbers)
        xMax = max(xNumbers)
        yMin = min(yNumbers)
        yMax = max(yNumbers)

        # Вычисляем координаты по краям коробля
        if xMin > 1:
            xMin -= 1
        if yMin > 1:
            yMin -= 1
        if xMax < self.width - 1:
            xMax += 1
        if yMax < self.height - 1:
            yMax += 1
        # Метим рядом стоящие клетки
        for x in range(xMin, xMax + 1):
            for y in range(yMin, yMax + 1):
                if GameEngine.makePointKey(x, y) not in shipKeys:
                    self.map[GameEngine.makePointKey(x, y)] = "T"

    # Метод, который определяет можно ли расположить корабль
    def checkShipDestination(self, ship:Ship):
        isAvailable = True
        # Сначала проверяем клетки по координатам самого коробля
        for point in ship.coordinates:
            if self.map[point.getPointKey()] != "0":
                isAvailable = False
                return isAvailable
        # Если все ок, то проверяем рядом стоящие клетки
        if isAvailable:
            xNumbers = []
            yNumbers = []
            for point in ship.coordinates:
                xNumbers.append(point.x)
                yNumbers.append(point.y)

            xMin = min(xNumbers)
            xMax = max(xNumbers)
            yMin = min(yNumbers)
            yMax = max(yNumbers)

            if xMin>1:
                xMin -= 1
            if yMin>1:
                yMin -= 1
            if xMax<self.width - 1:
                xMax += 1
            if yMax<self.height - 1:
                yMax += 1
            for x in range(xMin,xMax+1):
                for y in range(yMin,yMax+1):
                    if self.map[GameEngine.makePointKey(x,y)] != "0":
                        isAvailable = False
                        return isAvailable

            # Если все ок, тогда удаляем из списка свободных адресов занятые клетки + рядом стоящие
            if isAvailable:
                for x in range(xMin, xMax + 1):
                    for y in range(yMin, yMax + 1):
                        # print(str.format("Remove available Point {0}:{1}", x, y))
                        try:
                            self.availablePointsKeys.remove(GameEngine.makePointKey(x, y))
                        except Exception as e:
                            a = ""
                            # print(str.format("ERROR {2} Remove available Point {0}:{1}", x, y, e.args))
            # Возвращаем True, если все норм, либо False
            return isAvailable
    # Метод для получения случайного адреса из списка свободных с учетом размера корабля и его ориентации на поле
    def getRandomAvailablePoint(self, size: int, align: int):
        keyFounded = False
        coordinate = []
        pointKey = ""
        # Пока не найдем подходящий адрес, выполняем поиск
        while(not keyFounded):
            pointKey = random.choice(self.availablePointsKeys)
            coordinate = pointKey.split(":")
            x = int(coordinate[0])
            y = int(coordinate[1])
            if (align):
                if y in range(1, self.height + 1 - size):
                    keyFounded = True
                    break
            else:
                if x in range(1, self.width + 1 - size):
                    keyFounded = True
                    break

        return pointKey
    # Удалить адрес из свободных адресов
    def removeAvailablePoint(self, pointKey: str):
        self.availablePointsKeys.remove(pointKey)
    # Разместить корабль на доске
    def addShip(self, ship: Ship):
        # Если на момент вызова метода уже не осталось свободных адресов, тогда нужно запусить процесс расстановки всех кораблей на доске заново
        if (len(self.availablePointsKeys) == 0):
            return "BAD ARRANGEMENT"
        # Нужно сгенерировать рандомно координаты для корабля
        shipArranged = False
        while (not shipArranged):
            # Пытаемся разместить корабль
            ship.clearPoints()
            verticalAllign = randrange(2)
            key = self.getRandomAvailablePoint(ship.size, verticalAllign)
            x = int(key.split(":")[0])
            y = int(key.split(":")[1])

            if verticalAllign:
                for yy in range(y, y + ship.size):
                    ship.addPoint(Point(x,yy))
            else:
                for xx in range(x, x + ship.size):
                    ship.addPoint(Point(xx, y))
            # Проверяем можно ли разместить корабль на доске с расчитанными координатами
            if self.checkShipDestination(ship):
                shipArranged = True
                self.ships.append(ship)
                # Отмечаем корабль на карте
                for point in ship.coordinates:
                    self.map[point.getPointKey()] = "■"
            else:
                # Разместить не удалось, запускаем расчет координат заново
                shipArranged = False
        return "OK"

    # Метод, который отрабатывает полученный выстрел по входящему адресу
    def getShoot(self, point:Point):
        # Если попали в корабль, отмечаем X на карте и наносим урон кораблю
        if self.map[point.getPointKey()] == "■":
            self.map[point.getPointKey()] = "X"
            for ship in self.ships:
                for point_ in ship.coordinates:
                    if int(point_.x) == int(point.x) and int(point_.y) == int(point.y):
                        if ship.getDamage() <= 0:
                            self.markPointsNearDestroyedShip(ship)
            return "X"
        # Промах
        elif self.map[point.getPointKey()] == "0":
            self.map[point.getPointKey()] = "T"
            return "T"
        # Повторный выстрел
        else:
            raise ValueError("ПОВТОРНЫЙ ВЫСТРЕЛ!")
            # return "REPEAT"

# Движок игры, в котором я прописал статические методы для работы с игрой
class GameEngine:
    # Вывод доски на экран
    @staticmethod
    def showFieldMap(field: FieldMap):

        for y in range(0, field.height):
            fieldLine = ""
            for x in range(0, field.width):
                key = "{xx}:{yy}".format(xx=x, yy=y)
                symbol = field.map[key]
                if (field.hideShips):
                    if symbol == "■":
                        symbol = "0"
                fieldLine += symbol
                if (x >= 0 and x < field.width):
                    fieldLine += " | "
            print(fieldLine)

    # Метод получения ключа по координатам точки
    @staticmethod
    def makePointKey(x:int, y:int):
        return "{xx}:{yy}".format(xx=x, yy=y)

    # Метод получения координат из ключа
    @staticmethod
    def getCoordinatesFromKey(key:str):
        return key.split(":")

    # Метод проверки полного уничтожения всех кораблей на карте
    @staticmethod
    def isAllShipsDestroyed(field: FieldMap):
        totalHealth = 0
        for ship in field.ships:
            totalHealth += ship.health
        if not totalHealth:
            return True
        else:
            return False
    # Метод, который организует ход игры для игрока и AI
    @staticmethod
    def makeShoot(field:FieldMap):
        # Получения координат выстрела для игрока и AI
        xSaved = False
        while(not xSaved):
            if (field.hideShips):
                x = input("КООРДИНАТА ВЫСТРЕЛА X = ")
                try:
                    if int(x) in range(1,field.width):
                        xSaved = True
                except Exception as e:
                    print("НЕКОРРЕКТНЫЙ ВВОД КООРДИНАТЫ X. ВВЕДИТЕ ЕЩЕ РАЗ.")
            else:
                x = randrange(1,field.width)
                xSaved = True

        ySaved = False
        while(not ySaved):
            if (field.hideShips):
                y = input("КООРДИНАТА ВЫСТРЕЛА Y = ")
                try:
                    if int(y) in range(1,field.height):
                        ySaved = True
                except Exception as e:
                    print("НЕКОРРЕКТНЫЙ ВВОД КООРДИНАТЫ Y. ВВЕДИТЕ ЕЩЕ РАЗ.")
            else:
                y = randrange(1, field.height)
                ySaved = True

        res = ""

        # Вызываем обработчик выстрела у доски, если будет повторный выстрел, обработчик выдаст исключение
        try:
            field.getShoot(Point(x, y))
            playerSide = ""
            if field.hideShips:
                playerSide = "ИГРОК"
            else:
                playerSide = "AI"
            print(str.format("{2} ПРОИЗВЕЛ ВЫСТРЕЛ ПО КООРДИНАТАМ {0}:{1}", x, y, playerSide))
            s = field.map[GameEngine.makePointKey(x, y)]
            resultWord = ""
            if s == "X":
                resultWord = "ПОПАДАНИЕ!"
            else:
                resultWord = "ПРОМАХ"

            print(str.format("РЕЗУЛЬТАТ {0} - {1}", field.map[GameEngine.makePointKey(x, y)], resultWord))

        except ValueError:
            print("СЮДА УЖЕ СТРЕЛЯЛИ! ВВЕДИТЕ КООРДИНАТЫ ЗАНОВО")
            res = GameEngine.makeShoot(field)

# СТАРТ ИГРЫ
try:
    # ЗАДАЕМ РАЗМЕР ДОСКИ
    mapWidth = 6
    mapHeight = 6

    # СОЗДАЕМ КОРАБЛИ ДЛЯ ИГРОКА
    ships_User = []
    ships_User.append(Ship([],3))
    ships_User.append(Ship([],2))
    ships_User.append(Ship([],2))
    ships_User.append(Ship([],1))
    ships_User.append(Ship([],1))
    ships_User.append(Ship([],1))
    ships_User.append(Ship([],1))

    # СОЗДАЕМ КОРАБЛИ ДЛЯ AI
    ships_AI = []
    ships_AI.append(Ship([], 3))
    ships_AI.append(Ship([], 2))
    ships_AI.append(Ship([], 2))
    ships_AI.append(Ship([], 1))
    ships_AI.append(Ship([], 1))
    ships_AI.append(Ship([], 1))
    ships_AI.append(Ship([], 1))

    # СОЗДАЕМ ДОСКИ ДЛЯ ИГРОКА И AI
    field_User = FieldMap(mapWidth, mapHeight, ships_User, False)
    field_AI = FieldMap(mapWidth, mapHeight, ships_AI, True)

    # ВЫВОД ДОСОК НА ЭКРАН ПОЛЬЗОВАТЕЛЯ
    print("- - - - - - - - - - - - ")
    print("USER MAP")
    GameEngine.showFieldMap(field_User)
    print("- - - - - - - - - - - - ")
    print("AI MAP")
    GameEngine.showFieldMap(field_AI)

    # СТАРТУЕМ ИГРУ, ПЕРВЫЙ ХОД ЗА ИГРОКОМ
    turnStepper = 1
    fields = [field_AI,field_User]
    while (True):
        turnStepper += 1
        if turnStepper > 1:
            turnStepper = 0
            print("- - - - - - - - - - - - ")
            print("ХОД ИГРОКА")
        else:
            print("- - - - - - - - - - - - ")
            print("ХОД AI")

        GameEngine.makeShoot(fields[turnStepper])
        print("- - - - - - - - - - - - ")
        print("USER MAP")
        GameEngine.showFieldMap(field_User)
        print("- - - - - - - - - - - - ")
        print("AI MAP")
        GameEngine.showFieldMap(field_AI)
        time.sleep(2)

        # ПРОВЕРКА НА ПОБЕДУ
        UserState = GameEngine.isAllShipsDestroyed(field_User)
        AIState = GameEngine.isAllShipsDestroyed(field_AI)
        if UserState or AIState:
            print("КОНЕЦ БИТВЫ!")
            if UserState == AIState:
                print("НИЧЬЯ!")
            elif UserState and not AIState:
                print("ПОБЕДУ ОДЕРЖАЛ AI!")
            else:
                print("ПОБЕДУ ОДЕРЖАЛ ИГРОК!")
            break
except Exception as e:
    print(str.format("В ХОДЕ ИГРЫ ВОЗНИКЛА ОШИБКА {0}",e.__str__()))