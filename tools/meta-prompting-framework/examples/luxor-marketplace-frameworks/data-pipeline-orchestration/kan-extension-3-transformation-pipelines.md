# Kan Extension 3: Data Transformation Pipelines

## Overview

This Kan extension focuses on advanced data transformation patterns using dbt, SQL optimization, and data quality frameworks. It introduces categorical approaches to schema evolution, incremental processing, and semantic layer design.

## Theoretical Foundation

### Functors for Schema Transformations

Schema transformations can be modeled as functors between schema categories:
```
F: SchemaA → SchemaB
```
Where F preserves the structure while mapping data types and relationships.

### Natural Transformations for Model Versioning

Model versions form a category where natural transformations represent migrations:
```
η: F ⟹ G
```
Where F and G are different versions of a transformation pipeline.

## dbt Advanced Patterns

### 1. Categorical Model Architecture

```sql
-- models/staging/categorical/base_morphisms.sql
{{ config(
    materialized='view',
    tags=['categorical', 'base']
) }}

-- Base morphism: Raw → Staging
WITH source_data AS (
    SELECT * FROM {{ source('raw', 'events') }}
),

typed_morphism AS (
    -- Type functor application
    SELECT
        CAST(id AS BIGINT) as event_id,
        CAST(timestamp AS TIMESTAMP) as event_timestamp,
        CAST(user_id AS BIGINT) as user_id,
        CAST(event_type AS VARCHAR(100)) as event_type,
        TRY_PARSE_JSON(event_data) as event_data,
        CAST(session_id AS VARCHAR(255)) as session_id,
        -- Metadata preservation (identity functor)
        _airbyte_raw_id,
        _airbyte_extracted_at,
        _airbyte_loaded_at
    FROM source_data
),

validated_morphism AS (
    -- Validation functor (partial function)
    SELECT *
    FROM typed_morphism
    WHERE event_id IS NOT NULL
      AND event_timestamp IS NOT NULL
      AND event_timestamp >= '2020-01-01'::TIMESTAMP
      AND event_timestamp <= CURRENT_TIMESTAMP()
)

SELECT * FROM validated_morphism
```

```sql
-- models/intermediate/categorical/composed_transformations.sql
{{ config(
    materialized='table',
    unique_key='event_id',
    on_schema_change='sync_all_columns',
    tags=['categorical', 'intermediate']
) }}

-- Composition of morphisms: Staging → Intermediate
WITH staged_events AS (
    SELECT * FROM {{ ref('base_morphisms') }}
),

-- Natural transformation: Event → EnrichedEvent
enriched_events AS (
    SELECT
        se.*,
        -- User dimension join (pullback in category theory)
        u.user_name,
        u.user_segment,
        u.user_lifetime_value,
        -- Session enrichment (pushout)
        s.session_duration_seconds,
        s.session_page_views,
        s.session_conversion_flag
    FROM staged_events se
    LEFT JOIN {{ ref('dim_users') }} u
        ON se.user_id = u.user_id
    LEFT JOIN {{ ref('session_metrics') }} s
        ON se.session_id = s.session_id
),

-- Monoidal product: Parallel aggregations
aggregated_metrics AS (
    SELECT
        event_id,
        event_timestamp,
        user_id,
        event_type,
        event_data,
        session_id,
        user_name,
        user_segment,
        user_lifetime_value,
        session_duration_seconds,
        session_page_views,
        session_conversion_flag,
        -- Window functions as endofunctors
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY event_timestamp
        ) as user_event_sequence,
        LAG(event_timestamp) OVER (
            PARTITION BY user_id
            ORDER BY event_timestamp
        ) as previous_event_timestamp,
        LEAD(event_type) OVER (
            PARTITION BY user_id
            ORDER BY event_timestamp
        ) as next_event_type
    FROM enriched_events
)

SELECT
    *,
    -- Derived metrics (functor composition)
    EXTRACT(EPOCH FROM (event_timestamp - previous_event_timestamp)) as seconds_since_last_event,
    CASE
        WHEN next_event_type = 'purchase' THEN 1
        ELSE 0
    END as leads_to_purchase
FROM aggregated_metrics
```

### 2. Incremental Processing Patterns

