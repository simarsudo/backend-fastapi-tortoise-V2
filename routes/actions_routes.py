from typing import Annotated, Literal
from fastapi import Depends, HTTPException, APIRouter
from config import SIZE_IDS, BASELINK
from utils import get_customer, get_cart_summary_response
from models import Products, Wishlist, Cart, Address
from schema import (
    AddToWishlistOut,
    CustomerSchema,
    AddToCartOut,
    IsInWishlistOut,
    RemoveWishlistItemOut,
    MoveToCartIn,
    MoveToCartOut,
    UpdateCartItemQtyIn,
    UpdateCartItemSizeIn,
    NewAddressUserAddressIn,
)

router = APIRouter()


@router.post("/add-to-wishlist", response_model=AddToWishlistOut)
async def add_to_wishlist(
    item_slug,
    customer: Annotated[CustomerSchema, Depends(get_customer)],
):
    try:
        product_id = await Products.get_or_none(slug=item_slug)
        if product_id is None:
            raise HTTPException(status_code=404, detail="Product not found.")
        wishlist_item = Wishlist(product=product_id, customer=customer)
        await wishlist_item.save()
        return {"success": "Product added to wishlist"}
    except HTTPException:
        raise


@router.post("/add-to-cart", response_model=AddToCartOut)
async def add_to_cart(
    item_slug: str,
    size: Literal["s", "m", "l", "xl", "xxl", "32", "34", "36", "38", "40"],
    qty: int,
    customer: Annotated[CustomerSchema, Depends(get_customer)],
):
    try:
        if qty > 10:
            raise HTTPException(status_code=400, detail="Cannot add more than 10 items")
        product = await Products.get_or_none(slug=item_slug)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        old_item_in_cart = await Cart.get_or_none(
            product_id=product.id, customer_id=customer.id, size_id=SIZE_IDS[size]
        )
        # if user already have item in cart
        if old_item_in_cart:
            if old_item_in_cart.qty + qty <= 10:
                old_item_in_cart.qty += qty
                await old_item_in_cart.save()
        # if user added item in the cart for the first time
        else:
            cart_item = Cart(
                product_id=product.id,
                customer_id=customer.id,
                size_id=SIZE_IDS[size],
                qty=qty,
            )
            await cart_item.save()
        return {"success": "Product added to cart"}
    except HTTPException:
        raise


@router.get("/is-in-wishlist", response_model=IsInWishlistOut)
async def is_in_wishlist(
    slug: str,
    customer: Annotated[CustomerSchema, Depends(get_customer)],
):
    try:
        product = await Products.get_or_none(slug=slug)
        if product is None:
            raise HTTPException(status_code=404, detail="Item not found in wishlist")
        wishlist_item = await Wishlist.get_or_none(
            product_id=product.id, customer_id=customer.id
        )
        if wishlist_item:
            return {"success": "Item in wishlist"}
        raise HTTPException(status_code=404)
    except HTTPException:
        raise


# TODO: Add response_model
@router.get("/get-wishlist", status_code=200)
async def get_wishlist(
    customer: Annotated[CustomerSchema, Depends(get_customer)],
):
    try:
        wishlist_items = await Wishlist.filter(
            customer_id=customer.id
        ).prefetch_related(
            "product__images",
            "product__inventory__size",
            "customer",
        )
        if not wishlist_items:
            raise HTTPException(status_code=404)
        response = []
        for item in wishlist_items:
            response.append(
                {
                    "name": item.product.name,
                    "slug": item.product.slug,
                    "price": item.product.price,
                    "image": BASELINK + item.product.images[0].path,
                    "type": item.product.type,
                    "sizeAvailable": {
                        i.size.size: True if i.quantity > 0 else False
                        for i in item.product.inventory
                    },
                }
            )
        return {"wishlist": response}
    except HTTPException:
        raise


@router.post("/remove-wishlist-item", response_model=RemoveWishlistItemOut)
async def remove_wishlist_item(
    slug: str,
    customer: Annotated[CustomerSchema, Depends(get_customer)],
):
    try:
        product_id = await Products.get_or_none(slug=slug)
        if product_id is None:
            raise HTTPException(status_code=404, detail="Product not found")
        wishlist_item = await Wishlist.get_or_none(
            product_id=product_id.id, customer_id=customer.id
        )
        if wishlist_item:
            await wishlist_item.delete()
            return {
                "success": "Item removed from wishlist successfully",
            }
        else:
            raise HTTPException(status_code=404, detail="Item not found in wishlist.")
    except HTTPException:
        raise


@router.post("/move-to-cart", response_model=MoveToCartOut)
async def move_to_cart(
    request: MoveToCartIn,
    customer: Annotated[CustomerSchema, Depends(get_customer)],
):
    try:
        size_id = SIZE_IDS[request.size]
        product = await Products.get_or_none(slug=request.slug)
        if product is None:
            raise HTTPException(status_code=404)
        wishlist_item = await Wishlist.get_or_none(
            product_id=product.id, customer_id=customer.id
        )
        if wishlist_item is None:
            raise HTTPException(status_code=400, detail="Item not in user wishlist.")
        old_item_in_cart = await Cart.get_or_none(
            product_id=product.id,
            customer_id=customer.id,
            size_id=size_id,
        )
        # if user already have item in cart
        if old_item_in_cart:
            if old_item_in_cart.qty + request.qty <= 10:
                old_item_in_cart.qty += request.qty
                await old_item_in_cart.save()
        # if user added item in the cart for the first time
        else:
            cart_item = await Cart(
                product_id=product.id,
                customer_id=customer.id,
                size_id=size_id,
                qty=request.qty,
            )
            await cart_item.save()
        return {
            "success": "Item moved to cart",
        }
    except HTTPException:
        raise


