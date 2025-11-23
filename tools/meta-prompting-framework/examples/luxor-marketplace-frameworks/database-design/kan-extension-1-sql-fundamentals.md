# Kan Extension 1: SQL Fundamentals & Query Patterns

## Overview
First Kan extension focusing on foundational SQL operations, query composition patterns, and the categorical structure of relational algebra.

## Categorical Setup

### Base Category: **Tables**
- **Objects**: Database tables T₁, T₂, ..., Tₙ
- **Morphisms**: SQL queries Q: Tᵢ → Tⱼ
- **Composition**: Query chaining via CTEs and subqueries
- **Identity**: SELECT * FROM T

### Functor F: Tables → ResultSets
Maps tables to their query result sets with structure preservation.

## Core SQL Patterns

### 1. Basic CRUD Operations

```python
from sqlalchemy import create_engine, text, MetaData, Table
from contextlib import contextmanager
import pandas as pd

class SQLQueryBuilder:
    """Categorical query builder with composition support"""

    def __init__(self, engine):
        self.engine = engine
        self.metadata = MetaData()
        self.metadata.reflect(bind=engine)

    @contextmanager
    def transaction(self):
        """Transactional context manager"""
        conn = self.engine.connect()
        trans = conn.begin()
        try:
            yield conn
            trans.commit()
        except Exception:
            trans.rollback()
            raise
        finally:
            conn.close()

    def select(self, table_name, columns='*', where=None, order_by=None, limit=None):
        """Morphism: Table → ResultSet"""
        query_parts = [f"SELECT {columns}", f"FROM {table_name}"]

        if where:
            query_parts.append(f"WHERE {where}")
        if order_by:
            query_parts.append(f"ORDER BY {order_by}")
        if limit:
            query_parts.append(f"LIMIT {limit}")

        query = text(" ".join(query_parts))

        with self.engine.connect() as conn:
            result = conn.execute(query)
            return pd.DataFrame(result.fetchall(), columns=result.keys())

    def insert(self, table_name, **values):
        """Morphism: Values → Table"""
        columns = ", ".join(values.keys())
        placeholders = ", ".join([f":{k}" for k in values.keys()])
        query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING *")

        with self.transaction() as conn:
            result = conn.execute(query, values)
            return result.fetchone()

    def update(self, table_name, set_values, where):
        """Endomorphism: Table → Table"""
        set_clause = ", ".join([f"{k} = :{k}" for k in set_values.keys()])
        query = text(f"UPDATE {table_name} SET {set_clause} WHERE {where} RETURNING *")

        with self.transaction() as conn:
            result = conn.execute(query, set_values)
            return result.fetchall()

    def delete(self, table_name, where):
        """Morphism: Table → Table (subset)"""
        query = text(f"DELETE FROM {table_name} WHERE {where} RETURNING *")

        with self.transaction() as conn:
            result = conn.execute(query)
            return result.fetchall()
```

### 2. Join Patterns as Tensor Products

```python
class JoinOperations:
    """Joins as monoidal tensor products in the category of relations"""

    def __init__(self, engine):
        self.engine = engine

    def inner_join(self, left_table, right_table, on_condition):
        """Tensor product with intersection semantics"""
        query = text(f"""
            SELECT *
            FROM {left_table} AS l
            INNER JOIN {right_table} AS r
            ON {on_condition}
        """)

        with self.engine.connect() as conn:
            return pd.DataFrame(conn.execute(query).fetchall())

    def left_join(self, left_table, right_table, on_condition):
        """Left-biased tensor product"""
        query = text(f"""
            SELECT *
            FROM {left_table} AS l
            LEFT JOIN {right_table} AS r
            ON {on_condition}
        """)

        with self.engine.connect() as conn:
            return pd.DataFrame(conn.execute(query).fetchall())

    def full_outer_join(self, left_table, right_table, on_condition):
        """Full tensor product with null padding"""
        query = text(f"""
            SELECT *
            FROM {left_table} AS l
            FULL OUTER JOIN {right_table} AS r
            ON {on_condition}
        """)

        with self.engine.connect() as conn:
            return pd.DataFrame(conn.execute(query).fetchall())

    def cross_join(self, left_table, right_table):
        """Cartesian product - true tensor product"""
        query = text(f"""
            SELECT *
            FROM {left_table}
            CROSS JOIN {right_table}
        """)

        with self.engine.connect() as conn:
            return pd.DataFrame(conn.execute(query).fetchall())
```

