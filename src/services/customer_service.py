from src.repositories.customer_repository import CustomerRepository
from src.repositories.receipt_repository import ReceiptRepository


class CustomerService:
    def __init__(self) -> None:
        self.customers = CustomerRepository()
        self.receipts = ReceiptRepository()

    def add(self, name: str, mobile: str = "", address: str = "", code: str | None = None) -> int:
        if not name.strip():
            raise ValueError("نام لازمی ہے")
        return self.customers.add(name.strip(), mobile.strip(), address.strip(), code)

    def update(self, customer_id: int, name: str, mobile: str = "", address: str = "") -> int:
        if not name.strip():
            raise ValueError("نام لازمی ہے")
        return self.customers.update(customer_id, name.strip(), mobile.strip(), address.strip())

    def search(self, query: str):
        return self.customers.search(query.strip())

    def list_all(self):
        return self.customers.list_all()

    def get(self, customer_id: int):
        return self.customers.get(customer_id)

    def save_receipt(self, payload: dict) -> int:
        return self.receipts.save(payload)

    def get_receipt(self, receipt_no: int):
        return self.receipts.get_by_receipt_no(receipt_no)

    def next_receipt_no(self) -> int:
        return self.receipts.next_receipt_no()

    def totals_by_type(self) -> dict:
        return self.receipts.totals_by_type()