```sql
-- models/marts/incremental_categorical.sql
{{ config(
    materialized='incremental',
    unique_key='surrogate_key',
    on_schema_change='sync_all_columns',
    incremental_strategy='merge',
    merge_exclude_columns=['inserted_at'],
    tags=['categorical', 'marts', 'incremental']
) }}

-- Incremental processing as categorical limit/colimit
WITH source_data AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['order_id', 'product_id']) }} as surrogate_key,
        order_id,
        product_id,
        customer_id,
        order_date,
        quantity,
        unit_price,
        discount_percentage,
        tax_amount,
        shipping_cost,
        order_status,
        product_category,
        _extracted_at
    FROM {{ ref('stg_orders') }}

    {% if is_incremental() %}
        -- Incremental predicate (categorical filter)
        WHERE _extracted_at > (
            SELECT COALESCE(MAX(_extracted_at), '1900-01-01'::TIMESTAMP)
            FROM {{ this }}
        )
    {% endif %}
),

-- Type-safe transformations
transformed_data AS (
    SELECT
        surrogate_key,
        order_id,
        product_id,
        customer_id,
        order_date,
        quantity,
        unit_price,
        discount_percentage,
        tax_amount,
        shipping_cost,
        order_status,
        product_category,
        -- Categorical aggregations
        quantity * unit_price * (1 - discount_percentage) as gross_amount,
        quantity * unit_price * (1 - discount_percentage) + tax_amount + shipping_cost as total_amount,
        CASE
            WHEN order_status IN ('completed', 'shipped') THEN 'fulfilled'
            WHEN order_status IN ('pending', 'processing') THEN 'in_progress'
            WHEN order_status IN ('cancelled', 'refunded') THEN 'cancelled'
            ELSE 'unknown'
        END as order_status_category,
        -- Temporal categories
        DATE_TRUNC('month', order_date) as order_month,
        DATE_TRUNC('quarter', order_date) as order_quarter,
        EXTRACT(DOW FROM order_date) as day_of_week,
        CASE
            WHEN EXTRACT(DOW FROM order_date) IN (0, 6) THEN 'weekend'
            ELSE 'weekday'
        END as day_type,
        _extracted_at,
        CURRENT_TIMESTAMP() as inserted_at,
        CURRENT_TIMESTAMP() as updated_at
    FROM source_data
),

-- Data quality assertions (categorical invariants)
quality_checked AS (
    SELECT *
    FROM transformed_data
    WHERE gross_amount >= 0
      AND total_amount >= gross_amount
      AND quantity > 0
      AND unit_price > 0
      AND order_date <= CURRENT_DATE()
)

SELECT * FROM quality_checked
```

### 3. dbt Macros as Higher-Order Functions

```sql
-- macros/categorical_transformations.sql

{% macro generate_categorical_scd2(source_table, business_key, tracked_columns) %}
-- Slowly Changing Dimension Type 2 as categorical functor
WITH source AS (
    SELECT
        {{ business_key }} as natural_key,
        {{ tracked_columns | join(', ') }},
        {{ dbt_utils.generate_surrogate_key([business_key] + tracked_columns) }} as row_hash,
        _extracted_at as extracted_at
    FROM {{ source_table }}
),

current_records AS (
    SELECT *
    FROM {{ this }}
    WHERE is_current = TRUE
),

-- Detect changes (natural transformation)
changes AS (
    SELECT
        s.natural_key,
        s.row_hash as new_hash,
        c.row_hash as current_hash,
        CASE
            WHEN c.natural_key IS NULL THEN 'INSERT'
            WHEN s.row_hash != c.row_hash THEN 'UPDATE'
            ELSE 'NO_CHANGE'
        END as change_type
    FROM source s
    LEFT JOIN current_records c
        ON s.natural_key = c.natural_key
),

-- Apply SCD2 logic (endofunctor)
updates AS (
    SELECT
        natural_key,
        {% for col in tracked_columns %}
        {{ col }},
        {% endfor %}
        row_hash,
        extracted_at as valid_from,
        '9999-12-31'::TIMESTAMP as valid_to,
        TRUE as is_current,
        'UPDATE' as dml_action
    FROM source
    WHERE natural_key IN (
        SELECT natural_key FROM changes WHERE change_type = 'UPDATE'
    )

    UNION ALL

    -- Close out current records
    SELECT
        natural_key,
        {% for col in tracked_columns %}
        {{ col }},
        {% endfor %}
        row_hash,
        valid_from,
        extracted_at as valid_to,
        FALSE as is_current,
        'CLOSE' as dml_action
    FROM current_records
    WHERE natural_key IN (
        SELECT natural_key FROM changes WHERE change_type = 'UPDATE'
    )

    UNION ALL

    -- Insert new records
    SELECT
        natural_key,
        {% for col in tracked_columns %}
        {{ col }},
        {% endfor %}
        row_hash,
        extracted_at as valid_from,
        '9999-12-31'::TIMESTAMP as valid_to,
        TRUE as is_current,
        'INSERT' as dml_action
    FROM source
    WHERE natural_key IN (
        SELECT natural_key FROM changes WHERE change_type = 'INSERT'
    )
)

SELECT * FROM updates
{% endmacro %}

{% macro apply_categorical_aggregation(table_name, group_by_columns, aggregations) %}
-- Categorical aggregation as monoid operation
WITH base_data AS (
    SELECT * FROM {{ table_name }}
),

aggregated AS (
    SELECT
        {{ group_by_columns | join(', ') }},
        {% for agg_name, agg_expr in aggregations.items() %}
        {{ agg_expr }} as {{ agg_name }}{{ ',' if not loop.last }}
        {% endfor %}
    FROM base_data
    GROUP BY {{ group_by_columns | join(', ') }}
),

-- Add categorical metadata
with_metadata AS (
    SELECT
        *,
        -- Aggregation level indicator (functor tag)
        '{{ group_by_columns | join("_") }}' as aggregation_level,
        -- Aggregation timestamp
        CURRENT_TIMESTAMP() as aggregated_at,
        -- Row count for validation
        COUNT(*) OVER () as total_groups
    FROM aggregated
)

SELECT * FROM with_metadata
{% endmacro %}

{% macro generate_data_quality_tests(model_name, column_specs) %}
-- Generate data quality tests as categorical predicates
{% for column, specs in column_specs.items() %}

    {% if specs.get('not_null') %}
    -- Null check (identity functor preservation)
    SELECT '{{ model_name }}.{{ column }}' as test_name,
           'not_null' as test_type,
           COUNT(*) as failures
    FROM {{ ref(model_name) }}
    WHERE {{ column }} IS NULL
    HAVING COUNT(*) > 0

    UNION ALL
    {% endif %}

    {% if specs.get('unique') %}
    -- Uniqueness check (injection morphism)
    SELECT '{{ model_name }}.{{ column }}' as test_name,
           'unique' as test_type,
           COUNT(*) as failures
    FROM (
        SELECT {{ column }}, COUNT(*) as cnt
        FROM {{ ref(model_name) }}
        GROUP BY {{ column }}
        HAVING COUNT(*) > 1
    ) t

    UNION ALL
    {% endif %}

    {% if specs.get('accepted_values') %}
    -- Accepted values check (categorical membership)
    SELECT '{{ model_name }}.{{ column }}' as test_name,
           'accepted_values' as test_type,
           COUNT(*) as failures
    FROM {{ ref(model_name) }}
    WHERE {{ column }} NOT IN ({{ specs.get('accepted_values') | join(', ') }})

    UNION ALL
    {% endif %}

    {% if specs.get('relationships') %}
    -- Referential integrity (morphism existence)
    SELECT '{{ model_name }}.{{ column }}' as test_name,
           'relationships' as test_type,
           COUNT(*) as failures
    FROM {{ ref(model_name) }} t1
    LEFT JOIN {{ ref(specs.get('relationships').get('to')) }} t2
        ON t1.{{ column }} = t2.{{ specs.get('relationships').get('field') }}
    WHERE t2.{{ specs.get('relationships').get('field') }} IS NULL
      AND t1.{{ column }} IS NOT NULL
    {% endif %}

{% endfor %}
{% endmacro %}
```

