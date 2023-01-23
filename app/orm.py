import sqlalchemy as sa
from sqlalchemy.orm import mapper, relationship

from app import models

meta_data = sa.MetaData()

order_lines = sa.Table(
    "order_lines",
    meta_data,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("sku", sa.String(255)),
    sa.Column("quantity", sa.Integer, nullable=False),
    sa.Column("order_id", sa.String(255)),
)

batches = sa.Table(
    "batches",
    meta_data,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("reference", sa.String(255)),
    sa.Column("sku", sa.String(255)),
    sa.Column("_purchased_quantity", sa.Integer, nullable=False),
    sa.Column("eta", sa.DateTime, nullable=True),
)

allocations = sa.Table(
    "allocations",
    meta_data,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("orderline_id", sa.Integer, sa.ForeignKey("order_lines.id")),
    sa.Column("batch_id", sa.Integer, sa.ForeignKey("batches.id")),
)


def start_mappers() -> None:
    lines_mapper = mapper(models.OrderLine, order_lines)
    mapper(
        models.Batch,
        batches,
        properties={
            "_allocations": relationship(
                lines_mapper,
                secondary=allocations,
                collection_class=set,
            )
        },
    )
