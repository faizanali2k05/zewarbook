from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    role: str
    is_active: bool


@dataclass
class Item:
    id: int
    sku: str
    name_urdu: str
    quantity: int
    min_quantity: int
