# Kan Extension 2: ORM Patterns & SQLAlchemy Design

## Overview
Second Kan extension exploring Object-Relational Mapping as an adjunction between the category of Objects and the category of Relations, with deep SQLAlchemy implementation patterns.

## Categorical Framework

### The ORM Adjunction
- **Left Adjoint L**: Objects → Relations (serialization)
- **Right Adjoint R**: Relations → Objects (hydration)
- **Unit η**: id → R ∘ L (object creation from database)
- **Counit ε**: L ∘ R → id (database synchronization)

### Natural Transformations
- **Lazy Loading**: Deferred computation functor
- **Eager Loading**: Immediate computation functor
- **Hybrid Properties**: Computed attributes as derived morphisms

## Core ORM Patterns

### 1. Advanced Model Design

```python
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship, backref, validates, column_property
from sqlalchemy.sql import func, select, case
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime
import re

Base = declarative_base()

class TimestampMixin:
    """Reusable timestamp mixin - Functor pattern"""
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class SoftDeleteMixin:
    """Soft delete pattern - Endofunctor on entities"""
    @declared_attr
    def deleted_at(cls):
        return Column(DateTime, nullable=True, index=True)

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()

    def restore(self):
        self.deleted_at = None

class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(120), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    metadata_json = Column(JSON, default={})

    # Relationships with different loading strategies
    posts = relationship('Post', back_populates='author',
                        cascade='all, delete-orphan',
                        lazy='dynamic')  # Dynamic relationship

    comments = relationship('Comment', back_populates='user',
                          lazy='select')  # Default lazy loading

    roles = relationship('Role', secondary='user_roles',
                        back_populates='users',
                        lazy='subquery')  # Subquery eager loading

    # Hybrid property - works both in Python and SQL
    @hybrid_property
    def full_name(self):
        """Computed property - morphism in object category"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @full_name.expression
    def full_name(cls):
        """SQL expression - morphism in relation category"""
        return case(
            [(cls.first_name != None, cls.first_name + ' ' + cls.last_name)],
            else_=cls.username
        )

    # Validation - maintaining invariants
    @validates('email')
    def validate_email(self, key, email):
        """Email validation - preserves structure"""
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise ValueError('Invalid email address')
        return email.lower()

    # Column property for computed columns
    post_count = column_property(
        select([func.count(Post.id)])
        .where(Post.user_id == id)
        .correlate_except(Post)
        .scalar_subquery()
    )

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Post(Base, TimestampMixin):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    title = Column(String(200), nullable=False)
    content = Column(Text)
    status = Column(String(20), default='draft')
    view_count = Column(Integer, default=0)

    # Relationships
    author = relationship('User', back_populates='posts')
    tags = relationship('Tag', secondary='post_tags', back_populates='posts')
    comments = relationship('Comment', back_populates='post',
                          cascade='all, delete-orphan',
                          order_by='Comment.created_at')

    # Association proxy for simpler tag access
    tag_names = association_proxy('tags', 'name')

    # Constraints
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_created_at', 'created_at'),
        CheckConstraint("status IN ('draft', 'published', 'archived')",
                       name='check_post_status'),
    )

    @hybrid_property
    def is_published(self):
        return self.status == 'published'

    @is_published.expression
    def is_published(cls):
        return cls.status == 'published'

    @hybrid_method
    def has_min_views(self, min_views):
        """Hybrid method with parameters"""
        return self.view_count >= min_views

    @has_min_views.expression
    def has_min_views(cls, min_views):
        return cls.view_count >= min_views

# Association table for many-to-many
post_tags = Table('post_tags', Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE')),
    UniqueConstraint('post_id', 'tag_id', name='uq_post_tag')
)
```

### 2. Advanced Relationship Patterns

