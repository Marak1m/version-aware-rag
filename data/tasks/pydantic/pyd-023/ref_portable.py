def with_price(item, price):
    return type(item)(**{**dict(item), "price": price})
