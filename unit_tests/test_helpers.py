from numbers import Number
from typing import Dict, List, Union
from unittest import TestCase

from helpers import (
    add_is_in_payment_plan,
    add_remaining_amount,
    add_next_payment_due_date,
)


class HelpersTest(TestCase):
    def setUp(self) -> None:
        self.debts: List[Dict[str, Number]] = [
            {
                'amount': 123.46,
                'id': 0,
            },
            {
                'amount': 100,
                'id': 1,
            },
            {
                'amount': 4920.34,
                'id': 2,
            },
            {
                'amount': 12938,
                'id': 3,
            },
            {
                'amount': 9238.02,
                'id': 4,
            },
        ]
        self.debt_ids_to_plans: Dict[int, Dict[str, Union[Number, str]]] = {
            0: {
                'amount_to_pay': 102.5,
                'debt_id': 0,
                'id': 0,
                'installment_amount': 51.25,
                'installment_frequency': 'WEEKLY',
                'start_date': '2020-09-28',
            },
            1: {
                'amount_to_pay': 100,
                'debt_id': 1,
                'id': 1,
                'installment_amount': 25,
                'installment_frequency': 'WEEKLY',
                'start_date': '2020-08-01',
            },
            2: {
                'amount_to_pay': 4920.34,
                'debt_id': 2,
                'id': 2,
                'installment_amount': 1230.085,
                'installment_frequency': 'BI_WEEKLY',
                'start_date': '2020-01-01',
            },
            3: {
                'amount_to_pay': 4312.67,
                'debt_id': 3,
                'id': 3,
                'installment_amount': 1230.085,
                'installment_frequency': 'WEEKLY',
                'start_date': '2020-08-01',
            },
        }
        self.plan_ids_to_payments: Dict[int, List[Dict[str, Union[Number, str]]]] = {
            0: [
                {
                    'amount': 51.25,
                    'date': '2020-09-29',
                    'payment_plan_id': 0,
                },
                {
                    'amount': 51.25,
                    'date': '2020-10-29',
                    'payment_plan_id': 0,
                },
            ],
            1: [
                {
                    'amount': 25,
                    'date': '2020-08-08',
                    'payment_plan_id': 1,
                },
                {
                    'amount': 25,
                    'date': '2020-08-08',
                    'payment_plan_id': 1,
                },
            ],
            2: [
                {
                    'amount': 4312.67,
                    'date': '2020-08-08',
                    'payment_plan_id': 2,
                },
            ],
            3: [
                {
                    'amount': 1230.085,
                    'date': '2020-08-01',
                    'payment_plan_id': 3,
                },
                {
                    'amount': 1230.085,
                    'date': '2020-08-08',
                    'payment_plan_id': 3,
                },
                {
                    'amount': 1230.085,
                    'date': '2020-08-15',
                    'payment_plan_id': 3,
                },
            ],
        }

    def test_add_is_in_payment_plan(self) -> None:
        # 0: paid off
        # 1: in plan, not paid off
        # 2: in plan, not paid off
        # 3: in plan, not paid off
        # 4: no plan
        expected: List[Dict[str, Union[bool, Number]]] = [
            {
                'amount': 123.46,
                'id': 0,
                'is_in_payment_plan': False,
            },
            {
                'amount': 100,
                'id': 1,
                'is_in_payment_plan': True,
            },
            {
                'amount': 4920.34,
                'id': 2,
                'is_in_payment_plan': True,
            },
            {
                'amount': 12938,
                'id': 3,
                'is_in_payment_plan': True,
            },
            {
                'amount': 9238.02,
                'id': 4,
                'is_in_payment_plan': False,
            },
        ]
        actual: List[Dict[str, Union[bool, Number]]] = add_is_in_payment_plan(
            self.debts,
            self.debt_ids_to_plans,
            self.plan_ids_to_payments,
        )
        self.assertEqual(actual, expected)

    def test_add_remaining_amount(self) -> None:
        # 0: plan amount = 102.5, total paid = 102.5, remaining = 0
        # 1: plan amount = 100, total paid = 50, remaining = 50
        # 2: plan amount = 4920.34, total paid = 4312.67, remaining = 607.67
        # 3: plan amount = 4312.67, total paid = 3690.255, remaining = 622.415
        # 4: no plan
        expected: List[Dict[str, Union[bool, Number]]] = [
            {
                'amount': 123.46,
                'id': 0,
                'remaining_amount': 0,
            },
            {
                'amount': 100,
                'id': 1,
                'remaining_amount': 50,
            },
            {
                'amount': 4920.34,
                'id': 2,
                'remaining_amount': 607.6700000000001, # float precision
            },
            {
                'amount': 12938,
                'id': 3,
                'remaining_amount': 622.415,
            },
            {
                'amount': 9238.02,
                'id': 4,
                'remaining_amount': 9238.02,
            },
        ]
        actual: List[Dict[str, Union[bool, Number]]] = add_remaining_amount(
            self.debts,
            self.debt_ids_to_plans,
            self.plan_ids_to_payments,
        )
        self.assertEqual(actual, expected)

    def test_add_next_payment_due_date(self) -> None:
        # 0: paid off
        # 1: latest scheduled payment on 2020-08-08
        # 2: no scheduled payments
        # 3: latest scheduled payment on 2020-08-15
        # 4: no plan
        expected: List[Dict[str, Union[bool, Number]]] = [
            {
                'amount': 123.46,
                'id': 0,
                'next_payment_due_date': None,
            },
            {
                'amount': 100,
                'id': 1,
                'next_payment_due_date': '2020-08-15',
            },
            {
                'amount': 4920.34,
                'id': 2,
                'next_payment_due_date': '2020-01-01',
            },
            {
                'amount': 12938,
                'id': 3,
                'next_payment_due_date': '2020-08-22',
            },
            {
                'amount': 9238.02,
                'id': 4,
                'next_payment_due_date': None,
            },
        ]
        actual: List[Dict[str, Union[Number, str]]] = (
            add_next_payment_due_date(
                self.debts,
                self.debt_ids_to_plans,
                self.plan_ids_to_payments,
            )
        )
        self.assertEqual(actual, expected)