# TODO: Add response_model
@router.get("/get-cart-summary")
async def get_cart_summary(
    customer: Annotated[CustomerSchema, Depends(get_customer)],
):
    try:
        return await get_cart_summary_response(customer.id)
    except HTTPException:
        raise


# TODO: Add response_model
@router.post("/update-cart-item-qty")
async def update_cart_item_qty(
    item: UpdateCartItemQtyIn,
    customer: Annotated[CustomerSchema, Depends(get_customer)],
):
    try:
        if item.qty > 10:
            raise HTTPException(
                status_code=400, detail="Item qty cannot be more than 10."
            )
        size_id = SIZE_IDS[item.size]
        cart_item = await Cart.get_or_none(
            customer_id=customer.id, product_id=item.id, size_id=size_id
        )
        if cart_item is None:
            raise HTTPException(status_code=404)
        cart_item.qty = item.qty
        await cart_item.save()

        return await get_cart_summary_response(customer.id)
    except HTTPException:
        raise


# TODO: Add response_model
@router.post("/update-item-size")
async def update_item_qty(
    item: UpdateCartItemSizeIn,
    customer: Annotated[CustomerSchema, Depends(get_customer)],
):
    try:
        size_id = SIZE_IDS[item.size]
        prev_cart_item = await Cart.get_or_none(
            customer_id=customer.id, product_id=item.id, size_id=size_id
        )
        cart_item = await Cart.get_or_none(
            customer_id=customer.id,
            product_id=item.id,
            size_id=size_id,
            qty=item.qty,
        )
        if prev_cart_item:
            if prev_cart_item.qty + item.qty > 10:
                prev_cart_item.qty = 10
            else:
                prev_cart_item.qty += item.qty
            await cart_item.delete()
        else:
            cart_item.size_id = SIZE_IDS[item.size]
            await cart_item.save()

        return await get_cart_summary_response(customer.id)
    except HTTPException:
        raise


# TODO: Add response_model
@router.post("/remove-cart-item")
async def remove_cart_item(
    item_id,
    qty,
    size,
    customer: Annotated[CustomerSchema, Depends(get_customer)],
):
    size_id = SIZE_IDS[size]
    try:
        cart_item = await Cart.get_or_none(
            customer_id=customer.id,
            product_id=item_id,
            size_id=size_id,
            qty=qty,
        )
        if cart_item:
            await cart_item.delete()
            return await get_cart_summary_response(customer.id)
        raise HTTPException(status_code=404, detail="Item not found in cart.")
    except HTTPException:
        raise


# TODO: Add response_model
@router.post("/add-new-user-address")
async def get_user_addresses(
    address: NewAddressUserAddressIn,
    customer: Annotated[CustomerSchema, Depends(get_customer)],
):
    try:
        addresses = await Address.filter(customer_id=customer.id)
        if len(addresses) < 3:
            new_address = Address(
                name=address.name,
                address=address.address,
                city=address.city,
                state=address.state,
                pinCode=address.pinCode,
                customer_id=customer.id,
            )
            await new_address.save()
            new_addresses = await Address.filter(customer_id=customer.id)
            return {"new_addresses": new_addresses}
        else:
            raise HTTPException(status_code=400)
    except HTTPException:
        raise


# TODO: Add response_model
@router.post("/update-delivery-address")
async def update_delivery_address(
    addressId,
    customer: Annotated[CustomerSchema, Depends(get_customer)],
):
    try:
        address = await Address.get_or_none(id=addressId)
        if address:
            customer.delivery_address_id = address.id
            await address.save()
            return {"status": "success"}
        else:
            raise HTTPException(status_code=404, detail="Address not found")
    except HTTPException:
        raise


# @router.post("/place-order")
# def place_order(
#     # payment_details: PaymentDetailsSchema,
#     customer: Annotated[User, Depends(get_customer)],
#     db: Session = Depends(get_db_session),
# ):
#     # try:
#     if customer is None:
#         raise HTTPException(status_code=404, detail="Customer not found")
#     # pd = PaymentDetails(
#     #     card_number=payment_details.cardNumber,
#     #     card_holder_name=payment_details.name,
#     #     month=payment_details.month,
#     #     year=payment_details.year,
#     #     cvv=payment_details.cvv,
#     #     billing_address_id=customer.delivery_address_id,
#     # )
#     # db.add(pd)
#     cart_items_in_db = db.query(Cart).filter_by(customer_id=customer.id).all()
#     if cart_items_in_db is None:
#         raise HTTPException(status_code=400, detail="No item in cart.")
#     cart_items = []
#     for item in cart_items_in_db:
#         print(item)
#         cart_items.append(
#             {
#                 "id": item.id,
#                 "product_details": item.cart_item,
#                 "size": item.size.size,
#                 "qty": item.qty,
#             }
#         )
#     return {"cart_item": cart_items}
#     # except sqlalchemy.exc.SQLAlchemyError:
#     #     db.rollback()
#     #     raise HTTPException(status_code=500)
#     # except HTTPException:
#     #     raise
