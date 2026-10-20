from pydantic import BaseModel

from solution import with_price


class Item(BaseModel):
    name: str
    price: float


def test_copy_has_the_new_price():
    item = Item(name="pen", price=1.5)
    cheaper = with_price(item, 0.75)
    assert type(cheaper) is Item
    assert cheaper.price == 0.75
    assert cheaper.name == "pen"


def test_original_is_unchanged():
    item = Item(name="pen", price=1.5)
    cheaper = with_price(item, 0.75)
    assert cheaper is not item
    assert item.price == 1.5