### 4. Semantic Layer Implementation

```python
# models/semantic_layer/semantic_model.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AggregationType(Enum):
    """Categorical aggregation types"""
    SUM = "sum"
    AVG = "average"
    COUNT = "count"
    COUNT_DISTINCT = "count_distinct"
    MAX = "max"
    MIN = "min"
    MEDIAN = "median"

@dataclass
class Dimension:
    """Dimensional object in semantic category"""
    name: str
    sql_expression: str
    data_type: str
    description: str
    is_primary_key: bool = False
    is_time_dimension: bool = False

@dataclass
class Measure:
    """Measure as functor from dimensions to values"""
    name: str
    sql_expression: str
    aggregation: AggregationType
    description: str
    format_string: Optional[str] = None

@dataclass
class SemanticModel:
    """Semantic model as categorical structure"""
    name: str
    base_table: str
    dimensions: List[Dimension]
    measures: List[Measure]
    filters: Optional[Dict[str, str]] = None

class SemanticLayerBuilder:
    """Build semantic layer with categorical patterns"""

    def __init__(self):
        self.models: Dict[str, SemanticModel] = {}

    def register_model(self, model: SemanticModel):
        """Register semantic model in category"""
        self.models[model.name] = model

    def generate_sql(self, model_name: str,
                    dimensions: List[str],
                    measures: List[str],
                    filters: Optional[Dict[str, Any]] = None) -> str:
        """Generate SQL as categorical morphism"""

        model = self.models.get(model_name)
        if not model:
            raise ValueError(f"Model {model_name} not found")

        # Build dimension expressions
        dim_sql = []
        for dim_name in dimensions:
            dim = next((d for d in model.dimensions if d.name == dim_name), None)
            if dim:
                dim_sql.append(f"{dim.sql_expression} AS {dim.name}")

        # Build measure expressions
        measure_sql = []
        for measure_name in measures:
            measure = next((m for m in model.measures if m.name == measure_name), None)
            if measure:
                agg_func = self._get_agg_function(measure.aggregation)
                measure_sql.append(f"{agg_func}({measure.sql_expression}) AS {measure.name}")

        # Build WHERE clause
        where_clauses = []
        if model.filters:
            where_clauses.extend([f"{k} {v}" for k, v in model.filters.items()])
        if filters:
            where_clauses.extend([f"{k} = {v}" for k, v in filters.items()])

        # Construct query
        select_clause = ", ".join(dim_sql + measure_sql)
        from_clause = model.base_table
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        group_by_clause = ", ".join(dim_sql) if dim_sql else ""

        sql = f"""
        SELECT {select_clause}
        FROM {from_clause}
        WHERE {where_clause}
        """

        if group_by_clause and measure_sql:
            sql += f" GROUP BY {group_by_clause}"

        return sql

    def _get_agg_function(self, agg_type: AggregationType) -> str:
        """Map aggregation type to SQL function"""
        mapping = {
            AggregationType.SUM: "SUM",
            AggregationType.AVG: "AVG",
            AggregationType.COUNT: "COUNT",
            AggregationType.COUNT_DISTINCT: "COUNT(DISTINCT",
            AggregationType.MAX: "MAX",
            AggregationType.MIN: "MIN",
            AggregationType.MEDIAN: "MEDIAN"
        }
        return mapping.get(agg_type, "SUM")

# Example semantic model definition
sales_model = SemanticModel(
    name="sales_metrics",
    base_table="fact_sales",
    dimensions=[
        Dimension("date", "order_date", "date", "Order date", is_time_dimension=True),
        Dimension("customer_id", "customer_id", "integer", "Customer identifier", is_primary_key=True),
        Dimension("product_category", "product_category", "string", "Product category"),
        Dimension("region", "shipping_region", "string", "Shipping region")
    ],
    measures=[
        Measure("revenue", "unit_price * quantity", AggregationType.SUM, "Total revenue", "$#,##0.00"),
        Measure("units_sold", "quantity", AggregationType.SUM, "Units sold"),
        Measure("order_count", "order_id", AggregationType.COUNT_DISTINCT, "Number of orders"),
        Measure("avg_order_value", "total_amount", AggregationType.AVG, "Average order value", "$#,##0.00")
    ],
    filters={"order_status": "= 'completed'"}
)
```

