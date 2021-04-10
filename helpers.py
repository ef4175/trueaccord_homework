from datetime import date, datetime, timedelta
from numbers import Number
from typing import Dict, List, Optional, Union


FREQUENCIES: Dict[str, int] = {
    'WEEKLY': 7,
    'BI_WEEKLY': 14,
}

def add_is_in_payment_plan(
    debts: List[Dict[str, Number]],
    debt_ids_to_plans: Dict[int, Dict[str, Union[Number, str]]],
    plan_ids_to_payments: Dict[int, List[Dict[str, Union[Number, str]]]],
) -> List[Dict[str, Union[bool, Number]]]:
    def has_payment_plan(debt: Dict[str, Number]) -> bool:
        debt_id: int = debt['id']
        debt_has_payment_plan: bool = debt_id in debt_ids_to_plans
        return debt_has_payment_plan
    def is_paid_off(debt: Dict[str, Number]) -> bool:
        debt_id: int = debt['id']
        payment_plan: Dict[str, Union[Number, str]] = (
            debt_ids_to_plans[debt_id]
        )
        plan_id: int = payment_plan['id']
        payments: List[Dict[str, Union[Number, str]]] = (
            plan_ids_to_payments[plan_id]
        )
        total_amount_paid: float = (
            0 if len(payments) == 0 else sum(p['amount'] for p in payments)
        )
        amount_to_pay: float = payment_plan['amount_to_pay']
        plan_is_paid_off: bool = total_amount_paid >= amount_to_pay
        return plan_is_paid_off
    debts_plus_is_in_payment_plan: List[Dict[str, Union[bool, Number]]] = [
        {
            **debt,
            'is_in_payment_plan': (
                has_payment_plan(debt) and not is_paid_off(debt)
            ),
        }
        for debt in debts
    ]
    return debts_plus_is_in_payment_plan

def add_remaining_amount(
    debts: List[Dict[str, Number]],
    debt_ids_to_plans: Dict[int, Dict[str, Union[Number, str]]],
    plan_ids_to_payments: Dict[int, List[Dict[str, Union[Number, str]]]],
) -> List[Dict[str, Union[bool, Number]]]:
    def compute_remaining_amount(debt: Dict[str, Number]) -> float:
        debt_id: int = debt['id']
        if debt_id not in debt_ids_to_plans:
            return debt['amount']
        payment_plan: Dict[str, Union[Number, str]] = (
            debt_ids_to_plans[debt_id]
        )
        plan_id: int = payment_plan['id']
        payments: List[Dict[str, Union[Number, str]]] = (
            plan_ids_to_payments[plan_id]
        )
        total_amount_paid: float = (
            0 if len(payments) == 0 else sum(p['amount'] for p in payments)
        )
        amount_to_pay: float = payment_plan['amount_to_pay']
        remaining_amount: float = amount_to_pay - total_amount_paid
        non_negative_remaining_amount: float = max(0, remaining_amount)
        return non_negative_remaining_amount
    debts_plus_remaining_amount: List[Dict[str, Union[bool, Number]]] = [
        {
            **debt,
            'remaining_amount': compute_remaining_amount(debt),
        }
        for debt in debts
    ]
    return debts_plus_remaining_amount

def find_scheduled_payments(
    payment_plan: Dict[str, Union[Number, str]],
    payments_made: List[Dict[str, Union[Number, str]]],
    date_format: str = '%Y-%m-%d',
) -> List[Dict[str, Union[Number, str]]]:
    frequency: int = FREQUENCIES[payment_plan['installment_frequency']]
    plan_start_date: date = datetime.strptime(
        payment_plan['start_date'],
        date_format,
    ).date()
    def is_scheduled(payment: Dict[str, Union[Number, str]]) -> bool:
        payment_date: date = datetime.strptime(
            payment['date'],
            date_format,
        ).date()
        days_apart: int = (payment_date - plan_start_date).days
        return days_apart % frequency == 0
    scheduled_payments: List[Dict[str, Union[Number, str]]] = [
        payment for payment in payments_made if is_scheduled(payment)
    ]
    return scheduled_payments

def add_next_payment_due_date(
    debts: List[Dict[str, Number]],
    debt_ids_to_plans: Dict[int, Dict[str, Union[Number, str]]],
    plan_ids_to_payments: Dict[int, List[Dict[str, Union[Number, str]]]],
    date_format: str = '%Y-%m-%d',
) -> List[Dict[str, Union[bool, Number]]]:
    def get_next_payment_due_date(debt: Dict[str, Number]) -> Optional[str]:
        debt_id: int = debt['id']
        if debt_id not in debt_ids_to_plans:
            return None
        debt_id: int = debt['id']
        payment_plan: Dict[str, Union[Number, str]] = (
            debt_ids_to_plans[debt_id]
        )
        plan_id: int = payment_plan['id']
        payments: List[Dict[str, Union[Number, str]]] = (
            plan_ids_to_payments[plan_id]
        )
        total_amount_paid: float = (
            0 if len(payments) == 0 else sum(p['amount'] for p in payments)
        )
        amount_to_pay: float = payment_plan['amount_to_pay']
        plan_is_paid_off: bool = total_amount_paid >= amount_to_pay
        if plan_is_paid_off:
            return None
        scheduled_payments: List[Dict[str, Union[Number, str]]] = (
            find_scheduled_payments(payment_plan, payments, date_format)
        )
        if len(scheduled_payments) == 0:
            return payment_plan['start_date']
        latest_payment_date: str = max(p['date'] for p in scheduled_payments)
        frequency: int = FREQUENCIES[payment_plan['installment_frequency']]
        next_date: date = (
            datetime.strptime(latest_payment_date, date_format).date() +
            timedelta(days=frequency)
        )
        return next_date.strftime(date_format)
    debts_plus_next_payment_due_date: List[Dict[str, Union[bool, Number]]] = [
        {
            **debt,
            'next_payment_due_date': get_next_payment_due_date(debt),
        }
        for debt in debts
    ]
    return debts_plus_next_payment_due_date
