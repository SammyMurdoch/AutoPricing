import copy
import statistics
from collections import deque
from sympy import Rational

class Node:
    def __init__(self, s=None):
        self.stock_price = s
        self.value = None
        self.intrinsic_value = None
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __str__(self):
        return f"Stock: {self.stock_price}, IV:{self.intrinsic_value}, V:{self.value} "


class Model:
    def __init__(self, s0, r, T, up_func, down_func, intrinsic_func, stopping_times):
        self.s0 = s0
        self.r = r
        self.T = T
        self.up_func = up_func
        self.down_func = down_func
        self.intrinsic_func = intrinsic_func
        self.stopping_times = stopping_times

        self.model_root = Node(self.s0)

        self.generate_stock_tree(0, self.model_root)
        self.price_tree(0, self.model_root, [])
        
    def generate_stock_tree(self, t, current_node):
        if t >= self.T:
            return
        
        else:
            up_stock_price = self.up_func(current_node.stock_price)
            down_stock_price = self.down_func(current_node.stock_price)
            
            current_node.add_child(Node(up_stock_price))
            current_node.add_child(Node(down_stock_price))

            self.generate_stock_tree(t+1, current_node.children[0])
            self.generate_stock_tree(t+1, current_node.children[1])

    def price_tree(self, t, current_node, previous_data=None):
        new_data = copy.deepcopy(previous_data) + [current_node.stock_price]
        current_node.intrinsic_value = self.intrinsic_func(current_node.stock_price, new_data)

        if not current_node.children:
            current_node.value = current_node.intrinsic_value
            return

        for child in current_node.children:
            self.price_tree(t+1, child, new_data)

        up_factor = current_node.children[0].stock_price / current_node.stock_price
        down_factor = current_node.children[1].stock_price / current_node.stock_price

        p = ((1+self.r[t]) - down_factor) / (up_factor - down_factor)

        potential_current_node_value = 1/(1+self.r[t]) * (p*current_node.children[0].value +
                                             (1-p)*current_node.children[1].value)

        if t not in self.stopping_times:
            current_node.value = potential_current_node_value

        else:
            current_node.value = max(potential_current_node_value, current_node.intrinsic_value)

    def display_tree(self, current_node):
        node_deque = deque([current_node])

        while node_deque:
            current_node = node_deque.popleft()
            print(current_node)

            if current_node.children:
                node_deque.append(current_node.children[0])
                node_deque.append(current_node.children[1])


def up_func(s):
    return s + 2


def down_func(s):
    return s - 4


def intrinsic_func(s, previous_data):
    return max(statistics.median(previous_data) - 4, 0)


S0 = Rational(20)
r = [Rational(0) for i in range(3)]

model = Model(S0, r, Rational(3), up_func, down_func, intrinsic_func=intrinsic_func, stopping_times=[0, 1, 3])
model.display_tree(model.model_root)


# Intrinsic values dont include r