## SQL Optimization Patterns

### 1. Query Optimizer as Categorical Transformation

```python
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison
from typing import List, Tuple, Optional

class CategoricalQueryOptimizer:
    """SQL query optimizer using categorical transformations"""

    def __init__(self):
        self.transformation_rules = []
        self.register_default_rules()

    def register_default_rules(self):
        """Register categorical transformation rules"""

        # Rule 1: Push down predicates (functor preservation)
        self.transformation_rules.append(self.push_down_predicates)

        # Rule 2: Eliminate redundant joins (identity removal)
        self.transformation_rules.append(self.eliminate_redundant_joins)

        # Rule 3: Merge adjacent filters (monoid operation)
        self.transformation_rules.append(self.merge_filters)

        # Rule 4: Common subexpression elimination (memoization)
        self.transformation_rules.append(self.eliminate_common_subexpressions)

    def optimize(self, sql: str) -> str:
        """Apply categorical optimizations to SQL query"""

        parsed = sqlparse.parse(sql)[0]

        for rule in self.transformation_rules:
            parsed = rule(parsed)

        return str(parsed)

    def push_down_predicates(self, query):
        """Push predicates closer to data source"""
        # Simplified implementation
        # In practice, would use proper SQL AST manipulation
        return query

    def eliminate_redundant_joins(self, query):
        """Remove unnecessary joins"""
        # Detect and remove joins that don't contribute to result
        return query

    def merge_filters(self, query):
        """Combine multiple WHERE clauses"""
        # Merge adjacent filter conditions
        return query

    def eliminate_common_subexpressions(self, query):
        """Factor out common subexpressions"""
        # Identify and extract CTEs
        return query

class QueryPlanAnalyzer:
    """Analyze query execution plans categorically"""

    def __init__(self):
        self.cost_model = {
            'seq_scan': 1.0,
            'index_scan': 0.1,
            'hash_join': 0.5,
            'nested_loop': 2.0,
            'merge_join': 0.3
        }

    def estimate_cost(self, plan: Dict[str, Any]) -> float:
        """Estimate query cost as categorical morphism"""

        total_cost = 0.0

        if 'operation' in plan:
            op_cost = self.cost_model.get(plan['operation'], 1.0)
            row_factor = plan.get('estimated_rows', 1) / 1000
            total_cost += op_cost * row_factor

        if 'children' in plan:
            for child in plan['children']:
                total_cost += self.estimate_cost(child)

        return total_cost

    def suggest_optimizations(self, plan: Dict[str, Any]) -> List[str]:
        """Suggest optimizations based on plan analysis"""

        suggestions = []

        # Check for sequential scans on large tables
        if plan.get('operation') == 'seq_scan' and plan.get('estimated_rows', 0) > 10000:
            suggestions.append(f"Consider adding index on {plan.get('table')}")

        # Check for nested loop joins on large datasets
        if plan.get('operation') == 'nested_loop' and plan.get('estimated_rows', 0) > 1000:
            suggestions.append("Consider using hash join or merge join for better performance")

        return suggestions
```

### 2. Materialized View Management

