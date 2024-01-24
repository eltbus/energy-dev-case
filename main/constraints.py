from enum import Enum


class ParkName(str, Enum):
    netterden = "Netterden"
    stadskanaal = "Stadskanaal"
    windskanaal = "Windskanaal"
    zwartenbergseweg = "Zwartenbergseweg"
    bemmel = "Bemmel"


class EnergyType(str, Enum):
    wind = "Wind"
    solar = "Solar"


class Timezone(str, Enum):
    amsterdam = "Europe/Amsterdam"
    bucharest = "Europe/Bucharest"
    istanbul = "Europe/Istanbul"
    volgograd = "Europe/Volgograd"
    vienna = "Europe/Vienna"
