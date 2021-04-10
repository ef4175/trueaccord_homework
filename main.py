import json
import os
import sys
from collections import defaultdict
from numbers import Number
from typing import Dict, List, Union
from urllib import request

from helpers import (
    add_is_in_payment_plan,
    add_remaining_amount,
    add_next_payment_due_date,
)


def fetch(url: str, default_encoding: str = 'utf-8') -> str:
    with request.urlopen(url) as response:
        body: bytes = response.read()
        encoding: str = response.headers.get_content_charset(default_encoding)
        decoded_body: str = body.decode(encoding)
        return decoded_body

if __name__ == '__main__':
    debts_url: str = os.environ['DEBTS_URL']
    payment_plans_url: str = os.environ['PAYMENT_PLANS_URL']
    payments_url: str = os.environ['PAYMENTS_URL']

    debts_json: str = fetch(debts_url)
    payment_plans_json: str = fetch(payment_plans_url)
    payments_json: str = fetch(payments_url)

    debts: List[Dict[str, Number]] = json.loads(debts_json)
    payment_plans: List[Dict[str, Union[Number, str]]] = json.loads(
        payment_plans_json,
    )
    payments: List[Dict[str, Union[Number, str]]] = json.loads(payments_json)

    debt_ids_to_plans: Dict[int, Dict[str, Union[Number, str]]] = {
        plan['debt_id']: plan for plan in payment_plans
    }
    plan_ids_to_payments: Dict[int, List[Dict[str, Union[Number, str]]]] = (
        defaultdict(list)
    )
    for payment in payments:
        plan_id: int = payment['payment_plan_id']
        plan_ids_to_payments[plan_id].append(payment)

    debts_plus_is_in_payment_plan: List[Dict[str, Union[bool, Number]]] = (
        add_is_in_payment_plan(debts, debt_ids_to_plans, plan_ids_to_payments)
    )
    debts_plus_remaining_amount: List[Dict[str, Union[bool, Number]]] = (
        add_remaining_amount(
            debts_plus_is_in_payment_plan,
            debt_ids_to_plans,
            plan_ids_to_payments,
        )
    )
    debts_plus_next_due_date: List[Dict[str, Union[bool, Number, str]]] = (
        add_next_payment_due_date(
            debts_plus_remaining_amount,
            debt_ids_to_plans,
            plan_ids_to_payments,
        )
    )

    for debt in debts_plus_next_due_date:
        debt_as_serialized_json: str = json.dumps(debt)
        sys.stdout.write(f'{debt_as_serialized_json}\n')
        sys.stdout.flush()
