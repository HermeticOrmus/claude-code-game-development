# Kan Extension 3: Migration Architecture & Alembic Strategies

## Overview
Third Kan extension exploring database migrations as morphisms in the category of database schemas, with comprehensive Alembic patterns and multi-database architecture strategies.

## Categorical Framework

### Schema Evolution Category
- **Objects**: Database schemas S₁, S₂, ..., Sₙ
- **Morphisms**: Migrations M: Sᵢ → Sⱼ
- **Composition**: Sequential migration application
- **Identity**: No-op migration

### Migration Functors
- **Forward Migration**: F: Schema_v1 → Schema_v2
- **Rollback**: G: Schema_v2 → Schema_v1
- **Adjunction**: Forward ⊣ Rollback (when reversible)

## Core Migration Patterns

### 1. Advanced Alembic Configuration

```python
# alembic.ini configuration
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import os
import sys

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from app.database.models import Base
from app.config import DatabaseConfig

class AlembicConfiguration:
    """Advanced Alembic configuration patterns"""

    def __init__(self):
        self.config = context.config
        self.target_metadata = Base.metadata
        fileConfig(self.config.config_file_name)

    def run_migrations_offline(self):
        """Run migrations in 'offline' mode - generate SQL scripts"""
        url = self.config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=self.target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            render_as_batch=True,  # SQLite compatibility
            compare_type=True,  # Detect column type changes
            compare_server_default=True,  # Detect default changes
        )

        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online(self):
        """Run migrations in 'online' mode - direct database connection"""

        # Custom configuration for different environments
        configuration = self.config.get_section(self.config.config_ini_section)
        configuration['sqlalchemy.url'] = DatabaseConfig.get_url()

        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,  # Don't maintain connections
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=self.target_metadata,
                render_as_batch=True,
                compare_type=True,
                compare_server_default=True,
                transaction_per_migration=True,  # Separate transaction per migration
                # Custom comparison functions
                compare_foreign_keys=True,
                include_schemas=True,
                include_object=self.include_object,
                process_revision_directives=self.process_revision_directives,
            )

            with context.begin_transaction():
                context.run_migrations()

    def include_object(self, object, name, type_, reflected, compare_to):
        """Filter objects to include in migrations"""
        # Skip certain schemas or tables
        if type_ == "table" and name.startswith("temp_"):
            return False
        if hasattr(object, "schema") and object.schema == "audit":
            return False
        return True

    def process_revision_directives(self, context, revision, directives):
        """Process and modify migration scripts before creation"""
        if getattr(context.config.cmd_opts, 'autogenerate', False):
            script = directives[0]

            # Add custom imports
            script.imports.add("from sqlalchemy.dialects import postgresql")

            # Add custom upgrade/downgrade logic
            if script.upgrade_ops.is_empty():
                directives[:] = []  # Don't create empty migrations
```

### 2. Complex Migration Patterns

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from datetime import datetime