```sql
-- models/materialized_views/categorical_mv_manager.sql

{% macro create_categorical_materialized_view(view_name, base_query, refresh_strategy='incremental') %}
-- Materialized view as categorical cache functor

CREATE MATERIALIZED VIEW IF NOT EXISTS {{ view_name }} AS
WITH base_data AS (
    {{ base_query }}
),

-- Add categorical metadata
metadata_enriched AS (
    SELECT
        *,
        -- Versioning metadata
        {{ dbt_utils.generate_surrogate_key(['*']) }} as row_hash,
        CURRENT_TIMESTAMP() as materialized_at,
        '{{ refresh_strategy }}' as refresh_strategy
    FROM base_data
)

SELECT * FROM metadata_enriched;

-- Create indexes for categorical access patterns
CREATE INDEX IF NOT EXISTS idx_{{ view_name }}_materialized_at
    ON {{ view_name }} (materialized_at);

CREATE INDEX IF NOT EXISTS idx_{{ view_name }}_row_hash
    ON {{ view_name }} (row_hash);

{% endmacro %}

{% macro refresh_materialized_view(view_name, strategy='incremental') %}
-- Refresh strategy as endofunctor

{% if strategy == 'incremental' %}
    -- Incremental refresh (partial functor application)
    INSERT INTO {{ view_name }}
    SELECT * FROM (
        {{ caller() }}
    ) new_data
    WHERE NOT EXISTS (
        SELECT 1 FROM {{ view_name }} existing
        WHERE existing.row_hash = new_data.row_hash
    );

{% elif strategy == 'complete' %}
    -- Complete refresh (functor recomputation)
    TRUNCATE TABLE {{ view_name }};
    INSERT INTO {{ view_name }}
    {{ caller() }};

{% elif strategy == 'merge' %}
    -- Merge refresh (natural transformation)
    MERGE INTO {{ view_name }} target
    USING ({{ caller() }}) source
    ON target.row_hash = source.row_hash
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *;

{% endif %}

-- Update statistics (categorical metadata)
ANALYZE TABLE {{ view_name }} COMPUTE STATISTICS;

{% endmacro %}
```

## Data Quality Framework

### 1. Categorical Data Quality Rules

```python
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import pandas as pd

class QualityDimension(Enum):
    """Data quality dimensions as categorical objects"""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    UNIQUENESS = "uniqueness"
    VALIDITY = "validity"

@dataclass
class QualityRule:
    """Quality rule as categorical predicate"""
    name: str
    dimension: QualityDimension
    predicate: Callable[[pd.DataFrame], bool]
    severity: str  # 'error', 'warning', 'info'
    description: str

class CategoricalDataQuality:
    """Data quality framework using category theory"""

    def __init__(self):
        self.rules: List[QualityRule] = []
        self.results: List[Dict[str, Any]] = []

    def add_rule(self, rule: QualityRule):
        """Add quality rule to category"""
        self.rules.append(rule)

    def add_completeness_rule(self, column: str, threshold: float = 0.95):
        """Completeness as preservation of structure"""
        def check_completeness(df: pd.DataFrame) -> bool:
            if column not in df.columns:
                return False
            completeness = df[column].notna().mean()
            return completeness >= threshold

        self.add_rule(QualityRule(
            name=f"completeness_{column}",
            dimension=QualityDimension.COMPLETENESS,
            predicate=check_completeness,
            severity="error" if threshold > 0.9 else "warning",
            description=f"Column {column} must be at least {threshold*100}% complete"
        ))

    def add_uniqueness_rule(self, columns: List[str]):
        """Uniqueness as injection morphism"""
        def check_uniqueness(df: pd.DataFrame) -> bool:
            duplicates = df.duplicated(subset=columns, keep=False)
            return not duplicates.any()

        self.add_rule(QualityRule(
            name=f"uniqueness_{','.join(columns)}",
            dimension=QualityDimension.UNIQUENESS,
            predicate=check_uniqueness,
            severity="error",
            description=f"Columns {columns} must be unique"
        ))

    def add_consistency_rule(self, rule_expr: str):
        """Consistency as categorical equation"""
        def check_consistency(df: pd.DataFrame) -> bool:
            try:
                result = df.eval(rule_expr)
                return result.all()
            except:
                return False

        self.add_rule(QualityRule(
            name=f"consistency_{hash(rule_expr)}",
            dimension=QualityDimension.CONSISTENCY,
            predicate=check_consistency,
            severity="error",
            description=f"Data must satisfy: {rule_expr}"
        ))

    def add_referential_integrity_rule(self, source_col: str, ref_df: pd.DataFrame, ref_col: str):
        """Referential integrity as morphism existence"""
        def check_referential_integrity(df: pd.DataFrame) -> bool:
            source_values = set(df[source_col].dropna())
            ref_values = set(ref_df[ref_col])
            return source_values.issubset(ref_values)

        self.add_rule(QualityRule(
            name=f"referential_integrity_{source_col}",
            dimension=QualityDimension.VALIDITY,
            predicate=check_referential_integrity,
            severity="error",
            description=f"All {source_col} values must exist in reference"
        ))

    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data against all rules"""

        results = {
            'passed': [],
            'failed': [],
            'warnings': [],
            'summary': {}
        }

        for rule in self.rules:
            try:
                passed = rule.predicate(df)

                result = {
                    'rule': rule.name,
                    'dimension': rule.dimension.value,
                    'passed': passed,
                    'severity': rule.severity,
                    'description': rule.description
                }

                if passed:
                    results['passed'].append(result)
                else:
                    if rule.severity == 'error':
                        results['failed'].append(result)
                    else:
                        results['warnings'].append(result)

            except Exception as e:
                results['failed'].append({
                    'rule': rule.name,
                    'error': str(e),
                    'severity': 'error'
                })

        # Calculate summary statistics
        total_rules = len(self.rules)
        passed_count = len(results['passed'])
        failed_count = len(results['failed'])
        warning_count = len(results['warnings'])

        results['summary'] = {
            'total_rules': total_rules,
            'passed': passed_count,
            'failed': failed_count,
            'warnings': warning_count,
            'pass_rate': passed_count / total_rules if total_rules > 0 else 0,
            'quality_score': self.calculate_quality_score(results)
        }

        return results

    def calculate_quality_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall quality score as categorical measure"""

        # Weight by severity
        weights = {'error': 1.0, 'warning': 0.5, 'info': 0.1}

        total_weight = 0
        score = 0

        for passed_rule in results['passed']:
            weight = weights.get(passed_rule['severity'], 0.1)
            total_weight += weight
            score += weight

        for failed_rule in results['failed']:
            weight = weights.get(failed_rule['severity'], 1.0)
            total_weight += weight
            # Failed rules contribute 0 to score

        if total_weight == 0:
            return 1.0

        return score / total_weight
```