```python
from sqlalchemy.orm import remote, foreign
from sqlalchemy.ext.declarative import declarative_base

class RelationshipPatterns:
    """Advanced relationship configurations"""

    # Self-referential relationship (tree structure)
    class Category(Base):
        __tablename__ = 'categories'

        id = Column(Integer, primary_key=True)
        name = Column(String(50))
        parent_id = Column(Integer, ForeignKey('categories.id'))

        # Self-referential relationship
        children = relationship('Category',
                              backref=backref('parent', remote_side=[id]),
                              cascade='all, delete-orphan')

        def get_ancestors(self):
            """Traverse up the tree"""
            ancestors = []
            current = self.parent
            while current:
                ancestors.append(current)
                current = current.parent
            return ancestors

        def get_descendants(self):
            """Traverse down the tree"""
            descendants = []
            def traverse(node):
                for child in node.children:
                    descendants.append(child)
                    traverse(child)
            traverse(self)
            return descendants

    # Polymorphic relationships (single table inheritance)
    class Content(Base):
        __tablename__ = 'content'

        id = Column(Integer, primary_key=True)
        type = Column(String(50))
        title = Column(String(200))
        body = Column(Text)

        __mapper_args__ = {
            'polymorphic_identity': 'content',
            'polymorphic_on': type
        }

    class Article(Content):
        author = Column(String(100))

        __mapper_args__ = {
            'polymorphic_identity': 'article'
        }

    class Video(Content):
        duration = Column(Integer)
        url = Column(String(500))

        __mapper_args__ = {
            'polymorphic_identity': 'video'
        }

    # Association object pattern (many-to-many with extra data)
    class UserRole(Base):
        __tablename__ = 'user_roles'

        user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
        role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
        granted_at = Column(DateTime, default=func.now())
        granted_by = Column(Integer, ForeignKey('users.id'))

        user = relationship('User', foreign_keys=[user_id])
        role = relationship('Role')
        granter = relationship('User', foreign_keys=[granted_by])

        # Add custom methods to association
        def is_active(self):
            """Check if role grant is still valid"""
            # Add expiration logic here
            return True
```

### 3. Query Optimization Patterns

```python
from sqlalchemy.orm import joinedload, subqueryload, selectinload, contains_eager
from sqlalchemy.orm import lazyload, noload, raiseload
from sqlalchemy import and_, or_, not_

class QueryOptimizationPatterns:
    """Query optimization strategies as functors"""

    def __init__(self, session):
        self.session = session

    def eager_loading_strategies(self):
        """Different eager loading patterns"""

        # 1. Joined loading - single query with JOIN
        users_joined = self.session.query(User)\
            .options(joinedload(User.posts))\
            .all()

        # 2. Subquery loading - two queries
        users_subquery = self.session.query(User)\
            .options(subqueryload(User.posts))\
            .all()

        # 3. Select IN loading - better for one-to-many
        users_selectin = self.session.query(User)\
            .options(selectinload(User.posts))\
            .all()

        # 4. Nested eager loading
        users_nested = self.session.query(User)\
            .options(
                selectinload(User.posts)
                .selectinload(Post.comments)
            )\
            .all()

        return {
            'joined': users_joined,
            'subquery': users_subquery,
            'selectin': users_selectin,
            'nested': users_nested
        }

    def contains_eager_pattern(self):
        """Manual join with contains_eager"""
        # When you want to filter the eager loaded collection
        active_users_with_published_posts = self.session.query(User)\
            .join(User.posts)\
            .filter(Post.status == 'published')\
            .options(contains_eager(User.posts))\
            .all()

        return active_users_with_published_posts

    def lazy_loading_control(self):
        """Control lazy loading behavior"""

        # Raise exception on lazy load (good for APIs)
        strict_users = self.session.query(User)\
            .options(raiseload('*'))\
            .all()

        # Completely disable loading
        no_posts_users = self.session.query(User)\
            .options(noload(User.posts))\
            .all()

        return strict_users, no_posts_users

    def query_batching(self, user_ids, batch_size=100):
        """Batch queries to avoid memory issues"""
        for i in range(0, len(user_ids), batch_size):
            batch_ids = user_ids[i:i + batch_size]
            yield self.session.query(User)\
                .filter(User.id.in_(batch_ids))\
                .all()

    def optimize_pagination(self, page, per_page=20):
        """Efficient pagination with window functions"""
        # Using row_number() for consistent pagination
        from sqlalchemy import literal_column

        subquery = self.session.query(
            Post.id,
            func.row_number().over(
                order_by=Post.created_at.desc()
            ).label('row_num')
        ).subquery()

        posts = self.session.query(Post)\
            .join(subquery, Post.id == subquery.c.id)\
            .filter(
                and_(
                    subquery.c.row_num > (page - 1) * per_page,
                    subquery.c.row_num <= page * per_page
                )
            )\
            .all()

        return posts
```

