from datetime import datetime

from app.models import Batch, OrderLine


def make_batch_and_line(
    sku: str, batch_quantity: int, line_quantity: int
) -> tuple[Batch, OrderLine]:
    batch = Batch("batch-001", sku, batch_quantity, eta=datetime.today())
    line = OrderLine("order-123", sku, line_quantity)
    return batch, line


def test_batch_can_allocate_line_if_available_greater_than_required() -> None:
    large_batch, small_line = make_batch_and_line("SMALL-TABLE", 20, 2)
    assert large_batch.can_allocate(small_line) is True


def test_batch_cannot_allocate_line_if_available_smaller_than_required() -> None:
    small_batch, large_line = make_batch_and_line("SMALL-TABLE", 2, 20)
    assert small_batch.can_allocate(large_line) is False


def test_batch_can_allocate_line_if_available_equal_to_required() -> None:
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line) is True


def test_batch_cannot_allocate_line_if_skus_do_not_match() -> None:
    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert batch.can_allocate(different_sku_line) is False


def test_batch_can_deallocate_allocated_lines() -> None:
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20


def test_allocation_is_idempotent() -> None:
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18
