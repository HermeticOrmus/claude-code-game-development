package examples

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// Advanced constraint interfaces for type classes
type Numeric interface {
	~int | ~int8 | ~int16 | ~int32 | ~int64 |
		~uint | ~uint8 | ~uint16 | ~uint32 | ~uint64 |
		~float32 | ~float64
}

type Addable[T any] interface {
	Add(T) T
	Zero() T
}

type Multiplicable[T any] interface {
	Multiply(T) T
	One() T
}

// Monoid constraint
type Monoid[T any] interface {
	Empty() T
	Append(T) T
}

// Functor constraint
type Functor[F any, A any] interface {
	Map(func(A) A) F
}

// Applicative constraint
type Applicative[F any, A any] interface {
	Functor[F, A]
	Pure(A) F
	Apply(F) F
}

// Monad constraint
type Monad[F any, A any] interface {
	Applicative[F, A]
	FlatMap(func(A) F) F
}

// Vector with numeric operations
type Vector[T Numeric] []T

func (v Vector[T]) Add(other Vector[T]) Vector[T] {
	result := make(Vector[T], len(v))
	for i := range v {
		result[i] = v[i] + other[i]
	}
	return result
}

func (v Vector[T]) Scale(scalar T) Vector[T] {
	result := make(Vector[T], len(v))
	for i := range v {
		result[i] = v[i] * scalar
	}
	return result
}

func (v Vector[T]) Dot(other Vector[T]) T {
	var result T
	for i := range v {
		result += v[i] * other[i]
	}
	return result
}

// Matrix operations
type Matrix[T Numeric] [][]T

func (m Matrix[T]) Multiply(other Matrix[T]) Matrix[T] {
	rows := len(m)
	cols := len(other[0])
	result := make(Matrix[T], rows)

	for i := 0; i < rows; i++ {
		result[i] = make([]T, cols)
		for j := 0; j < cols; j++ {
			var sum T
			for k := 0; k < len(other); k++ {
				sum += m[i][k] * other[k][j]
			}
			result[i][j] = sum
		}
	}
	return result
}

// Transducer with type constraints
type Transducer[A, B any] func(Reducer[B, any]) Reducer[A, any]
type Reducer[T, R any] func(R, T) R

func MapT[A, B any](f func(A) B) Transducer[A, B] {
	return func(reducer Reducer[B, any]) Reducer[A, any] {
		return func(acc any, a A) any {
			return reducer(acc, f(a))
		}
	}
}

func FilterT[T any](pred func(T) bool) Transducer[T, T] {
	return func(reducer Reducer[T, any]) Reducer[T, any] {
		return func(acc any, t T) any {
			if pred(t) {
				return reducer(acc, t)
			}
			return acc
		}
	}
}

func TakeT[T any](n int) Transducer[T, T] {
	count := 0
	return func(reducer Reducer[T, any]) Reducer[T, any] {
		return func(acc any, t T) any {
			if count < n {
				count++
				return reducer(acc, t)
			}
			return acc
		}
	}
}

// Compose transducers
func ComposeT[A, B, C any](t1 Transducer[B, C], t2 Transducer[A, B]) Transducer[A, C] {
	return func(reducer Reducer[C, any]) Reducer[A, any] {
		return t2(t1(reducer))
	}
}

// Advanced Result type with context
type Result[T any] struct {
	value T
	err   error
	ctx   context.Context
}

func Ok[T any](ctx context.Context, value T) Result[T] {
	return Result[T]{value: value, ctx: ctx}
}

func Err[T any](ctx context.Context, err error) Result[T] {
	return Result[T]{err: err, ctx: ctx}
}

func (r Result[T]) Map(f func(T) T) Result[T] {
	if r.err != nil {
		return r
	}
	return Ok(r.ctx, f(r.value))
}

func (r Result[T]) FlatMap(f func(T) Result[T]) Result[T] {
	if r.err != nil {
		return r
	}
	return f(r.value)
}

func (r Result[T]) MapError(f func(error) error) Result[T] {
	if r.err != nil {
		return Err[T](r.ctx, f(r.err))
	}
	return r
}

func (r Result[T]) Recover(f func(error) T) Result[T] {
	if r.err != nil {
		return Ok(r.ctx, f(r.err))
	}
	return r
}

// Validation type for accumulating errors
type Validation[E any, T any] struct {
	value  *T
	errors []E
}

func Valid[E, T any](value T) Validation[E, T] {
	return Validation[E, T]{value: &value}
}

func Invalid[E, T any](errors ...E) Validation[E, T] {
	return Validation[E, T]{errors: errors}
}

func (v Validation[E, T]) Map(f func(T) T) Validation[E, T] {
	if v.value != nil {
		newVal := f(*v.value)
		return Valid[E](newVal)
	}
	return v
}

