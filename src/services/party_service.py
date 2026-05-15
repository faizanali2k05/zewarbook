from src.repositories.party_repository import PartyRepository


class PartyService:
    def __init__(self) -> None:
        self.repo = PartyRepository()

    def save_party(self, payload: dict):
        if not payload["name"]:
            raise ValueError("نام لازمی ہے")
        return self.repo.add_party(payload)

    def list_parties(self, party_type: str | None = None):
        return self.repo.list_parties(party_type)
