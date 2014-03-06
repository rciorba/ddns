import uuid

from sqlalchemy import create_engine, orm
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID

from ddns import config


cfg = config.get_config()
_engine_debug = cfg['DEBUG'].lower() == "true"
engine = create_engine(cfg['SQL_ENGINE'], echo=_engine_debug)
Base = declarative_base()
table_prefix = cfg.get('table_prefix', 'ddns_')


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

class Manager(object):
    def __init__(self, cls, session):
        self.cls = cls
        self.session = session

    def _filter(self, **kwargs):
        query = self.session.query(self.cls)
        return query.filter_by(**kwargs)

    def filter(self, **kwargs):
        return self._filter(**kwargs)

    def get(self, **kwargs):
        try:
            return self._filter(**kwargs).one()
        except orm.exc.NoResultFound:
            return None

    def add(self, obj):
        self.session.add(obj)

    def new(self, **kwargs):
        obj = self.cls(**kwargs)
        self.add(obj)
        return obj

    def commit(self):
        """commit session. beware session may be shared among multiple managers"""
        self.session.commit()

    def count(self, **kwargs):
        return self._filter(**kwargs).count()

    def __repr__(self):
        cls = type(self)
        return "<%s.%s<%s> at Ox%x>" % (cls.__module__, cls.__name__, self.cls.__name__, id(self))


def fk(kls, field_name="id"):
    return ForeignKey("{}.{}".format(kls.__tablename__, field_name))


class User(Base):
    __tablename__ = table_prefix + "user"
    id = Column(GUID, primary_key=True)
    username = Column(String(2048), nullable=False)
    password = Column(String(2048), nullable=False)


class Keys(Base):
    __tablename__ = table_prefix + "key"
    id = Column(GUID, primary_key=True)
    user = Column(GUID, fk(User), nullable=False)
    key = Column(String(2048), nullable=False)


class Domain(Base):
    __tablename__ = table_prefix + "domain"
    id = Column(GUID, primary_key=True)
    name = Column(String(2048), nullable=False)
    a = Column(String(2048), nullable=False)
    aaaa = Column(String(2048), nullable=False)


class Host(Base):
    __tablename__ = table_prefix + "host"
    id = Column(GUID, primary_key=True)
    user = Column(GUID, fk(User), nullable=False)
    name = Column(String(2048), nullable=False)
    a = Column(String(2048), nullable=False)
    aaaa = Column(String(2048), nullable=False)


def sync(engine_=engine, drop=False):
    if drop:
        Base.metadata.drop_all(engine_)
    Base.metadata.create_all(engine_)


def get_managers(session=None, engine_=engine, Manager=Manager):
    if session is None:
        session = orm.sessionmaker(bind=engine_)()
    users = Manager(User, session)
    keys = Manager(Key, session)
    hosts = Manager(Host, session)
    return users, keys, hosts


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--drop", default=False, dest="drop",
                        action="store_true", help="Drop tables?")
    args = parser.parse_args()
    sync(engine, drop=args.drop)
