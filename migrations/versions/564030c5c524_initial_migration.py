"""Initial migration.

Revision ID: 564030c5c524
Revises: 
Create Date: 2024-11-05 00:59:25.205019

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '564030c5c524'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tbl_docentes_tutorados')
    with op.batch_alter_table('push_subscription', schema=None) as batch_op:
        batch_op.alter_column('endpoint',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
        batch_op.alter_column('keys_p256dh',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
        batch_op.alter_column('keys_auth',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)

    with op.batch_alter_table('tbl_alumnos_agregados', schema=None) as batch_op:
        batch_op.alter_column('id_usuario',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('id_alumno',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('tbl_registro_acceso_alumno', schema=None) as batch_op:
        batch_op.alter_column('codigo_qr_alumno',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)

    with op.batch_alter_table('tbl_registro_acceso_docente', schema=None) as batch_op:
        batch_op.alter_column('codigo_qr',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tbl_registro_acceso_docente', schema=None) as batch_op:
        batch_op.alter_column('codigo_qr',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)

    with op.batch_alter_table('tbl_registro_acceso_alumno', schema=None) as batch_op:
        batch_op.alter_column('codigo_qr_alumno',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)

    with op.batch_alter_table('tbl_alumnos_agregados', schema=None) as batch_op:
        batch_op.alter_column('id_alumno',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('id_usuario',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('push_subscription', schema=None) as batch_op:
        batch_op.alter_column('keys_auth',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
        batch_op.alter_column('keys_p256dh',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
        batch_op.alter_column('endpoint',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)

    op.create_table('tbl_docentes_tutorados',
    sa.Column('id_docente_tutorados', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre_docente_tutorado', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id_docente_tutorados', name='tbl_docentes_tutorados_pkey')
    )
    # ### end Alembic commands ###