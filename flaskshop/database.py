# -*- coding: utf-8 -*-
"""Database module, including the SQLAlchemy database object and DB-related utilities."""
import datetime

from .extensions import db

# Alias common SQLAlchemy names
Column = db.Column
relationship = db.relationship


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named ``id`` to any declarative-mapped class."""

    __table_args__ = {"extend_existing": True}

    id = Column(db.Integer(), primary_key=True)
    created_at = Column(db.DateTime(), default=datetime.datetime.utcnow, index=True)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        class_ = type(self)
        return f"<{class_.__module__}.{class_.__name__}(id={self.id})>"

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if any(
                (
                        isinstance(record_id, (str, bytes)) and record_id.isdigit(),
                        isinstance(record_id, (int, float)),
                )
        ):
            return cls.query.get(int(record_id))
        return None

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = cls.query.filter_by(**kwargs).first()
        if instance:
            return instance, False
        else:
            instance = cls.create(**kwargs)
            return instance, True

    def to_dict(self):
        return self.__dict__.copy()


def reference_col(tablename, nullable=True, pk_name="id", **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    return Column(
        db.ForeignKey(
            f"{tablename}.{pk_name}",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=nullable,
        **kwargs,
    )
