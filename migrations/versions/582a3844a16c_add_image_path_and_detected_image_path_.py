"""Add image_path and detected_image_path to detections

Revision ID: 582a3844a16c
Revises: 1552d1a212d7
Create Date: 2025-11-26 11:13:45.806334
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '582a3844a16c'
down_revision = '1552d1a212d7'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns as nullable first to avoid breaking existing rows
    with op.batch_alter_table('detections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_path', sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column('detected_image_path', sa.String(length=300), nullable=True))

    # Original uploaded images
    op.execute("""
        UPDATE detections
        SET image_path = CASE
            WHEN detection_type = 'pothole' THEN 'uploads/pothole/default.png'
            WHEN detection_type = 'waste' THEN 'uploads/waste/default.png'
        END
        WHERE image_path IS NULL
    """)
    # Detected images
    op.execute("""
        UPDATE detections
        SET detected_image_path = CASE
            WHEN detection_type = 'pothole' THEN 'storage/pothole/detected/default.png'
            WHEN detection_type = 'waste' THEN 'storage/waste/detected/default.png'
        END
        WHERE detected_image_path IS NULL
    """)

    # Now make image_path NOT NULL for future rows
    with op.batch_alter_table('detections', schema=None) as batch_op:
        batch_op.alter_column('image_path', nullable=False)


def downgrade():
    with op.batch_alter_table('detections', schema=None) as batch_op:
        batch_op.drop_column('detected_image_path')
        batch_op.drop_column('image_path')
