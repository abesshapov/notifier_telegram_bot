"""Worker base class."""
from abc import ABC, abstractmethod


class BaseWorker(ABC):
    """Abstract base class for workers."""

    @abstractmethod
    async def run(self, *args, **kwargs) -> None:
        """Run worker."""
