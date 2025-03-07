## What output?

### Default arguments

```python
def update_dict(key, value, defaults={}):
  defaults[key] = value
  print(defaults)

update_dict(key='fruit', value='apple')
update_dict(key='vegetable', value='tomato', defaults = {'tree': 'oak'})
update_dict(key='car', value='ferrari')
```

1. Первый раз создаем словарь "внутри" ф-ции как defaults, записываем в него:
   `{'fruit': 'apple'}`
2. Передаем внутрь существующий словарь и записываем в него:
   `{'tree': 'oak', 'vegetable': 'tomato'}`
3. Записываем в существующий, "внутренний" словарь, созданный в 1:
   `{'fruit': 'apple', 'car': 'ferrari' }`

Я бы исплользовал `dict().update(...)` или переписал бы обертку:

```python
def update_dict(key: str, value: str, defaults: None | dict = None) -> dict:
    if not isinstance(defaults, dict):
        return {key: value}

    defaults.update({key: value})
    return defaults
```

### Inheritance

```python

class Animal:
  def say(self):
    print("I'm an animal")

class Cat(Animal): ...

class Robot:
  def say(self):
    print("I'm a robot")

class RobotCat(Cat, Robot): ...

robo = RoboCat()
robo.say()
print(RoboCat.__mro__)
```

`RobotCat` будет говорить как робот, т.к. классы наследуются, грубо говоря, слева направо.
Для наследования python использует `MethodResolutionOrder` и достает первое удовлетворящий метод.
Подробнее в выводе RoboCat.**mro** (RoboCat -> Cat -> Animal -> Robot)
Для смены на робота, можно использовать изменить порядок наследования или `super(Animal, self).say()`
На super полагаются в PyQT (PySide).

### Django Class-based View

Просто пример, я предпочитаю class-based, `View` или `ViewSet`.
Для простых ендпоинтов можно использовать function-based.

```python
class OrderView(View):
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({"error": "bad product id"}, status=HTTP_404_NOT_FOUND)

        if product.count == 0:
            return JsonResponse({"error": "Product out of stock"}, status=HTTP_400_BAD_REQUEST)

        try:
            order = Orders(product_id=product_id)
            with transaction.atomic():
                product.count -= 1
                product.save()
                order.save()

            return JsonResponse({"success": "Order created", "product_id": product.id, "order_id": order.id}, status=201)
        except Exception:
            return JsonResponse({"error": "Something went wrong"}, status=HTTP_500_INTERNAL_SERVER_ERROR)
```

### Schema Validation

```python
from pydantic import BaseModel


class RequestSchema(BaseModel):
    user_id: str
    action: str
    is_bot: bool = False


# http://localhost/?user_id=1&action=get&is_bot=0
RequestSchema(user_id="1", action="get", is_bot=bool(0))
# http://localhost/?user_id=2&action=5&is_bot=1
RequestSchema(user_id="2", action="5", is_bot=bool(1))
# http://localhost/?user_id=3&action=set_id
RequestSchema(user_id="3", action="set_id")
# http://localhost/?user_id=3&action=set_id&is_bot=
RequestSchema(user_id="3", action="set_id")


```

### Mutable(Resized) Strings

Pyhon, в целях оптимизации, может не пересоздавать строку, а изменять существующую.

```python
def resized_string():
    ex = "hello world: "
    ids = set()

    for i in range(10):
        ex += str(i)
        ids.add(id(ex))

    print(ids)

def copy_string():
    ex = "hello world: "
    _ = list()
    ids = set()

    for i in range(10):
        ex += str(i)
        _.append(ex)
        ids.add(id(ex))

    print(ids)
```

### Lazy Evaluation

Просто интересный пример ленивых вычислений + потребляемых объектов:

```python
iterator = iter(range(10))
print(tuple(zip(iterator, map(lambda x: x**2, iterator))))
```

Вывод: `( (0, 1), (2, 9), (4, 25), (6, 49), (8, 81) )`