### 2. Data Profiling

```python
import numpy as np
from scipy import stats
from typing import Optional

class CategoricalDataProfiler:
    """Data profiler using categorical analysis"""

    def __init__(self):
        self.profile = {}

    def profile_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive data profile"""

        profile = {
            'metadata': self.extract_metadata(df),
            'columns': {}
        }

        for column in df.columns:
            profile['columns'][column] = self.profile_column(df[column])

        profile['relationships'] = self.detect_relationships(df)
        profile['anomalies'] = self.detect_anomalies(df)

        return profile

    def extract_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract categorical metadata"""

        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024 / 1024,  # MB
            'duplicates': df.duplicated().sum(),
            'missing_cells': df.isna().sum().sum(),
            'completeness': 1 - (df.isna().sum().sum() / (len(df) * len(df.columns)))
        }

    def profile_column(self, series: pd.Series) -> Dict[str, Any]:
        """Profile individual column as categorical object"""

        profile = {
            'name': series.name,
            'dtype': str(series.dtype),
            'missing': series.isna().sum(),
            'missing_pct': series.isna().mean(),
            'unique': series.nunique(),
            'unique_pct': series.nunique() / len(series) if len(series) > 0 else 0
        }

        # Numeric profiling
        if pd.api.types.is_numeric_dtype(series):
            profile.update(self.profile_numeric(series))

        # Categorical profiling
        elif pd.api.types.is_string_dtype(series) or pd.api.types.is_categorical_dtype(series):
            profile.update(self.profile_categorical(series))

        # Temporal profiling
        elif pd.api.types.is_datetime64_any_dtype(series):
            profile.update(self.profile_temporal(series))

        return profile

    def profile_numeric(self, series: pd.Series) -> Dict[str, Any]:
        """Profile numeric column as measurement functor"""

        clean_series = series.dropna()

        if len(clean_series) == 0:
            return {}

        return {
            'mean': clean_series.mean(),
            'median': clean_series.median(),
            'std': clean_series.std(),
            'min': clean_series.min(),
            'max': clean_series.max(),
            'q25': clean_series.quantile(0.25),
            'q75': clean_series.quantile(0.75),
            'iqr': clean_series.quantile(0.75) - clean_series.quantile(0.25),
            'skewness': stats.skew(clean_series),
            'kurtosis': stats.kurtosis(clean_series),
            'zeros': (clean_series == 0).sum(),
            'negative': (clean_series < 0).sum(),
            'outliers': self.detect_outliers_iqr(clean_series)
        }

    def profile_categorical(self, series: pd.Series) -> Dict[str, Any]:
        """Profile categorical column as discrete category"""

        value_counts = series.value_counts()

        return {
            'cardinality': len(value_counts),
            'mode': value_counts.index[0] if len(value_counts) > 0 else None,
            'mode_freq': value_counts.iloc[0] if len(value_counts) > 0 else 0,
            'top_values': value_counts.head(10).to_dict(),
            'entropy': stats.entropy(value_counts),
            'is_boolean': len(value_counts) == 2,
            'has_whitespace': series.astype(str).str.contains(r'\s').any()
        }

    def profile_temporal(self, series: pd.Series) -> Dict[str, Any]:
        """Profile temporal column as time category"""

        clean_series = series.dropna()

        if len(clean_series) == 0:
            return {}

        return {
            'min_date': clean_series.min(),
            'max_date': clean_series.max(),
            'date_range': (clean_series.max() - clean_series.min()).days,
            'future_dates': (clean_series > pd.Timestamp.now()).sum(),
            'weekend_count': clean_series.dt.dayofweek.isin([5, 6]).sum(),
            'most_common_day': clean_series.dt.day_name().mode()[0] if len(clean_series) > 0 else None,
            'is_monotonic': clean_series.is_monotonic_increasing or clean_series.is_monotonic_decreasing
        }

    def detect_outliers_iqr(self, series: pd.Series, multiplier: float = 1.5) -> int:
        """Detect outliers using IQR method"""

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr

        return ((series < lower_bound) | (series > upper_bound)).sum()

    def detect_relationships(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect relationships between columns as morphisms"""

        relationships = {
            'correlations': {},
            'dependencies': {},
            'potential_keys': []
        }

        # Numeric correlations
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            high_corr = np.where(np.abs(corr_matrix) > 0.7)
            for i, j in zip(high_corr[0], high_corr[1]):
                if i < j:  # Upper triangle only
                    col1, col2 = numeric_cols[i], numeric_cols[j]
                    relationships['correlations'][f"{col1}_{col2}"] = corr_matrix.iloc[i, j]

        # Detect potential keys
        for col in df.columns:
            if df[col].nunique() == len(df):
                relationships['potential_keys'].append(col)

        return relationships

    def detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect data anomalies as categorical violations"""

        anomalies = []

        # Check for constant columns
        for col in df.columns:
            if df[col].nunique() == 1:
                anomalies.append({
                    'type': 'constant_column',
                    'column': col,
                    'severity': 'warning'
                })

        # Check for high cardinality in small dataset
        if len(df) < 1000:
            for col in df.columns:
                if df[col].nunique() > len(df) * 0.9:
                    anomalies.append({
                        'type': 'high_cardinality',
                        'column': col,
                        'severity': 'info'
                    })

        return anomalies
```

