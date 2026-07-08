"""drop whitelist, encrypt router password

Revision ID: a1b2c3d4e5f6
Revises: f73869c5de17
Create Date: 2026-07-08 18:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

import crypto_utils

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f73869c5de17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('whitelist')

    with op.batch_alter_table('routers') as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('password_encrypted', sa.String(), nullable=True))

    connection = op.get_bind()
    routers = connection.execute(sa.text('SELECT id, password FROM routers')).fetchall()
    for router_id, password in routers:
        connection.execute(
            sa.text('UPDATE routers SET password_hash = :hash, password_encrypted = :enc WHERE id = :id'),
            {
                'hash': crypto_utils.hash_password(password),
                'enc': crypto_utils.encrypt_password(password),
                'id': router_id,
            },
        )

    with op.batch_alter_table('routers') as batch_op:
        batch_op.alter_column('password_hash', nullable=False)
        batch_op.alter_column('password_encrypted', nullable=False)
        batch_op.drop_constraint('uq_router_host_password', type_='unique')
        batch_op.create_unique_constraint('uq_router_host_password_hash', ['host', 'password_hash'])
        batch_op.drop_column('password')


def downgrade() -> None:
    with op.batch_alter_table('routers') as batch_op:
        batch_op.add_column(sa.Column('password', sa.String(), nullable=True))

    connection = op.get_bind()
    routers = connection.execute(sa.text('SELECT id, password_encrypted FROM routers')).fetchall()
    for router_id, password_encrypted in routers:
        connection.execute(
            sa.text('UPDATE routers SET password = :password WHERE id = :id'),
            {'password': crypto_utils.decrypt_password(password_encrypted), 'id': router_id},
        )

    with op.batch_alter_table('routers') as batch_op:
        batch_op.alter_column('password', nullable=False)
        batch_op.drop_constraint('uq_router_host_password_hash', type_='unique')
        batch_op.create_unique_constraint('uq_router_host_password', ['host', 'password'])
        batch_op.drop_column('password_hash')
        batch_op.drop_column('password_encrypted')

    op.create_table(
        'whitelist',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
    )