class ComplexMigrationPatterns:
    """Advanced migration patterns for complex schema changes"""

    @staticmethod
    def safe_column_rename(table_name, old_name, new_name):
        """Safe column rename with backward compatibility"""

        def upgrade():
            # Step 1: Add new column
            op.add_column(table_name, sa.Column(new_name, sa.String()))

            # Step 2: Copy data
            connection = op.get_bind()
            connection.execute(
                f"UPDATE {table_name} SET {new_name} = {old_name}"
            )

            # Step 3: Add deprecation notice (as comment)
            op.execute(
                f"COMMENT ON COLUMN {table_name}.{old_name} IS "
                f"'DEPRECATED: Use {new_name} instead'"
            )

        def downgrade():
            # Copy data back
            connection = op.get_bind()
            connection.execute(
                f"UPDATE {table_name} SET {old_name} = {new_name}"
            )

            # Remove new column
            op.drop_column(table_name, new_name)

        return upgrade, downgrade

    @staticmethod
    def safe_not_null_constraint(table_name, column_name, default_value):
        """Add NOT NULL constraint with data backfill"""

        def upgrade():
            # Step 1: Update NULL values
            connection = op.get_bind()
            connection.execute(
                f"UPDATE {table_name} SET {column_name} = %s "
                f"WHERE {column_name} IS NULL",
                (default_value,)
            )

            # Step 2: Add NOT NULL constraint
            op.alter_column(
                table_name,
                column_name,
                nullable=False,
                server_default=str(default_value)
            )

        def downgrade():
            op.alter_column(
                table_name,
                column_name,
                nullable=True,
                server_default=None
            )

        return upgrade, downgrade

    @staticmethod
    def data_migration_pattern(upgrade_func, downgrade_func):
        """Pattern for data migrations with verification"""

        def upgrade():
            # Create temporary table for rollback
            op.create_table(
                '_migration_backup',
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('table_name', sa.String(100)),
                sa.Column('data', sa.JSON),
                sa.Column('created_at', sa.DateTime, default=datetime.utcnow)
            )

            try:
                # Run upgrade function
                connection = op.get_bind()
                result = upgrade_func(connection)

                # Verify migration
                if not verify_migration(connection, result):
                    raise Exception("Migration verification failed")

                # Clean up backup
                op.drop_table('_migration_backup')

            except Exception as e:
                # Restore from backup
                restore_from_backup(connection)
                raise e

        def downgrade():
            connection = op.get_bind()
            downgrade_func(connection)

        return upgrade, downgrade

    @staticmethod
    def batch_update_migration(table_name, update_func, batch_size=1000):
        """Update large tables in batches to avoid locks"""

        def upgrade():
            connection = op.get_bind()

            # Get total count
            result = connection.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = result.scalar()

            # Process in batches
            for offset in range(0, total_rows, batch_size):
                batch_query = f"""
                    UPDATE {table_name}
                    SET updated_at = NOW()
                    WHERE id IN (
                        SELECT id FROM {table_name}
                        ORDER BY id
                        LIMIT {batch_size} OFFSET {offset}
                    )
                """
                connection.execute(batch_query)

                # Allow other transactions to proceed
                connection.execute("COMMIT")
                connection.execute("BEGIN")

        return upgrade
```

### 3. Multi-Database Migration Strategy

```python
from enum import Enum
from typing import List, Dict, Any
import json

class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    ORACLE = "oracle"

class MultiDatabaseMigration:
    """Handle migrations across different database types"""

    def __init__(self, database_type: DatabaseType):
        self.database_type = database_type
        self.dialect_handlers = {
            DatabaseType.POSTGRESQL: PostgreSQLMigration(),
            DatabaseType.MYSQL: MySQLMigration(),
            DatabaseType.SQLITE: SQLiteMigration(),
            DatabaseType.ORACLE: OracleMigration()
        }

    def create_index(self, table_name, columns, unique=False, partial=None):
        """Create index with database-specific optimizations"""
        handler = self.dialect_handlers[self.database_type]
        return handler.create_index(table_name, columns, unique, partial)

    def add_json_column(self, table_name, column_name):
        """Add JSON column with appropriate type"""
        handler = self.dialect_handlers[self.database_type]
        return handler.add_json_column(table_name, column_name)

class PostgreSQLMigration:
    """PostgreSQL-specific migration patterns"""

    def create_index(self, table_name, columns, unique=False, partial=None):
        index_name = f"idx_{table_name}_{'_'.join(columns)}"

        if partial:
            # Partial index for PostgreSQL
            return f"""
            CREATE {('UNIQUE' if unique else '')} INDEX CONCURRENTLY {index_name}
            ON {table_name} ({', '.join(columns)})
            WHERE {partial}
            """
        else:
            return f"""
            CREATE {('UNIQUE' if unique else '')} INDEX CONCURRENTLY {index_name}
            ON {table_name} ({', '.join(columns)})
            """

    def add_json_column(self, table_name, column_name):
        return f"ALTER TABLE {table_name} ADD COLUMN {column_name} JSONB"

    def add_array_column(self, table_name, column_name, array_type):
        """PostgreSQL array support"""
        return f"ALTER TABLE {table_name} ADD COLUMN {column_name} {array_type}[]"

    def create_materialized_view(self, view_name, query):
        """Create materialized view for performance"""
        return f"""
        CREATE MATERIALIZED VIEW {view_name} AS
        {query}
        WITH DATA
        """

