"""initial schema

Revision ID: 20261115_0001
Revises:
Create Date: 2026-11-15
"""

from alembic import op
import sqlalchemy as sa


revision = "20261115_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    role = sa.Enum("owner", "manager", "accountant", name="role")
    greenhouse_status = sa.Enum("active", "inactive", name="greenhousestatus")
    crop = sa.Enum("tomato", "pepper", "zucchini", "cucumber", name="crop")
    cycle_status = sa.Enum("planned", "active", "completed", "cancelled", name="cropcyclestatus")
    sale_channel = sa.Enum("wholesaler", "market", "distributor", "other", name="salechannel")
    expense_category = sa.Enum(
        "seeds_plants",
        "fertilizer",
        "water",
        "energy",
        "labor",
        "equipment",
        "maintenance",
        "transport",
        "packaging",
        "other",
        name="expensecategory",
    )
    expense_scope = sa.Enum("whole_farm", "greenhouse", "crop_cycle", name="expensescope")

    role.create(op.get_bind(), checkfirst=True)
    greenhouse_status.create(op.get_bind(), checkfirst=True)
    crop.create(op.get_bind(), checkfirst=True)
    cycle_status.create(op.get_bind(), checkfirst=True)
    sale_channel.create(op.get_bind(), checkfirst=True)
    expense_category.create(op.get_bind(), checkfirst=True)
    expense_scope.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", role, nullable=False),
        sa.Column("locale", sa.String(5), nullable=False, server_default="en"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_role", "users", ["role"])

    op.create_table(
        "greenhouses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("area_m2", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", greenhouse_status, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "crop_cycles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("greenhouse_id", sa.String(36), sa.ForeignKey("greenhouses.id"), nullable=False),
        sa.Column("crop", crop, nullable=False),
        sa.Column("planting_date", sa.Date(), nullable=False),
        sa.Column("expected_end_date", sa.Date(), nullable=True),
        sa.Column("status", cycle_status, nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_crop_cycles_greenhouse_id", "crop_cycles", ["greenhouse_id"])
    op.create_index("ix_crop_cycles_status", "crop_cycles", ["status"])
    op.create_index("ix_crop_cycles_crop", "crop_cycles", ["crop"])

    op.create_table(
        "harvest_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("crop_cycle_id", sa.String(36), sa.ForeignKey("crop_cycles.id"), nullable=False),
        sa.Column("harvest_date", sa.Date(), nullable=False),
        sa.Column("quantity_kg", sa.Numeric(14, 3), nullable=False),
        sa.Column("quality_grade", sa.String(30), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_harvest_events_crop_cycle_id", "harvest_events", ["crop_cycle_id"])

    op.create_table(
        "customers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("contact_ref", sa.String(180), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "sales",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sale_date", sa.Date(), nullable=False),
        sa.Column("customer_id", sa.String(36), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("crop_cycle_id", sa.String(36), sa.ForeignKey("crop_cycles.id"), nullable=False),
        sa.Column("quantity_kg", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit_price_mad", sa.Numeric(14, 2), nullable=False),
        sa.Column("total_mad", sa.Numeric(14, 2), nullable=False),
        sa.Column("channel", sale_channel, nullable=True),
        sa.Column("external_reference", sa.String(120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(120), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_sales_idempotency_key"),
    )

    op.create_table(
        "expenses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("category", expense_category, nullable=False),
        sa.Column("amount_mad", sa.Numeric(14, 2), nullable=False),
        sa.Column("scope", expense_scope, nullable=False),
        sa.Column("greenhouse_id", sa.String(36), sa.ForeignKey("greenhouses.id"), nullable=True),
        sa.Column("crop_cycle_id", sa.String(36), sa.ForeignKey("crop_cycles.id"), nullable=True),
        sa.Column("supplier_reference", sa.String(160), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(120), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_expenses_idempotency_key"),
    )

    op.create_table(
        "financial_analyses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("cutoff_month", sa.String(7), nullable=False),
        sa.Column("facts", sa.JSON(), nullable=False),
        sa.Column("forecast", sa.JSON(), nullable=False),
        sa.Column("narrative_en", sa.Text(), nullable=False),
        sa.Column("narrative_ar", sa.Text(), nullable=False),
        sa.Column("source_hash", sa.String(128), nullable=False),
        sa.Column("model_version", sa.String(32), nullable=False),
        sa.Column("stale", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("actor_id", sa.String(36), nullable=True),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("field_names", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "incidents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("alert_name", sa.String(120), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("actions", sa.JSON(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "incidents",
        "audit_events",
        "financial_analyses",
        "expenses",
        "sales",
        "customers",
        "harvest_events",
        "crop_cycles",
        "greenhouses",
        "users",
    ]:
        op.drop_table(table)

    for enum_name in [
        "expensescope",
        "expensecategory",
        "salechannel",
        "cropcyclestatus",
        "crop",
        "greenhousestatus",
        "role",
    ]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