func (v Validation[E, T]) Apply(vf Validation[E, func(T) T]) Validation[E, T] {
	if v.value != nil && vf.value != nil {
		fn := *vf.value
		newVal := fn(*v.value)
		return Valid[E](newVal)
	}

	var allErrors []E
	allErrors = append(allErrors, v.errors...)
	allErrors = append(allErrors, vf.errors...)
	return Invalid[E, T](allErrors...)
}

// Parallel validation
func ValidateAll[E, T any](validators ...func(T) Validation[E, T]) func(T) Validation[E, T] {
	return func(value T) Validation[E, T] {
		var wg sync.WaitGroup
		results := make([]Validation[E, T], len(validators))

		for i, validator := range validators {
			wg.Add(1)
			go func(idx int, v func(T) Validation[E, T]) {
				defer wg.Done()
				results[idx] = v(value)
			}(i, validator)
		}

		wg.Wait()

		// Combine all validations
		var allErrors []E
		for _, result := range results {
			if result.value == nil {
				allErrors = append(allErrors, result.errors...)
			}
		}

		if len(allErrors) > 0 {
			return Invalid[E, T](allErrors...)
		}

		return Valid[E](value)
	}
}

// Type-safe builder with phantom types
type Builder[T any, State any] struct {
	value T
	state State
}

type Incomplete struct{}
type Complete struct{}

func NewBuilder[T any]() Builder[T, Incomplete] {
	var zero T
	return Builder[T, Incomplete]{value: zero}
}

func (b Builder[T, S]) WithField(setter func(T) T) Builder[T, S] {
	return Builder[T, S]{
		value: setter(b.value),
		state: b.state,
	}
}

func (b Builder[T, Incomplete]) Complete() Builder[T, Complete] {
	return Builder[T, Complete]{
		value: b.value,
	}
}

func (b Builder[T, Complete]) Build() T {
	return b.value
}

// Example usage
func ExampleAdvancedGenerics() {
	ctx := context.Background()

	// Vector operations
	v1 := Vector[float64]{1, 2, 3}
	v2 := Vector[float64]{4, 5, 6}
	v3 := v1.Add(v2).Scale(2)
	dot := v1.Dot(v2)
	fmt.Printf("Vector result: %v, dot product: %v\n", v3, dot)

	// Transducer composition
	transducer := ComposeT(
		MapT(func(x int) int { return x * 2 }),
		FilterT(func(x int) bool { return x > 5 }),
	)

	reducer := func(acc []int, x int) []int {
		return append(acc, x)
	}

	// Apply transducer
	input := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
	var result []int
	finalReducer := transducer(func(acc any, x int) any {
		return reducer(acc.([]int), x)
	})

	for _, item := range input {
		result = finalReducer(result, item).([]int)
	}
	fmt.Printf("Transduced result: %v\n", result)

	// Result chaining with context
	computation := Ok(ctx, 10).
		Map(func(x int) int { return x * 2 }).
		FlatMap(func(x int) Result[int] {
			if x > 15 {
				return Ok(ctx, x)
			}
			return Err[int](ctx, fmt.Errorf("value too small"))
		})

	if computation.err != nil {
		fmt.Printf("Error: %v\n", computation.err)
	} else {
		fmt.Printf("Success: %v\n", computation.value)
	}

	// Validation composition
	validateAge := func(age int) Validation[string, int] {
		if age < 0 {
			return Invalid[string, int]("Age cannot be negative")
		}
		if age > 150 {
			return Invalid[string, int]("Age cannot exceed 150")
		}
		return Valid[string](age)
	}

	validateName := func(name string) Validation[string, string] {
		if len(name) == 0 {
			return Invalid[string, string]("Name cannot be empty")
		}
		if len(name) > 100 {
			return Invalid[string, string]("Name too long")
		}
		return Valid[string](name)
	}

	ageValidation := validateAge(25)
	nameValidation := validateName("John Doe")

	if ageValidation.value != nil && nameValidation.value != nil {
		fmt.Printf("Valid: age=%v, name=%v\n", *ageValidation.value, *nameValidation.value)
	}
}

// Performance-optimized generic operations
func SumSimd[T Numeric](slice []T) T {
	var sum T
	// Unroll loop for better performance
	i := 0
	for ; i < len(slice)-3; i += 4 {
		sum += slice[i] + slice[i+1] + slice[i+2] + slice[i+3]
	}
	for ; i < len(slice); i++ {
		sum += slice[i]
	}
	return sum
}

// Generic memoization with TTL
type MemoizedWithTTL[K comparable, V any] struct {
	fn    func(K) V
	cache sync.Map
	ttl   time.Duration
}

type cacheEntry[V any] struct {
	value     V
	timestamp time.Time
}

func (m *MemoizedWithTTL[K, V]) Call(key K) V {
	if cached, ok := m.cache.Load(key); ok {
		entry := cached.(cacheEntry[V])
		if time.Since(entry.timestamp) < m.ttl {
			return entry.value
		}
		m.cache.Delete(key)
	}

	value := m.fn(key)
	m.cache.Store(key, cacheEntry[V]{
		value:     value,
		timestamp: time.Now(),
	})

	return value
}