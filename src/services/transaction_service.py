from src.repositories.item_repository import ItemRepository
from src.repositories.transaction_repository import TransactionRepository


class TransactionService:
    def __init__(self) -> None:
        self.repo = TransactionRepository()
        self.item_repo = ItemRepository()

    def create_purchase(self, supplier_id: int, rows: list[dict], notes: str = "") -> int:
        if not rows:
            raise ValueError("Purchase items required")
        return self.repo.create_purchase(supplier_id, rows, notes)

    def create_sale(self, customer_id: int, rows: list[dict], notes: str = "") -> int:
        if not rows:
            raise ValueError("Sale items required")
        for row in rows:
            item = self.item_repo.get_item(row["item_id"])
            if not item or item["quantity"] < row["quantity"]:
                raise ValueError("ناکافی اسٹاک")
        return self.repo.create_sale(customer_id, rows, notes)

    def get_latest_transaction_note(self) -> str:
        return self.repo.get_latest_transaction_note()

    def save_daily_rates(self, tola: float, gram: float, tezabi: float) -> None:
        """Save daily gold rates"""
        self.repo.save_daily_rates(tola, gram, tezabi)

    def save_transaction(self, receipt_data: dict) -> int:
        """Save transaction receipt"""
        return self.repo.save_transaction(receipt_data)

    def get_next_receipt_number(self) -> int:
        """Get next available receipt number"""
        return self.repo.get_next_receipt_number()

    def get_transaction_by_receipt_number(self, receipt_number: int) -> dict:
        """Fetch transaction by receipt number"""
        return self.repo.get_transaction_by_receipt_number(receipt_number)
