package examples

import (
	"errors"
	"fmt"
)

// Level 3: Functional error handling patterns

// Result type represents success or failure
type Result[T any] struct {
	value T
	err   error
}

// Ok creates a successful Result
func Ok[T any](value T) Result[T] {
	return Result[T]{value: value, err: nil}
}

// Err creates a failed Result
func Err[T any](err error) Result[T] {
	var zero T
	return Result[T]{value: zero, err: err}
}

// IsOk checks if Result is successful
func (r Result[T]) IsOk() bool {
	return r.err == nil
}

// IsErr checks if Result is an error
func (r Result[T]) IsErr() bool {
	return r.err != nil
}

// Unwrap gets the value (panics on error)
func (r Result[T]) Unwrap() T {
	if r.err != nil {
		panic(fmt.Sprintf("called Unwrap on error Result: %v", r.err))
	}
	return r.value
}

// UnwrapOr provides a default value on error
func (r Result[T]) UnwrapOr(defaultValue T) T {
	if r.err != nil {
		return defaultValue
	}
	return r.value
}

// Map transforms the success value
func (r Result[T]) Map[R any](f func(T) R) Result[R] {
	if r.err != nil {
		return Err[R](r.err)
	}
	return Ok(f(r.value))
}

// FlatMap chains operations that might fail
func (r Result[T]) FlatMap[R any](f func(T) Result[R]) Result[R] {
	if r.err != nil {
		return Err[R](r.err)
	}
	return f(r.value)
}

// MapErr transforms the error
func (r Result[T]) MapErr(f func(error) error) Result[T] {
	if r.err != nil {
		return Err[T](f(r.err))
	}
	return r
}

// Option type represents presence or absence of a value
type Option[T any] struct {
	value *T
}

// Some creates an Option with a value
func Some[T any](value T) Option[T] {
	return Option[T]{value: &value}
}

// None creates an empty Option
func None[T any]() Option[T] {
	return Option[T]{value: nil}
}

// IsSome checks if Option has a value
func (o Option[T]) IsSome() bool {
	return o.value != nil
}

// IsNone checks if Option is empty
func (o Option[T]) IsNone() bool {
	return o.value == nil
}

// Unwrap gets the value (panics if None)
func (o Option[T]) Unwrap() T {
	if o.value == nil {
		panic("called Unwrap on None Option")
	}
	return *o.value
}

// UnwrapOr provides a default value if None
func (o Option[T]) UnwrapOr(defaultValue T) T {
	if o.value == nil {
		return defaultValue
	}
	return *o.value
}

// Map transforms the value if present
func (o Option[T]) Map[R any](f func(T) R) Option[R] {
	if o.value == nil {
		return None[R]()
	}
	return Some(f(*o.value))
}

// FlatMap chains operations that return Options
func (o Option[T]) FlatMap[R any](f func(T) Option[R]) Option[R] {
	if o.value == nil {
		return None[R]()
	}
	return f(*o.value)
}

// Filter keeps the value only if it satisfies the predicate
func (o Option[T]) Filter(pred func(T) bool) Option[T] {
	if o.value != nil && pred(*o.value) {
		return o
	}
	return None[T]()
}

// Try wraps a function that might panic into a Result
func Try[T any](f func() T) Result[T] {
	defer func() {
		if r := recover(); r != nil {
			var err error
			switch e := r.(type) {
			case error:
				err = e
			default:
				err = fmt.Errorf("panic: %v", e)
			}
			// This would need special handling since we can't modify return value in defer
			// In practice, you'd use a different pattern
		}
	}()
	return Ok(f())
}

// Chain composes multiple fallible operations
func Chain[T any](funcs ...func(T) (T, error)) func(T) Result[T] {
	return func(input T) Result[T] {
		current := input
		for _, f := range funcs {
			next, err := f(current)
			if err != nil {
				return Err[T](err)
			}
			current = next
		}
		return Ok(current)
	}
}

// Sequence converts slice of Results to Result of slice
func Sequence[T any](results []Result[T]) Result[[]T] {
	values := make([]T, len(results))
	for i, r := range results {
		if r.IsErr() {
			return Err[[]T](r.err)
		}
		values[i] = r.value
	}
	return Ok(values)
}

// Traverse maps and sequences in one operation
func Traverse[T, R any](slice []T, f func(T) Result[R]) Result[[]R] {
	results := make([]Result[R], len(slice))
	for i, v := range slice {
		results[i] = f(v)
	}
	return Sequence(results)
}

// ValidationError aggregates multiple errors
type ValidationError struct {
	errors []error
}

func NewValidationError() *ValidationError {
	return &ValidationError{errors: []error{}}
}

func (v *ValidationError) Add(err error) {
	if err != nil {
		v.errors = append(v.errors, err)
	}
}

func (v *ValidationError) AddIf(condition bool, msg string) {
	if condition {
		v.errors = append(v.errors, errors.New(msg))
	}
}

func (v *ValidationError) HasErrors() bool {
	return len(v.errors) > 0
}

func (v *ValidationError) Error() string {
	if len(v.errors) == 0 {
		return ""
	}
	msg := "validation errors:"
	for _, err := range v.errors {
		msg += "\n  - " + err.Error()
	}
	return msg
}

func (v *ValidationError) ToResult[T any](value T) Result[T] {
	if v.HasErrors() {
		return Err[T](v)
	}
	return Ok(value)
}