### 4. Session Management Patterns

```python
from contextlib import contextmanager
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging

class SessionManagementPatterns:
    """Session management as monad operations"""

    def __init__(self, engine):
        self.engine = engine
        self.SessionFactory = sessionmaker(bind=engine)
        self.ScopedSession = scoped_session(self.SessionFactory)

    @contextmanager
    def session_scope(self):
        """Provide transactional scope - monadic bind operation"""
        session = self.SessionFactory()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Session error: {e}")
            raise
        finally:
            session.close()

    @contextmanager
    def bulk_insert_scope(self):
        """Optimized scope for bulk operations"""
        session = self.SessionFactory()
        session.execute('SET synchronous_commit = OFF')  # PostgreSQL optimization
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise
        finally:
            session.execute('SET synchronous_commit = ON')
            session.close()

    def nested_transaction(self, session):
        """Savepoint-based nested transactions"""
        @contextmanager
        def nested():
            trans = session.begin_nested()
            try:
                yield
                trans.commit()
            except Exception:
                trans.rollback()
                raise

        return nested()

    def retry_on_deadlock(self, func, max_retries=3):
        """Retry logic for deadlock resolution"""
        import time
        from sqlalchemy.exc import OperationalError

        for attempt in range(max_retries):
            try:
                with self.session_scope() as session:
                    return func(session)
            except OperationalError as e:
                if 'deadlock detected' in str(e) and attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
```

### 5. Advanced Query Builder

```python
from sqlalchemy.sql import Select
from typing import List, Dict, Any, Optional

class AdvancedQueryBuilder:
    """Composable query builder - Free monad pattern"""

    def __init__(self, session, model):
        self.session = session
        self.model = model
        self.query = session.query(model)
        self.filters = []
        self.joins = []
        self.orders = []

    def filter_by(self, **kwargs):
        """Add filters - functor mapping"""
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                self.filters.append(getattr(self.model, key) == value)
        return self

    def filter_in(self, field, values):
        """IN clause filter"""
        if hasattr(self.model, field):
            self.filters.append(getattr(self.model, field).in_(values))
        return self

    def filter_like(self, field, pattern):
        """LIKE pattern filter"""
        if hasattr(self.model, field):
            self.filters.append(getattr(self.model, field).like(pattern))
        return self

    def filter_between(self, field, start, end):
        """BETWEEN filter"""
        if hasattr(self.model, field):
            attr = getattr(self.model, field)
            self.filters.append(and_(attr >= start, attr <= end))
        return self

    def join_model(self, relationship, filters=None):
        """Add join with optional filters"""
        self.joins.append((relationship, filters))
        return self

    def order_by(self, field, desc=False):
        """Add ordering"""
        if hasattr(self.model, field):
            attr = getattr(self.model, field)
            self.orders.append(attr.desc() if desc else attr)
        return self

    def build(self):
        """Compile the query - evaluate the free monad"""
        q = self.query

        # Apply joins
        for relationship, filters in self.joins:
            if filters:
                q = q.join(relationship).filter(filters)
            else:
                q = q.join(relationship)

        # Apply filters
        if self.filters:
            q = q.filter(and_(*self.filters))

        # Apply ordering
        if self.orders:
            q = q.order_by(*self.orders)

        return q

    def paginate(self, page, per_page=20):
        """Add pagination"""
        q = self.build()
        return q.limit(per_page).offset((page - 1) * per_page)

    def execute(self):
        """Execute and return results"""
        return self.build().all()

    def count(self):
        """Get count without fetching results"""
        return self.build().count()

    def exists(self):
        """Check if any results exist"""
        return self.session.query(self.build().exists()).scalar()
```

### 6. Caching Patterns

