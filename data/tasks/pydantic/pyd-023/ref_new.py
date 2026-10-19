def with_price(item, price):
    return item.model_copy(update={"price": price})
