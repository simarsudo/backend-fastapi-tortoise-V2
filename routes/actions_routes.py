import sqlalchemy
from typing import Annotated, Literal
from sqlalchemy.exc import IntegrityError
from fastapi import Depends, HTTPException, APIRouter
from core.schema.products_schema import (
    WishlistItemAddedSchema,
    CartItemAddedSchema,
    ProductInCartSchema,
    UpdateCartItemQtySchema,
    UpdateCartItemSizeSchema,
)
from core.db_connection import get_db_session
from sqlalchemy.orm import Session
from core.models.products_model import Products, Wishlist, Cart
from core.models.user_model import Address, Customer
from core.schema.user_schema import User, NewAddress
from core.utils.user_utils import get_customer

router = APIRouter()

TAXRATE = 5


size_ids = {
    "s": 1,
    "m": 2,
    "l": 3,
    "xl": 4,
    "xxl": 5,
    "32": 6,
    "34": 7,
    "36": 8,
    "38": 9,
    "40": 10,
}


@router.post("/add-to-wishlist", response_model=WishlistItemAddedSchema)
def add_to_wishlist(
    item_slug,
    customer: Annotated[User, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    try:
        product_id = db.query(Products).filter(Products.slug == item_slug).first()
        if product_id is not None:
            wishlist_item = Wishlist(product_id=product_id.id, customer_id=customer.id)
            db.add(wishlist_item)
            db.commit()
            return {
                "status": "success",
                "message": "Product added to wishlist successfully",
            }
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    except HTTPException:
        raise HTTPException(status_code=400)
    except IntegrityError:
        db.rollback()
        return {"status": "failed", "message": "Product already in customer wishlist"}
    except Exception:
        raise HTTPException(status_code=500)


@router.post("/add-to-cart", response_model=CartItemAddedSchema)
def add_to_cart(
    item_slug: str,
    size: Literal["s", "m", "l", "xl", "xxl", "32", "34", "36", "38", "40"],
    qty: int,
    customer: Annotated[User, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    try:
        product_id = db.query(Products).filter(Products.slug == item_slug).first()
        if product_id is not None:
            old_item_in_cart = (
                db.query(Cart)
                .filter(
                    Cart.product_id == product_id.id,
                    Cart.customer_id == customer.id,
                    Cart.size_id == size_ids[size],
                )
                .first()
            )
            # if user already have item in cart
            if old_item_in_cart:
                old_item_in_cart.qty += qty
            # if user added item in the cart for the first time
            else:
                cart_item = Cart(
                    product_id=product_id.id,
                    customer_id=customer.id,
                    size_id=size_ids[size],
                    qty=qty,
                )
                db.add(cart_item)
            db.commit()
            return {"status": "success", "message": "Item added to cart"}
        else:
            return {"status": "failed", "message": "Product not found"}
    except IntegrityError:
        db.rollback()
        return {"status": "failed", "message": "Product already in customer cart"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500)


@router.get("/is-in-wishlist", status_code=200)
def is_in_wishlist(
    slug: str,
    customer: Annotated[User, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    try:
        product_id = db.query(Products).filter(Products.slug == slug).first()
        if product_id is None:
            raise HTTPException(status_code=404)
        wishlist_item = (
            db.query(Wishlist)
            .filter(
                Wishlist.product_id == product_id.id,
                Wishlist.customer_id == customer.id,
            )
            .first()
        )
        if wishlist_item:
            return {"status": "success"}
        raise HTTPException(status_code=404)
    except HTTPException:
        raise HTTPException(status_code=400, detail="Product not found")


# Todo move api to right path
@router.get("/get-wishlist", status_code=200)
def get_wishlist(
    customer: Annotated[User, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    try:
        wishlist_items = (
            db.query(Wishlist).filter(Wishlist.customer_id == customer.id).all()
        )
        if wishlist_items is None:
            raise HTTPException(status_code=404)
        response = []
        for item in wishlist_items:
            response.append(
                {
                    "name": item.wishlist_item.name,
                    "slug": item.wishlist_item.slug,
                    "price": item.wishlist_item.price,
                    "image": "http://127.0.0.1:8000/"
                    + item.wishlist_item.images[0].image_path,
                    "type": item.wishlist_item.type,
                    "sizeAvailable": {
                        i.size.size: True if i.quantity > 0 else False
                        for i in item.wishlist_item.inventory
                    },
                }
            )
        return {"wishlist": response}
    except HTTPException:
        raise


@router.post("/remove-wishlist-item", status_code=200)
def remove_wishlist_item(
    slug: str,
    customer: Annotated[User, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    product_id = db.query(Products).filter(Products.slug == slug).first()
    try:
        if product_id is None:
            raise HTTPException(status_code=404, detail="Product not found")
        wishlist_item = (
            db.query(Wishlist)
            .filter(
                Wishlist.product_id == product_id.id,
                Wishlist.customer_id == customer.id,
            )
            .first()
        )
        if wishlist_item:
            db.delete(wishlist_item)
            db.commit()
            return {
                "status": "success",
                "message": "Item removed from wishlist successfully",
            }
        else:
            raise HTTPException(status_code=404, detail="Item not found in wishlist.")
    except sqlalchemy.exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/move-to-cart", status_code=200)
def move_to_cart(
    product_in_cart: ProductInCartSchema,
    customer: Annotated[User, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    try:
        product = (
            db.query(Products).filter(Products.slug == product_in_cart.slug).first()
        )
        if product is None:
            raise HTTPException(status_code=404)
        wishlist_item = (
            db.query(Wishlist)
            .filter(
                Wishlist.product_id == product.id,
                Wishlist.customer_id == customer.id,
            )
            .first()
        )
        if wishlist_item is None:
            raise HTTPException(status_code=400, detail="Item not in user wishlist.")
        old_item_in_cart = (
            db.query(Cart)
            .filter(
                Cart.product_id == product.id,
                Cart.customer_id == customer.id,
                Cart.size_id == size_ids[product_in_cart.size],
            )
            .first()
        )
        # if user already have item in cart
        if old_item_in_cart:
            old_item_in_cart.qty += product_in_cart.qty
        # if user added item in the cart for the first time
        else:
            cart_item = Cart(
                product_id=product.id,
                customer_id=customer.id,
                size_id=size_ids[product_in_cart.size],
                qty=product_in_cart.qty,
            )
            db.add(cart_item)
        db.delete(wishlist_item)
        db.commit()
    except sqlalchemy.exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Could not add the product to cart."
        )
    except HTTPException:
        raise


@router.get("/get-cart-summary")
def get_cart_summary(
    customer: Annotated[User, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    customer_address = (
        db.query(Address).filter_by(id=customer.delivery_address_id).first()
    )
    cart = []
    response = {
        "cartBeforeTax": 0,
        "gst": 0,
        "cartTotal": 0,
        "items": cart,
        "addresses": [],
        "deliveryAddress": customer_address,
    }
    try:
        cart_list = db.query(Cart).filter_by(customer_id=customer.id).all()
        if cart_list is None:
            return response
        for item in cart_list:
            response["cartBeforeTax"] += item.cart_item.price * item.qty
            cart.append(
                {
                    "id": item.cart_item.id,
                    "slug": item.cart_item.slug,
                    "name": item.cart_item.name,
                    "type": item.cart_item.type,
                    "image": "http://127.0.0.1:8000/"
                    + item.cart_item.images[0].image_path,
                    "qty": item.qty,
                    "size": item.size.size,
                    "price": item.cart_item.price,
                    "availableSize": {
                        i.size.size: True if i.quantity > 0 else False
                        for i in item.cart_item.inventory
                    },
                }
            )
            gst = (response["cartBeforeTax"] * TAXRATE) / 100
            response["gst"] = gst
            response["cartTotal"] = response["cartBeforeTax"] + gst
        user_addresses = db.query(Address).filter_by(customer_id=customer.id).all()
        response["addresses"] = user_addresses
        return response
    except sqlalchemy.exc.SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Could not add the product to cart."
        )
    except HTTPException:
        raise


@router.post("/update-cart-item-qty")
def update_cart_item_qty(
    item: UpdateCartItemQtySchema,
    customer: Annotated[User, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    cart = []
    response = {"cartBeforeTax": 0, "gst": 0, "cartTotal": 0, "items": cart}
    try:
        cart_item = (
            db.query(Cart)
            .filter(
                Cart.customer_id == customer.id,
                Cart.product_id == item.id,
                Cart.size_id == size_ids[item.size],
            )
            .first()
        )
        if cart_item is None:
            raise HTTPException(status_code=404)
        cart_item.qty = item.qty
        db.commit()
        cart_list = db.query(Cart).filter_by(customer_id=customer.id).all()
        for item in cart_list:
            response["cartBeforeTax"] += item.cart_item.price * item.qty
            gst = (response["cartBeforeTax"] * TAXRATE) / 100
            response["gst"] = gst
            response["cartTotal"] = response["cartBeforeTax"] + gst
            cart.append(
                {
                    "id": item.cart_item.id,
                    "slug": item.cart_item.slug,
                    "name": item.cart_item.name,
                    "type": item.cart_item.type,
                    "image": "http://127.0.0.1:8000/"
                    + item.cart_item.images[0].image_path,
                    "qty": item.qty,
                    "size": item.size.size,
                    "price": item.cart_item.price,
                    "availableSize": {
                        i.size.size: True if i.quantity > 0 else False
                        for i in item.cart_item.inventory
                    },
                }
            )
            gst = (response["cartBeforeTax"] * TAXRATE) / 100
        return response
    except HTTPException:
        raise


@router.post("/update-item-size")
def update_item_qty(
    item: UpdateCartItemSizeSchema,
    customer: Annotated[User, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    cart = []
    response = {"cartBeforeTax": 0, "gst": 0, "cartTotal": 0, "items": cart}
    try:
        prev_cart_item = (
            db.query(Cart)
            .filter(
                Cart.customer_id == customer.id,
                Cart.product_id == item.id,
                Cart.size_id == size_ids[item.size],
            )
            .first()
        )
        cart_item = (
            db.query(Cart)
            .filter(
                Cart.customer_id == customer.id,
                Cart.product_id == item.id,
                Cart.size_id == size_ids[item.prevSize],
                Cart.qty == item.qty,
            )
            .first()
        )
        if prev_cart_item:
            if prev_cart_item.qty + item.qty > 10:
                prev_cart_item.qty = 10
            else:
                prev_cart_item.qty += item.qty
            db.delete(cart_item)
        else:
            cart_item.size_id = size_ids[item.size]
        db.commit()
        cart_list = db.query(Cart).filter_by(customer_id=customer.id).all()
        if cart_list is None:
            return response
        for item in cart_list:
            response["cartBeforeTax"] += item.cart_item.price * item.qty
            cart.append(
                {
                    "id": item.cart_item.id,
                    "slug": item.cart_item.slug,
                    "name": item.cart_item.name,
                    "type": item.cart_item.type,
                    "image": "http://127.0.0.1:8000/"
                    + item.cart_item.images[0].image_path,
                    "qty": item.qty,
                    "size": item.size.size,
                    "price": item.cart_item.price,
                    "availableSize": {
                        i.size.size: True if i.quantity > 0 else False
                        for i in item.cart_item.inventory
                    },
                }
            )
            gst = (response["cartBeforeTax"] * TAXRATE) / 100
            response["gst"] = gst
            response["cartTotal"] = response["cartBeforeTax"] + gst
        return response
    except sqlalchemy.exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not update item size.")
    except HTTPException:
        raise


@router.post("/remove-cart-item")
def remove_cart_item(
    item_id,
    qty,
    size,
    customer: Annotated[User, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    try:
        cart_item = (
            db.query(Cart)
            .filter(
                Cart.customer_id == customer.id,
                Cart.product_id == item_id,
                Cart.size_id == size_ids[size],
                Cart.qty == qty,
            )
            .first()
        )
        if cart_item:
            db.delete(cart_item)
            db.commit()
            cart_list = db.query(Cart).filter_by(customer_id=customer.id).all()
            cart = []
            response = {"cartBeforeTax": 0, "gst": 0, "cartTotal": 0, "items": cart}
            if cart_list is None:
                return response
            for item in cart_list:
                response["cartBeforeTax"] += item.cart_item.price * item.qty
                cart.append(
                    {
                        "id": item.cart_item.id,
                        "slug": item.cart_item.slug,
                        "name": item.cart_item.name,
                        "type": item.cart_item.type,
                        "image": "http://127.0.0.1:8000/"
                        + item.cart_item.images[0].image_path,
                        "qty": item.qty,
                        "size": item.size.size,
                        "price": item.cart_item.price,
                        "availableSize": {
                            i.size.size: True if i.quantity > 0 else False
                            for i in item.cart_item.inventory
                        },
                    }
                )
                gst = (response["cartBeforeTax"] * TAXRATE) / 100
                response["gst"] = gst
                response["cartTotal"] = response["cartBeforeTax"] + gst
            return response
        raise HTTPException(status_code=404, detail="Item not found in cart.")
    except sqlalchemy.exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not remove item from cart.")
    except HTTPException:
        raise


@router.post("/add-new-user-address")
def get_user_addresses(
    address: NewAddress,
    customer: Annotated[User, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    try:
        addresses = db.query(Address).filter_by(customer_id=customer.id).all()
        if len(addresses) < 3:
            new_address = Address(
                name=address.name,
                address=address.address,
                city=address.city,
                state=address.state,
                pinCode=address.pinCode,
                customer_id=customer.id,
            )
            db.add(new_address)
            db.commit()
            new_addresses = db.query(Address).filter_by(customer_id=customer.id).all()
            return {"new_addresses": new_addresses}
        else:
            raise HTTPException(status_code=400)
    except sqlalchemy.exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/update-delivery-address")
def update_delivery_address(
    addressId,
    customer: Annotated[User, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    try:
        address = db.query(Address).filter_by(id=addressId).first()
        if address:
            customer.delivery_address_id = address.id
            db.commit()
            return {"status": "success"}
        else:
            raise HTTPException(status_code=404, detail="Address not found")
    except sqlalchemy.exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/place-order")
def place_order(
    # payment_details: PaymentDetailsSchema,
    customer: Annotated[User, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    # try:
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    # pd = PaymentDetails(
    #     card_number=payment_details.cardNumber,
    #     card_holder_name=payment_details.name,
    #     month=payment_details.month,
    #     year=payment_details.year,
    #     cvv=payment_details.cvv,
    #     billing_address_id=customer.delivery_address_id,
    # )
    # db.add(pd)
    cart_items_in_db = db.query(Cart).filter_by(customer_id=customer.id).all()
    if cart_items_in_db is None:
        raise HTTPException(status_code=400, detail="No item in cart.")
    cart_items = []
    for item in cart_items_in_db:
        print(item)
        cart_items.append(
            {
                "id": item.id,
                "product_details": item.cart_item,
                "size": item.size.size,
                "qty": item.qty,
            }
        )
    return {"cart_item": cart_items}
    # except sqlalchemy.exc.SQLAlchemyError:
    #     db.rollback()
    #     raise HTTPException(status_code=500)
    # except HTTPException:
    #     raise