### 3. Aggregation Patterns

```python
class AggregationPatterns:
    """Aggregations as functors from Relations to Statistics"""

    def __init__(self, engine):
        self.engine = engine

    def group_aggregate(self, table, group_by, aggregates):
        """
        Functor: Relation → AggregatedRelation

        Args:
            table: Source table name
            group_by: List of grouping columns
            aggregates: Dict of {alias: aggregate_expression}

        Example:
            group_aggregate('sales', ['product_id'],
                          {'total': 'SUM(amount)', 'count': 'COUNT(*)'})
        """
        group_clause = ", ".join(group_by)
        select_parts = group_by + [f"{expr} AS {alias}"
                                   for alias, expr in aggregates.items()]
        select_clause = ", ".join(select_parts)

        query = text(f"""
            SELECT {select_clause}
            FROM {table}
            GROUP BY {group_clause}
            ORDER BY {group_clause}
        """)

        with self.engine.connect() as conn:
            return pd.DataFrame(conn.execute(query).fetchall())

    def window_aggregation(self, table, partition_by, order_by, window_functions):
        """Window functions as local aggregations"""
        window_clause = f"PARTITION BY {partition_by} ORDER BY {order_by}"
        select_parts = ["*"] + [f"{func} OVER ({window_clause}) AS {alias}"
                               for alias, func in window_functions.items()]
        select_clause = ", ".join(select_parts)

        query = text(f"""
            SELECT {select_clause}
            FROM {table}
        """)

        with self.engine.connect() as conn:
            return pd.DataFrame(conn.execute(query).fetchall())

    def rolling_statistics(self, table, date_column, metrics, window_days=30):
        """Time-based rolling aggregations"""
        metric_calculations = []
        for alias, expression in metrics.items():
            metric_calculations.append(f"""
                {expression} OVER (
                    ORDER BY {date_column}
                    RANGE BETWEEN INTERVAL '{window_days} days' PRECEDING
                    AND CURRENT ROW
                ) AS {alias}
            """)

        query = text(f"""
            SELECT *,
                   {', '.join(metric_calculations)}
            FROM {table}
            ORDER BY {date_column}
        """)

        with self.engine.connect() as conn:
            return pd.DataFrame(conn.execute(query).fetchall())
```

### 4. CTE Composition Patterns

```python
class CTEComposition:
    """Common Table Expressions as morphism composition"""

    def __init__(self, engine):
        self.engine = engine
        self.ctes = []

    def add_cte(self, name, query):
        """Add a CTE to the composition chain"""
        self.ctes.append((name, query))
        return self

    def compose(self, final_query):
        """Compose all CTEs into final query"""
        if not self.ctes:
            return final_query

        cte_definitions = []
        for name, query in self.ctes:
            cte_definitions.append(f"{name} AS ({query})")

        full_query = f"""
        WITH {', '.join(cte_definitions)}
        {final_query}
        """

        return full_query

    def execute(self, final_query):
        """Execute the composed query"""
        composed = self.compose(final_query)
        with self.engine.connect() as conn:
            return pd.DataFrame(conn.execute(text(composed)).fetchall())

    def hierarchical_query(self, table, id_column, parent_column, root_condition):
        """Recursive CTE for hierarchical data"""
        query = f"""
        WITH RECURSIVE hierarchy AS (
            -- Base case: root nodes
            SELECT {id_column}, {parent_column}, 1 as level,
                   CAST({id_column} AS VARCHAR) as path
            FROM {table}
            WHERE {root_condition}

            UNION ALL

            -- Recursive case: child nodes
            SELECT t.{id_column}, t.{parent_column}, h.level + 1,
                   h.path || '/' || CAST(t.{id_column} AS VARCHAR)
            FROM {table} t
            INNER JOIN hierarchy h ON t.{parent_column} = h.{id_column}
        )
        SELECT * FROM hierarchy
        ORDER BY path
        """

        with self.engine.connect() as conn:
            return pd.DataFrame(conn.execute(text(query)).fetchall())
```

