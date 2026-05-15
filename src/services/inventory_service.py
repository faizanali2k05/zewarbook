from src.repositories.item_repository import ItemRepository


class InventoryService:
    def __init__(self) -> None:
        self.repo = ItemRepository()

    def save_item(self, payload: dict, item_id: int | None = None):
        if not payload["sku"] or not payload["name_urdu"]:
            raise ValueError("SKU اور نام لازمی ہیں")
        if item_id:
            self.repo.update_item(item_id, payload)
            return item_id
        return self.repo.add_item(payload)

    def list_items(self, query: str = ""):
        return self.repo.list_items(query)

    def low_stock(self):
        return self.repo.low_stock_items()
