import logging


END_GAME = object()
logger = logging.getLogger(__name__)


# Errors
class NoCommandException(Exception):
    pass


# Mix-ins
class Controllable:
    commands = {}

    def control(self, *args):
        command = self.commands.get(args[0])
        if command is None:
            return self.subordinate.control(*args)
        command(*args)

    @property
    def subordinate(self) -> 'Controllable':
        raise NoCommandException


class Loggable:

    @property
    def logger(self):
        return logger.getChild(type(self).__name__)


# Base Classes
class Controller(Controllable):

    def __init__(self, subordinate):
        self._subordinate = subordinate

    def interact(self):
        player_input = input("What will you do?\n")
        args = player_input.lower().split()
        try:
            return self.control(*args)
        except NoCommandException:
            return self.reprompt(*args)

    def reprompt(self, *args):
        print(f"{args[0]} is not a valid command.")
        return None

    @property
    def subordinate(self):
        return self._subordinate


class Engine(Controllable, Loggable):

    def __init__(self, controller=Controller):
        self.commands = {
            "quit": self.exit,
            "q": self.exit,
        }
        self.running = False
        self.controller = controller(self)
        self.game = Game()

    def exit(self, *args):
        self.logger.debug("Exit called.")
        self.running = False

    def run(self):
        self.logger.info("Starting Engine")
        self.running = True
        self.game.start()
        while self.running:
            self.controller.interact()
        self.logger.info("Engine stopping")

    @property
    def subordinate(self):
        return self.game


class Game(Controllable):

    def __init__(self):
        self.map = Map()
        self.player = Player(self.map.starting_room)  # TODO: Player

    @property
    def subordinate(self):
        return self.player

    def start(self):
        self.player.current_room.describe()


class Map:
    def __init__(self):
        room_descriptions = [
            "The room is like a dungeon.",
            "The room is like a space ship.",
            "The room has a wide window under a lake.",
            "The room doesn't make sense"
        ]
        rooms = (
            (room_descriptions[0], 3, 1, None, None),
            (room_descriptions[1], 2, None, None, 0),
            (room_descriptions[2], None, None, 1, 3),
            (room_descriptions[3], None, 2, 0, None)
        )
        self.rooms = []
        for room in rooms:
            description, north, east, south, west = room
            north = self.get_room(north)
            south = self.get_room(south)
            east = self.get_room(east)
            west = self.get_room(west)
            self.rooms.append(Room(description, north_neighbor=north,
                                   south_neighbor=south, east_neighbor=east,
                                   west_neighbor=west))

    @property
    def starting_room(self):
        return self.rooms[0]

    def get_room(self, id):
        if id is not None and len(self.rooms) > id:
            return self.rooms[id]
        else:
            return None


class Player(Controllable):

    def __init__(self, starting_room):
        self.current_room = starting_room
        self.inventory = {}
        self.commands = {
            "cry": self.cry,
            "c": self.cry,
            "move": self.move,
            "m": self.move
        }

    @property
    def subordinate(self):
        return self.current_room

    def cry(self, *args):
        print("You stand there and sob.")

    def move(self, _, direction):
        previous_room = self.current_room
        self.current_room = self.current_room.move(direction)
        if self.current_room is previous_room:
            print("There's no path.")
        else:
            self.current_room.describe()
        return None


class Room(Controllable):

    def __init__(self, description, *, north_neighbor=None, south_neighbor=None,
                 east_neighbor=None, west_neighbor=None):
        self.description = description
        self.north_neighbor = north_neighbor
        if self.north_neighbor is not None:
            self.north_neighbor.south_neighbor = self
        self.south_neighbor = south_neighbor
        if self.south_neighbor is not None:
            self.south_neighbor.north_neighbor = self
        self.east_neighbor = east_neighbor
        if self.east_neighbor is not None:
            self.east_neighbor.west_neighbor = self
        self.west_neighbor = west_neighbor
        if self.west_neighbor is not None:
            self.west_neighbor.east_neighbor = self
        self.directions = {
            "north": self.north,
            "south": self.south,
            "east": self.east,
            "west": self.west
        }

    def describe(self):
        print(self.description)
        if self.north_neighbor:
            print("There is an exit to the north.")
        if self.east_neighbor:
            print("There is an exit to the east.")
        if self.south_neighbor:
            print("There is an exit to the south.")
        if self.west_neighbor:
            print("There is an exit to the west.")

    def move(self, direction):
        if direction not in self.directions:
            print(f"{direction} is not a valid direction")
            return self
        return self.directions[direction]()

    def north(self):
        return self.north_neighbor or self

    def south(self):
        return self.south_neighbor or self

    def east(self):
        return self.east_neighbor or self

    def west(self):
        return self.west_neighbor or self