## Pipeline Orchestration Patterns

### 1. DAG Composition

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.sql import SQLOperator
from airflow.providers.dbt.operators.dbt_cloud import DbtCloudRunJobOperator
from datetime import datetime, timedelta

class CategoricalDAGBuilder:
    """Build Airflow DAGs using categorical composition"""

    def __init__(self, dag_id: str, schedule_interval: str):
        self.dag_id = dag_id
        self.schedule_interval = schedule_interval
        self.default_args = {
            'owner': 'data-team',
            'depends_on_past': False,
            'start_date': datetime(2024, 1, 1),
            'retries': 2,
            'retry_delay': timedelta(minutes=5),
            'email_on_failure': True,
            'email_on_retry': False
        }

    def build_dag(self) -> DAG:
        """Build DAG as categorical graph"""

        dag = DAG(
            self.dag_id,
            default_args=self.default_args,
            schedule_interval=self.schedule_interval,
            catchup=False,
            tags=['categorical', 'data-pipeline']
        )

        return dag

    def compose_sequential(self, dag: DAG, tasks: List[Dict[str, Any]]) -> None:
        """Sequential composition (categorical arrow)"""

        previous_task = None
        for task_config in tasks:
            task = self.create_task(dag, task_config)
            if previous_task:
                previous_task >> task
            previous_task = task

    def compose_parallel(self, dag: DAG, tasks: List[Dict[str, Any]]) -> List:
        """Parallel composition (monoidal product)"""

        return [self.create_task(dag, task_config) for task_config in tasks]

    def compose_conditional(self, dag: DAG, condition_task, true_tasks, false_tasks):
        """Conditional composition (coproduct)"""

        from airflow.operators.python import BranchPythonOperator

        branch = BranchPythonOperator(
            task_id='conditional_branch',
            python_callable=condition_task,
            dag=dag
        )

        true_branch = self.compose_sequential(dag, true_tasks)
        false_branch = self.compose_sequential(dag, false_tasks)

        branch >> [true_branch[0], false_branch[0]]

    def create_task(self, dag: DAG, task_config: Dict[str, Any]):
        """Create task as categorical morphism"""

        task_type = task_config.get('type')

        if task_type == 'python':
            return PythonOperator(
                task_id=task_config['id'],
                python_callable=task_config['callable'],
                op_kwargs=task_config.get('kwargs', {}),
                dag=dag
            )
        elif task_type == 'sql':
            return SQLOperator(
                task_id=task_config['id'],
                sql=task_config['sql'],
                conn_id=task_config.get('conn_id', 'default'),
                dag=dag
            )
        elif task_type == 'dbt':
            return DbtCloudRunJobOperator(
                task_id=task_config['id'],
                job_id=task_config['job_id'],
                account_id=task_config['account_id'],
                dag=dag
            )

