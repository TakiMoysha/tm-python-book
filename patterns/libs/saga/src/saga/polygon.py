from dataclasses import dataclass
from typing import Protocol, override


# =====================================================================


@dataclass(frozen=True)
class OrderData:
    id: int


# =====================================================================


class IService(Protocol):
    _plan = {}

    def cancel(self, *args, **kwargs): ...


class OrderService(IService):
    _plan = {}

    def create_order(self, order_data):
        return OrderData(1)

    @override
    def cancel(self):
        pass


class NotificationService(IService):
    _plan = {}

    def send_notify(self, notification_data, order_id):
        pass

    @override
    def cancel(self):
        pass


class PaymentService(IService):
    _plan = {}

    def make_payment(self, order_id, payment_data):
        pass

    @override
    def cancel(self):
        pass


# =====================================================================


class PaymentCoordinator:
    def order_process(self, order_data, payment_data, notfication_data):
        order_service = OrderService()
        payment_service = PaymentService()
        notification_service = NotificationService()

        try:
            order = order_service.create_order(order_data)
            payment_service.make_payment(order.id, payment_data)
            notification_service.send_notify(order.id, notfication_data)
        except Exception:
            order_service.cancel()
            payment_service.cancel()
            notification_service.cancel()
