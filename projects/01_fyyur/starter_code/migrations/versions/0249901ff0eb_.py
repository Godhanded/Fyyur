"""empty message

Revision ID: 0249901ff0eb
Revises: aaff7aac6d5d
Create Date: 2022-08-16 17:32:51.139397

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0249901ff0eb'
down_revision = 'aaff7aac6d5d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('venue', 'genres',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venue', 'genres',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###
