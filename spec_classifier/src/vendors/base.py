from abc import ABC, abstractmethod
from typing import List, Tuple


class VendorAdapter(ABC):
    @abstractmethod
    def parse(self, filepath: str) -> Tuple[List[dict], int]:
        """
        Возвращает (rows, header_row_index).
        rows: list[dict], каждый dict содержит поля строки + '__row_index__' (1-based).
        header_row_index: 0-based индекс строки заголовка в исходном файле.
        """
        pass

    @abstractmethod
    def normalize(self, raw_rows: List[dict]) -> list:
        """
        Возвращает list с объектами совместимыми с NormalizedRow.
        Обязательные поля (core contract):
          source_row_index, row_kind, group_name, group_id, product_name,
          module_name, option_name, option_id, skus (list[str]), qty (int), option_price (float).
        """
        pass

    @abstractmethod
    def get_rules_file(self) -> str:
        """Путь к YAML-файлу правил для этого вендора."""
        pass
