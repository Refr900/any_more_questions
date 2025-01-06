from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class User:
    id: int
    model: str
    last_used: datetime
    uses_count: int
    dialog: List[Dict[str, str]]