class MySQLMigration:
    """MySQL-specific migration patterns"""

    def create_index(self, table_name, columns, unique=False, partial=None):
        index_name = f"idx_{table_name}_{'_'.join(columns)}"

        # MySQL doesn't support partial indexes directly
        if partial:
            # Use generated column as workaround
            return f"""
            ALTER TABLE {table_name}
            ADD COLUMN _partial_idx BOOLEAN GENERATED ALWAYS AS ({partial}) STORED,
            ADD {('UNIQUE' if unique else '')} INDEX {index_name}
            ({', '.join(columns)}, _partial_idx)
            """
        else:
            return f"""
            ALTER TABLE {table_name}
            ADD {('UNIQUE' if unique else '')} INDEX {index_name} ({', '.join(columns)})
            """

    def add_json_column(self, table_name, column_name):
        return f"ALTER TABLE {table_name} ADD COLUMN {column_name} JSON"

    def optimize_table(self, table_name):
        """MySQL-specific optimization"""
        return f"OPTIMIZE TABLE {table_name}"

class SQLiteMigration:
    """SQLite-specific migration patterns with limitations"""

    def create_index(self, table_name, columns, unique=False, partial=None):
        index_name = f"idx_{table_name}_{'_'.join(columns)}"

        if partial:
            return f"""
            CREATE {('UNIQUE' if unique else '')} INDEX {index_name}
            ON {table_name} ({', '.join(columns)})
            WHERE {partial}
            """
        else:
            return f"""
            CREATE {('UNIQUE' if unique else '')} INDEX {index_name}
            ON {table_name} ({', '.join(columns)})
            """

    def add_json_column(self, table_name, column_name):
        # SQLite stores JSON as TEXT
        return f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT"

    def rename_column(self, table_name, old_name, new_name):
        """SQLite 3.25+ supports column rename"""
        return f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name}"
```

### 4. Migration Testing Framework

```python
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

class MigrationTestFramework:
    """Comprehensive migration testing"""

    def __init__(self):
        self.test_db_url = "postgresql://test_user:test_pass@localhost/test_db"
        self.engine = create_engine(self.test_db_url)
        self.alembic_cfg = Config("alembic.ini")

    def test_migration_up_down(self, revision):
        """Test migration upgrade and downgrade"""

        # Upgrade to target revision
        command.upgrade(self.alembic_cfg, revision)

        # Verify schema after upgrade
        inspector = inspect(self.engine)
        tables_after_upgrade = inspector.get_table_names()

        # Downgrade
        command.downgrade(self.alembic_cfg, "-1")

        # Verify schema after downgrade
        inspector = inspect(self.engine)
        tables_after_downgrade = inspector.get_table_names()

        return {
            'upgrade_tables': tables_after_upgrade,
            'downgrade_tables': tables_after_downgrade
        }

    def test_migration_data_integrity(self, revision, test_data):
        """Test that migrations preserve data integrity"""

        # Insert test data
        Session = sessionmaker(bind=self.engine)
        session = Session()

        for record in test_data:
            session.execute(record)
        session.commit()

        # Run migration
        command.upgrade(self.alembic_cfg, revision)

        # Verify data still exists and is correct
        results = session.execute("SELECT * FROM test_table")
        migrated_data = results.fetchall()

        # Compare with original
        assert len(migrated_data) == len(test_data)

        session.close()

    def test_migration_performance(self, revision):
        """Test migration performance on large datasets"""
        import time

        # Create large dataset
        self.create_large_dataset()

        start_time = time.time()
        command.upgrade(self.alembic_cfg, revision)
        duration = time.time() - start_time

        assert duration < 60, f"Migration took {duration}s, exceeding 60s limit"

        return duration

    def test_concurrent_migration_safety(self, revision):
        """Test migration behavior with concurrent connections"""
        import threading

        def run_query():
            engine = create_engine(self.test_db_url)
            with engine.connect() as conn:
                conn.execute("SELECT 1")

        # Start concurrent queries
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=run_query)
            thread.start()
            threads.append(thread)

        # Run migration
        command.upgrade(self.alembic_cfg, revision)

        # Wait for threads
        for thread in threads:
            thread.join()

    def create_large_dataset(self, rows=100000):
        """Create large dataset for performance testing"""
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Bulk insert
        data = [{"id": i, "value": f"test_{i}"} for i in range(rows)]
        session.bulk_insert_mappings(TestTable, data)
        session.commit()
        session.close()
```

### 5. Zero-Downtime Migration Strategies

```python
from contextlib import contextmanager
import time