# Example DAG using categorical composition
def build_etl_dag():
    """Build ETL DAG with categorical patterns"""

    builder = CategoricalDAGBuilder(
        dag_id='categorical_etl_pipeline',
        schedule_interval='@daily'
    )

    dag = builder.build_dag()

    # Stage 1: Extract (parallel composition)
    extract_tasks = builder.compose_parallel(dag, [
        {'id': 'extract_orders', 'type': 'python', 'callable': extract_orders},
        {'id': 'extract_customers', 'type': 'python', 'callable': extract_customers},
        {'id': 'extract_products', 'type': 'python', 'callable': extract_products}
    ])

    # Stage 2: Transform (sequential composition)
    transform_tasks = [
        {'id': 'validate_data', 'type': 'python', 'callable': validate_data},
        {'id': 'transform_data', 'type': 'python', 'callable': transform_data},
        {'id': 'enrich_data', 'type': 'python', 'callable': enrich_data}
    ]

    # Stage 3: Load (conditional composition)
    quality_check = {'id': 'quality_check', 'type': 'python', 'callable': check_quality}
    load_tasks = [{'id': 'load_to_warehouse', 'type': 'python', 'callable': load_data}]
    alert_tasks = [{'id': 'send_alert', 'type': 'python', 'callable': send_quality_alert}]

    # Compose pipeline
    for extract_task in extract_tasks:
        extract_task >> transform_tasks[0]

    builder.compose_sequential(dag, transform_tasks)
    builder.compose_conditional(dag, quality_check, load_tasks, alert_tasks)

    return dag
```

## Performance Testing

### 1. Load Testing Framework

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable

class PipelineLoadTester:
    """Load testing for data pipelines"""

    def __init__(self, pipeline_func: Callable):
        self.pipeline_func = pipeline_func
        self.metrics = []

    async def run_load_test(self,
                           data_generator: Callable,
                           num_requests: int,
                           concurrency: int) -> Dict[str, Any]:
        """Run load test with categorical metrics"""

        start_time = time.time()

        # Generate test data
        test_data = [data_generator() for _ in range(num_requests)]

        # Run pipeline with concurrency control
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            for data in test_data:
                future = executor.submit(self.run_single_test, data)
                futures.append(future)

            results = [f.result() for f in futures]

        end_time = time.time()

        # Calculate metrics
        return self.calculate_metrics(results, end_time - start_time)

    def run_single_test(self, data: Any) -> Dict[str, Any]:
        """Run single pipeline execution"""

        start = time.time()
        try:
            result = self.pipeline_func(data)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)

        return {
            'duration': time.time() - start,
            'success': success,
            'error': error,
            'timestamp': start
        }

    def calculate_metrics(self, results: List[Dict], total_time: float) -> Dict[str, Any]:
        """Calculate categorical performance metrics"""

        durations = [r['duration'] for r in results if r['success']]
        failures = [r for r in results if not r['success']]

        return {
            'total_requests': len(results),
            'successful_requests': len(durations),
            'failed_requests': len(failures),
            'success_rate': len(durations) / len(results) if results else 0,
            'total_time': total_time,
            'throughput': len(results) / total_time if total_time > 0 else 0,
            'latency': {
                'mean': np.mean(durations) if durations else 0,
                'median': np.median(durations) if durations else 0,
                'p95': np.percentile(durations, 95) if durations else 0,
                'p99': np.percentile(durations, 99) if durations else 0,
                'min': np.min(durations) if durations else 0,
                'max': np.max(durations) if durations else 0
            },
            'errors': [f['error'] for f in failures[:10]]  # First 10 errors
        }

    def generate_report(self, metrics: Dict[str, Any]) -> str:
        """Generate load test report"""

        report = f"""
        Load Test Report
        ================
        Total Requests: {metrics['total_requests']}
        Successful: {metrics['successful_requests']}
        Failed: {metrics['failed_requests']}
        Success Rate: {metrics['success_rate']*100:.2f}%

        Performance Metrics
        ------------------
        Total Time: {metrics['total_time']:.2f}s
        Throughput: {metrics['throughput']:.2f} req/s

        Latency Distribution
        -------------------
        Mean: {metrics['latency']['mean']*1000:.2f}ms
        Median: {metrics['latency']['median']*1000:.2f}ms
        P95: {metrics['latency']['p95']*1000:.2f}ms
        P99: {metrics['latency']['p99']*1000:.2f}ms
        Min: {metrics['latency']['min']*1000:.2f}ms
        Max: {metrics['latency']['max']*1000:.2f}ms
        """

        if metrics['errors']:
            report += "\nErrors:\n"
            for error in metrics['errors']:
                report += f"  - {error}\n"

        return report
```

## Conclusion

This Kan extension provides comprehensive patterns for data transformation pipelines, including advanced dbt modeling, SQL optimization, and data quality frameworks. The categorical approach ensures type safety, composability, and formal verification of transformation logic throughout the pipeline.