### 5. Query Optimization Patterns

```python
class QueryOptimizationPatterns:
    """Natural transformations for query optimization"""

    def __init__(self, engine):
        self.engine = engine

    def explain_analyze(self, query):
        """Analyze query execution plan"""
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"

        with self.engine.connect() as conn:
            result = conn.execute(text(explain_query))
            plan = result.fetchone()[0][0]  # Extract JSON plan
            return self.parse_execution_plan(plan)

    def parse_execution_plan(self, plan):
        """Parse and analyze execution plan"""
        return {
            'total_time': plan.get('Execution Time', 0),
            'planning_time': plan.get('Planning Time', 0),
            'nodes': self.extract_node_info(plan.get('Plan', {})),
            'optimization_hints': self.generate_hints(plan)
        }

    def extract_node_info(self, node):
        """Recursively extract node information"""
        info = {
            'type': node.get('Node Type'),
            'cost': node.get('Total Cost'),
            'rows': node.get('Plan Rows'),
            'actual_rows': node.get('Actual Rows'),
            'time': node.get('Actual Total Time')
        }

        if 'Plans' in node:
            info['children'] = [self.extract_node_info(child)
                              for child in node['Plans']]

        return info

    def generate_hints(self, plan):
        """Generate optimization hints based on plan"""
        hints = []
        root = plan.get('Plan', {})

        # Check for sequential scans on large tables
        if root.get('Node Type') == 'Seq Scan' and root.get('Actual Rows', 0) > 10000:
            hints.append(f"Consider adding index on {root.get('Relation Name')}")

        # Check for nested loops with high iteration count
        if root.get('Node Type') == 'Nested Loop':
            if root.get('Actual Loops', 0) > 1000:
                hints.append("High nested loop count - consider hash join")

        return hints

    def optimize_pagination(self, table, order_column, page_size=100):
        """Keyset pagination for better performance"""
        return f"""
        SELECT *
        FROM {table}
        WHERE {order_column} > :last_seen_value
        ORDER BY {order_column}
        LIMIT {page_size}
        """

    def batch_insert_optimization(self, table, records):
        """Optimized batch insertion using COPY"""
        import io
        import csv

        # Create in-memory CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=records[0].keys())
        writer.writerows(records)
        output.seek(0)

        # Use COPY for efficient bulk insert
        with self.engine.raw_connection() as conn:
            cursor = conn.cursor()
            columns = ', '.join(records[0].keys())
            cursor.copy_expert(
                f"COPY {table} ({columns}) FROM STDIN WITH CSV HEADER",
                output
            )
            conn.commit()
```

## Advanced Query Patterns

### Temporal Queries
```python
class TemporalQueries:
    """Time-based query patterns"""

    def point_in_time_query(self, table, timestamp, valid_from='valid_from', valid_to='valid_to'):
        """Query state at specific point in time"""
        return f"""
        SELECT *
        FROM {table}
        WHERE {valid_from} <= :timestamp
          AND ({valid_to} IS NULL OR {valid_to} > :timestamp)
        """

    def temporal_join(self, left_table, right_table, join_key, timestamp):
        """Join tables with temporal validity"""
        return f"""
        SELECT l.*, r.*
        FROM {left_table} l
        INNER JOIN {right_table} r
          ON l.{join_key} = r.{join_key}
          AND l.valid_from <= :timestamp
          AND (l.valid_to IS NULL OR l.valid_to > :timestamp)
          AND r.valid_from <= :timestamp
          AND (r.valid_to IS NULL OR r.valid_to > :timestamp)
        """
```

### Pivot Operations
```python
class PivotOperations:
    """Pivot/Unpivot as functors between wide and long formats"""

    def pivot_query(self, table, row_key, column_key, value_column, columns):
        """Transform long format to wide format"""
        pivot_columns = []
        for col in columns:
            pivot_columns.append(
                f"MAX(CASE WHEN {column_key} = '{col}' THEN {value_column} END) AS {col}"
            )

        return f"""
        SELECT {row_key},
               {', '.join(pivot_columns)}
        FROM {table}
        GROUP BY {row_key}
        """

    def unpivot_query(self, table, row_key, value_columns):
        """Transform wide format to long format"""
        unpivot_parts = []
        for col in value_columns:
            unpivot_parts.append(f"SELECT {row_key}, '{col}' as attribute, {col} as value FROM {table}")

        return ' UNION ALL '.join(unpivot_parts)
```

