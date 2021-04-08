import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderProduct, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    payload = request.data
    try:
        order_products = payload['products']
    except KeyError:
        return Response(
            {"message": "No product list in the order"},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not order_products or not isinstance(order_products, list):
        return Response(
        {"message": "Products must be a list"},
        status=status.HTTP_400_BAD_REQUEST
    )

    if not payload['products']:
        return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)
    order = Order(
        first_name = payload['firstname'],
        last_name = payload['lastname'],
        phone_number = payload['phonenumber'],
        address = payload['address'],
    )
    order.save()
    for product in order_products:
        order_product = OrderProduct(
            order = order,
            product = Product.objects.get(pk=product['product']),
            amount = product['quantity'],
        )
        order_product.save()
    return Response({"message": "ok"}, status=status.HTTP_201_CREATED)
