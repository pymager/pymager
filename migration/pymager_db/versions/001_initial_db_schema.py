from sqlalchemy import *
from migrate import *

meta = MetaData(migrate_engine)
abstract_item = Table('abstract_item', meta,
    Column('id', String(255), primary_key=True),
    Column('status', String(255), index=True, nullable=False),
    Column('last_status_change_date', DateTime, index=True, nullable=False),
    Column('width', Integer, index=True, nullable=False),
    Column('height', Integer, index=True, nullable=False),
    Column('format', String(255), index=True, nullable=False),
    Column('type', String(255), nullable=False)
)

original_image_metadata = Table('original_image_metadata', meta,
    Column('id', String(255), ForeignKey('abstract_item.id'), primary_key=True)
)

derived_image_metadata = Table('derived_image_metadata', meta,
    Column('id', String(255), ForeignKey('abstract_item.id'), primary_key=True),
    Column('original_image_metadata_id', String(255), ForeignKey('original_image_metadata.id', ondelete="CASCADE"))
)

def upgrade():
    abstract_item.create()
    original_image_metadata.create()
    derived_image_metadata.create()

#def downgrade():
#    derived_image_metadata.drop()
#    original_image_metadata.drop()
#    abstract_item.drop()