class ZeroDowntimeMigration:
    """Strategies for zero-downtime database migrations"""

    def __init__(self, primary_db, replica_db):
        self.primary_db = primary_db
        self.replica_db = replica_db

    def expand_contract_migration(self, expansion_func, contraction_func):
        """Expand-Contract pattern for backward compatibility"""

        # Phase 1: Expand - Add new structure alongside old
        print("Phase 1: Expansion")
        with self.get_connection(self.primary_db) as conn:
            expansion_func(conn)

        # Wait for application deployment
        print("Waiting for application deployment...")
        self.wait_for_deployment()

        # Phase 2: Migrate - Move data to new structure
        print("Phase 2: Data Migration")
        self.migrate_data_incrementally()

        # Phase 3: Contract - Remove old structure
        print("Phase 3: Contraction")
        with self.get_connection(self.primary_db) as conn:
            contraction_func(conn)

    def blue_green_migration(self, migration_func):
        """Blue-Green deployment pattern for migrations"""

        # Setup green database (new schema)
        green_db = self.setup_green_database()

        # Apply migration to green database
        with self.get_connection(green_db) as conn:
            migration_func(conn)

        # Sync data from blue to green
        self.sync_databases(self.primary_db, green_db)

        # Switch traffic to green
        self.switch_traffic(green_db)

        # Keep blue as backup
        self.archive_database(self.primary_db)

    def rolling_migration(self, migration_func, shard_count=4):
        """Rolling migration across database shards"""

        shards = self.get_database_shards(shard_count)

        for i, shard in enumerate(shards):
            print(f"Migrating shard {i+1}/{shard_count}")

            # Remove shard from pool
            self.remove_from_pool(shard)

            # Apply migration
            with self.get_connection(shard) as conn:
                migration_func(conn)

            # Add back to pool
            self.add_to_pool(shard)

            # Wait before next shard
            time.sleep(30)

    def online_schema_change(self, table_name, change_func):
        """Online schema change using triggers"""

        # Step 1: Create shadow table with new schema
        shadow_table = f"{table_name}_new"
        self.create_shadow_table(table_name, shadow_table, change_func)

        # Step 2: Create triggers to sync changes
        self.create_sync_triggers(table_name, shadow_table)

        # Step 3: Copy existing data in batches
        self.copy_data_in_batches(table_name, shadow_table)

        # Step 4: Atomic table swap
        self.atomic_table_swap(table_name, shadow_table)

        # Step 5: Cleanup
        self.cleanup_migration_artifacts(table_name)

    def create_sync_triggers(self, source_table, target_table):
        """Create triggers to sync data during migration"""

        triggers = f"""
        -- INSERT trigger
        CREATE TRIGGER sync_insert_{source_table}
        AFTER INSERT ON {source_table}
        FOR EACH ROW
        BEGIN
            INSERT INTO {target_table} SELECT * FROM NEW;
        END;

        -- UPDATE trigger
        CREATE TRIGGER sync_update_{source_table}
        AFTER UPDATE ON {source_table}
        FOR EACH ROW
        BEGIN
            DELETE FROM {target_table} WHERE id = OLD.id;
            INSERT INTO {target_table} SELECT * FROM NEW;
        END;

        -- DELETE trigger
        CREATE TRIGGER sync_delete_{source_table}
        AFTER DELETE ON {source_table}
        FOR EACH ROW
        BEGIN
            DELETE FROM {target_table} WHERE id = OLD.id;
        END;
        """

        return triggers

    def copy_data_in_batches(self, source, target, batch_size=10000):
        """Copy data in batches to minimize lock time"""

        with self.get_connection(self.primary_db) as conn:
            # Get total count
            result = conn.execute(f"SELECT MAX(id) FROM {source}")
            max_id = result.scalar() or 0

            for start_id in range(0, max_id, batch_size):
                end_id = min(start_id + batch_size, max_id)

                # Copy batch
                conn.execute(f"""
                    INSERT INTO {target}
                    SELECT * FROM {source}
                    WHERE id > {start_id} AND id <= {end_id}
                """)

                # Small delay to reduce load
                time.sleep(0.1)

    def atomic_table_swap(self, old_table, new_table):
        """Atomically swap tables"""

        swap_sql = f"""
        BEGIN;
        ALTER TABLE {old_table} RENAME TO {old_table}_old;
        ALTER TABLE {new_table} RENAME TO {old_table};
        COMMIT;
        """

        with self.get_connection(self.primary_db) as conn:
            conn.execute(swap_sql)

    @contextmanager
    def get_connection(self, database):
        """Get database connection context"""
        conn = database.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
