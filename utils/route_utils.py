from models import Cart, Address
from config import BASELINK, TAXRATE


async def get_cart_summary_response(customer_id: int) -> dict:
    cart_list = await Cart.filter(customer_id=customer_id).prefetch_related(
        "product__cart_item",
        "product__images",
        "size__cart_item_size",
        "product__inventory__size",
    )
    cart = []
    response = {
        "cartBeforeTax": 0,
        "gst": 0,
        "cartTotal": 0,
        "items": cart,
        "addresses": [],
        "deliveryAddress": [],
    }

    if not cart_list:
        return response

    for item in cart_list:
        response["cartBeforeTax"] += item.product.price * item.qty
        cart.append(
            {
                "id": item.product.id,
                "slug": item.product.slug,
                "name": item.product.name,
                "type": item.product.type,
                "image": BASELINK + item.product.images[0].path,
                "qty": item.qty,
                "size": item.size.size,
                "price": item.product.price,
                "availableSize": {
                    i.size.size: True if i.quantity > 0 else False
                    for i in item.product.inventory
                },
            }
        )
    gst = (response["cartBeforeTax"] * TAXRATE) / 100
    response["gst"] = gst
    response["cartTotal"] = response["cartBeforeTax"] + gst
    user_addresses = await Address.get(customer_id=customer_id)
    response["addresses"] = user_addresses
    response["deliveryAddress"] = user_addresses
    return response
