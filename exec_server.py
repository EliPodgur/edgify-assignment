class ExecutionSdk:
    @staticmethod
    def execute_orders(orders: list):
        orders = orders.copy()
        for order in orders:
            order.status = 'approved'
        return orders