## Performance Monitoring

```python
class QueryPerformanceMonitor:
    """Monitor and track query performance"""

    def __init__(self, engine):
        self.engine = engine
        self.query_log = []

    def log_query(self, query, duration, rows_affected):
        """Log query execution details"""
        self.query_log.append({
            'query': query,
            'duration': duration,
            'rows': rows_affected,
            'timestamp': datetime.now()
        })

    def get_slow_queries(self, threshold_ms=1000):
        """Identify slow queries"""
        return [q for q in self.query_log if q['duration'] > threshold_ms]

    def get_query_statistics(self):
        """Aggregate query statistics"""
        if not self.query_log:
            return {}

        durations = [q['duration'] for q in self.query_log]
        return {
            'total_queries': len(self.query_log),
            'avg_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'p95_duration': sorted(durations)[int(len(durations) * 0.95)]
        }
```

## Testing Framework

```python
import unittest
from unittest.mock import Mock, patch

class SQLQueryTests(unittest.TestCase):
    """Test suite for SQL query patterns"""

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.query_builder = SQLQueryBuilder(self.engine)

    def test_select_composition(self):
        """Test query composition"""
        result = self.query_builder.select(
            'users',
            columns='id, username',
            where="active = true",
            limit=10
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)

    def test_join_associativity(self):
        """Test that joins are associative"""
        # (A ⊗ B) ⊗ C should equal A ⊗ (B ⊗ C)
        join_ops = JoinOperations(self.engine)

        # Create test tables
        self.create_test_tables()

        # Test left association
        left_first = self.compose_joins(['A', 'B', 'C'], 'left')

        # Test right association
        right_first = self.compose_joins(['A', 'B', 'C'], 'right')

        # Results should be equivalent
        self.assertEqual(set(left_first.columns), set(right_first.columns))

    def create_test_tables(self):
        """Create test tables for join testing"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE A (id INT PRIMARY KEY, value TEXT)
            """))
            conn.execute(text("""
                CREATE TABLE B (id INT PRIMARY KEY, a_id INT, value TEXT)
            """))
            conn.execute(text("""
                CREATE TABLE C (id INT PRIMARY KEY, b_id INT, value TEXT)
            """))
            conn.commit()
```

## Integration with Luxor Marketplace

### Skill: postgresql-database-engineering
```python
class PostgreSQLIntegration:
    """Integration with PostgreSQL-specific features"""

    def __init__(self, pg_engine):
        self.engine = pg_engine

    def use_json_operators(self, table, json_column, json_path):
        """PostgreSQL JSON operators"""
        return f"""
        SELECT {json_column}->'{json_path}' as extracted
        FROM {table}
        WHERE {json_column} ? '{json_path}'
        """

    def array_operations(self, table, array_column):
        """PostgreSQL array operations"""
        return f"""
        SELECT unnest({array_column}) as element,
               array_length({array_column}, 1) as length,
               {array_column} && ARRAY[1,2,3] as overlaps
        FROM {table}
        """

    def use_upsert(self, table, columns, values, conflict_column):
        """PostgreSQL UPSERT operation"""
        cols = ', '.join(columns)
        vals = ', '.join([f':{v}' for v in values])
        updates = ', '.join([f"{c} = EXCLUDED.{c}" for c in columns])

        return f"""
        INSERT INTO {table} ({cols})
        VALUES ({vals})
        ON CONFLICT ({conflict_column})
        DO UPDATE SET {updates}
        RETURNING *
        """
```

## Conclusion

This first Kan extension establishes the fundamental SQL patterns as categorical structures, providing:

1. **Compositional Query Building**: Queries as morphisms that compose naturally
2. **Join Algebra**: Joins as tensor products in the monoidal category of relations
3. **Aggregation Functors**: Transformations from detailed to summary data
4. **CTE Composition**: Complex queries through morphism composition
5. **Performance Optimization**: Natural transformations for query optimization

The framework provides both theoretical foundation and practical implementation, enabling developers to think categorically while writing efficient SQL queries.