```

### 6. Migration Monitoring and Rollback

```python
import logging
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class MigrationState:
    """Track migration state"""
    revision: str
    status: str  # pending, running, completed, failed, rolled_back
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    metrics: Dict[str, Any]

class MigrationMonitor:
    """Monitor and manage migration execution"""

    def __init__(self, database_url):
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)

    def execute_with_monitoring(self, revision, migration_func):
        """Execute migration with monitoring and automatic rollback"""

        state = MigrationState(
            revision=revision,
            status='pending',
            started_at=None,
            completed_at=None,
            error_message=None,
            metrics={}
        )

        try:
            # Pre-migration checks
            if not self.pre_migration_checks():
                raise Exception("Pre-migration checks failed")

            # Start migration
            state.status = 'running'
            state.started_at = datetime.utcnow()
            self.save_state(state)

            # Execute migration
            result = migration_func()

            # Post-migration validation
            if not self.post_migration_validation(result):
                raise Exception("Post-migration validation failed")

            # Success
            state.status = 'completed'
            state.completed_at = datetime.utcnow()
            state.metrics = self.collect_metrics()
            self.save_state(state)

            self.logger.info(f"Migration {revision} completed successfully")

        except Exception as e:
            # Failure - attempt rollback
            state.status = 'failed'
            state.error_message = str(e)
            self.save_state(state)

            self.logger.error(f"Migration {revision} failed: {e}")

            # Automatic rollback
            if self.should_auto_rollback(state):
                self.rollback_migration(revision)
                state.status = 'rolled_back'
                self.save_state(state)

            raise

    def pre_migration_checks(self):
        """Verify system is ready for migration"""

        checks = {
            'database_accessible': self.check_database_connection(),
            'sufficient_disk_space': self.check_disk_space(),
            'low_database_load': self.check_database_load(),
            'no_long_running_queries': self.check_long_queries(),
            'backup_recent': self.check_recent_backup()
        }

        failed_checks = [k for k, v in checks.items() if not v]

        if failed_checks:
            self.logger.error(f"Pre-migration checks failed: {failed_checks}")
            return False

        return True

    def post_migration_validation(self, result):
        """Validate migration was successful"""

        validations = {
            'schema_correct': self.validate_schema(),
            'data_integrity': self.validate_data_integrity(),
            'indexes_present': self.validate_indexes(),
            'constraints_valid': self.validate_constraints(),
            'performance_acceptable': self.validate_performance()
        }

        failed_validations = [k for k, v in validations.items() if not v]

        if failed_validations:
            self.logger.error(f"Post-migration validation failed: {failed_validations}")
            return False

        return True

    def collect_metrics(self):
        """Collect migration metrics"""

        return {
            'duration_seconds': self.get_migration_duration(),
            'rows_affected': self.get_rows_affected(),
            'disk_usage_change': self.get_disk_usage_change(),
            'index_count': self.get_index_count(),
            'table_count': self.get_table_count()
        }

    def should_auto_rollback(self, state):
        """Determine if automatic rollback should occur"""

        # Don't auto-rollback if explicitly disabled
        if os.environ.get('DISABLE_AUTO_ROLLBACK') == 'true':
            return False

        # Auto-rollback for critical errors
        critical_errors = [
            'constraint violation',
            'data loss detected',
            'schema corruption'
        ]

        if state.error_message:
            for error in critical_errors:
                if error in state.error_message.lower():
                    return True

        return False

    def rollback_migration(self, revision):
        """Rollback to previous revision"""

        self.logger.info(f"Rolling back migration {revision}")

        # Use Alembic to rollback
        from alembic import command
        from alembic.config import Config

        cfg = Config("alembic.ini")
        command.downgrade(cfg, "-1")

        self.logger.info("Rollback completed")
```

### 7. Cross-Database Synchronization

```python
from typing import List, Dict
import asyncio
import aioboto3

