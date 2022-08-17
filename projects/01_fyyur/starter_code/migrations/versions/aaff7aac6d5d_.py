"""empty message

Revision ID: aaff7aac6d5d
Revises: 46f400060266
Create Date: 2022-08-16 17:21:44.687704

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aaff7aac6d5d'
down_revision = '46f400060266'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genres', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'genres')
    # ### end Alembic commands ###