```python
from functools import wraps
from sqlalchemy.ext.baked import bakery
import pickle
import hashlib

class ORMCachingPatterns:
    """Caching strategies for ORM queries"""

    def __init__(self, session, redis_client):
        self.session = session
        self.redis = redis_client
        self.bakery = bakery()

    def baked_query_pattern(self, user_id):
        """Baked queries for repeated query patterns"""
        baked_query = self.bakery(lambda s: s.query(User))
        baked_query += lambda q: q.filter(User.id == user_id)

        result = baked_query(self.session).one_or_none()
        return result

    def cache_key(self, model, **filters):
        """Generate cache key from model and filters"""
        key_parts = [model.__tablename__]
        for k, v in sorted(filters.items()):
            key_parts.append(f"{k}:{v}")
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def cached_get(self, model, **filters):
        """Get with caching"""
        cache_key = self.cache_key(model, **filters)

        # Try cache first
        cached = self.redis.get(cache_key)
        if cached:
            return pickle.loads(cached)

        # Query database
        result = self.session.query(model).filter_by(**filters).first()

        if result:
            # Cache the result
            self.redis.setex(cache_key, 3600, pickle.dumps(result))

        return result

    def cached_query(self, ttl=3600):
        """Decorator for caching query results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from function and arguments
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                cache_key = hashlib.md5(cache_key.encode()).hexdigest()

                # Check cache
                cached = self.redis.get(cache_key)
                if cached:
                    return pickle.loads(cached)

                # Execute query
                result = func(*args, **kwargs)

                # Cache result
                self.redis.setex(cache_key, ttl, pickle.dumps(result))

                return result
            return wrapper
        return decorator

    def invalidate_cache(self, model, **filters):
        """Invalidate cache entries"""
        pattern = f"{model.__tablename__}:*"
        for key in self.redis.scan_iter(match=pattern):
            self.redis.delete(key)
```

### 7. Event Listeners and Hooks

```python
from sqlalchemy import event
from sqlalchemy.orm import Session
from datetime import datetime

class ORMEventPatterns:
    """Event-driven patterns - Observer pattern in ORM"""

    @staticmethod
    def setup_audit_log():
        """Automatic audit logging"""

        @event.listens_for(Base, 'before_insert', propagate=True)
        def receive_before_insert(mapper, connection, target):
            """Log before insert"""
            if hasattr(target, 'created_by'):
                target.created_by = get_current_user_id()
            if hasattr(target, 'created_at'):
                target.created_at = datetime.utcnow()

        @event.listens_for(Base, 'before_update', propagate=True)
        def receive_before_update(mapper, connection, target):
            """Log before update"""
            if hasattr(target, 'updated_by'):
                target.updated_by = get_current_user_id()
            if hasattr(target, 'updated_at'):
                target.updated_at = datetime.utcnow()

        @event.listens_for(Session, 'after_flush')
        def receive_after_flush(session, context):
            """Create audit trail after flush"""
            for obj in session.new:
                create_audit_entry('INSERT', obj)
            for obj in session.dirty:
                create_audit_entry('UPDATE', obj)
            for obj in session.deleted:
                create_audit_entry('DELETE', obj)

    @staticmethod
    def setup_cache_invalidation():
        """Automatic cache invalidation on changes"""

        @event.listens_for(Session, 'after_commit')
        def receive_after_commit(session):
            """Invalidate cache after successful commit"""
            for obj in session.identity_map.values():
                cache_key = generate_cache_key(obj)
                redis_client.delete(cache_key)

    @staticmethod
    def setup_search_index_sync():
        """Sync with search index (e.g., Elasticsearch)"""

        @event.listens_for(Post, 'after_insert')
        def index_post(mapper, connection, target):
            """Add to search index"""
            add_to_search_index('posts', target)

        @event.listens_for(Post, 'after_update')
        def update_post_index(mapper, connection, target):
            """Update search index"""
            update_search_index('posts', target)

        @event.listens_for(Post, 'after_delete')
        def remove_post_index(mapper, connection, target):
            """Remove from search index"""
            remove_from_search_index('posts', target.id)
```

### 8. Testing ORM Code

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch

class TestORMPatterns:
    """Testing strategies for ORM code"""

    @pytest.fixture
    def test_session(self):
        """Create test database session"""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        session = Session(engine)
        yield session
        session.close()

    @pytest.fixture
    def sample_user(self, test_session):
        """Create sample user for testing"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        test_session.add(user)
        test_session.commit()
        return user

    def test_hybrid_property(self, sample_user):
        """Test hybrid property works in both Python and SQL"""
        # Python side
        assert sample_user.full_name == 'Test User'

        # SQL side
        session = Session.object_session(sample_user)
        result = session.query(User.full_name).first()
        assert result[0] == 'Test User'

    def test_relationship_loading(self, test_session, sample_user):
        """Test different loading strategies"""
        # Create posts
        for i in range(5):
            post = Post(
                user_id=sample_user.id,
                title=f'Post {i}',
                content=f'Content {i}'
            )
            test_session.add(post)
        test_session.commit()

        # Test dynamic loading
        assert sample_user.posts.count() == 5

        # Test eager loading
        user = test_session.query(User)\
            .options(joinedload(User.posts))\
            .filter(User.id == sample_user.id)\
            .first()

        # No additional queries should be made
        with patch.object(test_session, 'execute') as mock_execute:
            posts = user.posts
            assert len(posts) == 5
            mock_execute.assert_not_called()

    def test_soft_delete(self, test_session, sample_user):
        """Test soft delete functionality"""
        # Soft delete
        sample_user.soft_delete()
        test_session.commit()

        assert sample_user.is_deleted
        assert sample_user.deleted_at is not None

        # Should still exist in database
        user = test_session.query(User)\
            .filter(User.id == sample_user.id)\
            .first()
        assert user is not None

        # Restore
        sample_user.restore()
        test_session.commit()
        assert not sample_user.is_deleted
```

## Integration with Luxor Marketplace

### SQLAlchemy Skill Integration
```python
class LuxorSQLAlchemyIntegration:
    """Integration with Luxor's SQLAlchemy skill"""

    def __init__(self):
        self.engine = self.setup_engine()
        self.Session = sessionmaker(bind=self.engine)

    def setup_engine(self):
        """Configure SQLAlchemy engine with best practices"""
        return create_engine(
            'postgresql://user:pass@localhost/db',
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,  # Verify connections
            echo=False,  # Set to True for debugging
            isolation_level='READ_COMMITTED',
            connect_args={
                'connect_timeout': 10,
                'application_name': 'luxor_orm'
            }
        )

    def create_session(self):
        """Create a new session instance"""
        return self.Session()

    def bulk_operations(self, objects):
        """Efficient bulk operations"""
        with self.session_scope() as session:
            session.bulk_insert_mappings(User, objects)
            session.commit()
```

## Performance Profiling

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging

class ORMProfiler:
    """Profile ORM operations"""

    def __init__(self):
        self.query_times = []

    def setup_profiling(self):
        """Setup query profiling"""

        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())

        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - conn.info['query_start_time'].pop(-1)
            self.query_times.append({
                'statement': statement,
                'time': total,
                'parameters': parameters
            })

            if total > 0.5:  # Log slow queries
                logging.warning(f"Slow query ({total:.2f}s): {statement[:100]}...")

    def get_statistics(self):
        """Get profiling statistics"""
        if not self.query_times:
            return {}

        times = [q['time'] for q in self.query_times]
        return {
            'total_queries': len(self.query_times),
            'total_time': sum(times),
            'avg_time': sum(times) / len(times),
            'slowest_query': max(self.query_times, key=lambda x: x['time'])
        }
```

## Conclusion

This second Kan extension demonstrates ORM patterns as categorical adjunctions between Objects and Relations, providing:

1. **Model Design**: Advanced patterns with mixins, hybrid properties, and constraints
2. **Relationship Management**: Complex relationships including self-referential and polymorphic
3. **Query Optimization**: Multiple loading strategies and query building patterns
4. **Session Management**: Transactional scopes and retry logic
5. **Caching Strategies**: Multiple levels of caching for performance
6. **Event-Driven Patterns**: Hooks and listeners for cross-cutting concerns
7. **Testing Strategies**: Comprehensive testing approaches for ORM code

The framework shows how ORM acts as a bidirectional functor, preserving structure while transforming between object and relational representations.