class CrossDatabaseSync:
    """Synchronize schema changes across multiple databases"""

    def __init__(self, databases: List[Dict[str, Any]]):
        self.databases = databases
        self.primary = databases[0]  # First database is primary

    async def sync_schema_changes(self, migration_script):
        """Apply schema changes to all databases"""

        # Apply to primary first
        await self.apply_migration(self.primary, migration_script)

        # Apply to replicas in parallel
        tasks = []
        for db in self.databases[1:]:
            task = asyncio.create_task(
                self.apply_migration(db, migration_script)
            )
            tasks.append(task)

        # Wait for all replicas
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for failures
        failures = [r for r in results if isinstance(r, Exception)]
        if failures:
            await self.handle_sync_failure(failures)

        return results

    async def apply_migration(self, database, migration_script):
        """Apply migration to specific database"""

        connection = await self.get_async_connection(database)

        try:
            # Begin transaction
            await connection.execute("BEGIN")

            # Apply migration
            await connection.execute(migration_script)

            # Verify migration
            if await self.verify_migration(connection):
                await connection.execute("COMMIT")
            else:
                await connection.execute("ROLLBACK")
                raise Exception(f"Migration verification failed for {database['name']}")

        except Exception as e:
            await connection.execute("ROLLBACK")
            raise

        finally:
            await connection.close()

    async def verify_migration(self, connection):
        """Verify migration was applied correctly"""

        # Check table structure
        result = await connection.fetch("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)

        # Compare with expected schema
        return self.validate_schema_structure(result)

    async def handle_sync_failure(self, failures):
        """Handle synchronization failures"""

        # Log failures
        for failure in failures:
            self.logger.error(f"Sync failure: {failure}")

        # Attempt to restore consistency
        await self.restore_consistency()

        # Alert operations team
        await self.send_alert({
            'type': 'sync_failure',
            'failures': str(failures),
            'timestamp': datetime.utcnow()
        })

    async def restore_consistency(self):
        """Restore consistency across databases"""

        # Get schema from primary
        primary_schema = await self.get_schema(self.primary)

        # Apply to all replicas
        for db in self.databases[1:]:
            try:
                await self.apply_schema(db, primary_schema)
            except Exception as e:
                self.logger.error(f"Failed to restore consistency for {db['name']}: {e}")
```

## Integration with Luxor Marketplace

### Alembic Skill Integration
```python
class LuxorAlembicIntegration:
    """Integration with Luxor's Alembic skill"""

    def __init__(self):
        self.config = Config("alembic.ini")

    def generate_migration(self, message):
        """Generate new migration with Luxor standards"""
        from alembic import command

        # Generate migration with naming convention
        revision = command.revision(
            self.config,
            message=message,
            autogenerate=True
        )

        # Add Luxor metadata
        self.add_luxor_metadata(revision)

        return revision

    def add_luxor_metadata(self, revision):
        """Add Luxor-specific metadata to migration"""
        metadata = {
            'luxor_version': '1.0',
            'skill': 'alembic',
            'timestamp': datetime.utcnow().isoformat(),
            'author': os.environ.get('LUXOR_USER', 'unknown')
        }

        # Add metadata as comment in migration file
        migration_file = f"alembic/versions/{revision}.py"
        with open(migration_file, 'r') as f:
            content = f.read()

        with open(migration_file, 'w') as f:
            f.write(f"# Luxor Metadata: {json.dumps(metadata)}\n")
            f.write(content)
```

## Best Practices Summary

1. **Migration Safety**
   - Always test migrations on staging first
   - Include both upgrade and downgrade paths
   - Use transactions for atomic changes
   - Implement health checks before/after migration

2. **Performance Optimization**
   - Use CONCURRENTLY for index creation in PostgreSQL
   - Batch large data updates
   - Consider online schema change tools
   - Monitor migration duration and impact

3. **Version Control**
   - Keep migrations in version control
   - Use descriptive migration messages
   - Tag database schema versions
   - Document breaking changes

4. **Testing Strategy**
   - Test upgrade and rollback paths
   - Verify data integrity
   - Test with production-like data volumes
   - Test concurrent access during migration

5. **Monitoring**
   - Track migration execution time
   - Monitor database performance during migration
   - Set up alerts for failed migrations
   - Keep migration audit log

## Conclusion

This third Kan extension demonstrates migrations as morphisms between database schemas, providing:

1. **Advanced Alembic Configuration**: Comprehensive setup for production use
2. **Complex Migration Patterns**: Strategies for challenging schema changes
3. **Multi-Database Support**: Handling different database dialects
4. **Zero-Downtime Strategies**: Multiple patterns for continuous availability
5. **Testing Framework**: Comprehensive migration testing approaches
6. **Monitoring & Rollback**: Automated monitoring and recovery
7. **Cross-Database Sync**: Maintaining consistency across multiple databases

The framework treats migrations as composable transformations, ensuring safe and efficient schema evolution.