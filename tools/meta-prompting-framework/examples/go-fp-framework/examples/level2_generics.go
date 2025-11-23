package examples

// Level 2: Generic functional combinators

// Map transforms each element in a slice
func Map[T, R any](slice []T, f func(T) R) []R {
	result := make([]R, len(slice))
	for i, v := range slice {
		result[i] = f(v)
	}
	return result
}

// Filter returns elements that satisfy the predicate
func Filter[T any](slice []T, pred func(T) bool) []T {
	result := make([]T, 0, len(slice))
	for _, v := range slice {
		if pred(v) {
			result = append(result, v)
		}
	}
	return result
}

// Reduce folds a slice into a single value
func Reduce[T, R any](slice []T, initial R, f func(R, T) R) R {
	acc := initial
	for _, v := range slice {
		acc = f(acc, v)
	}
	return acc
}

// FlatMap maps and flattens in one operation
func FlatMap[T, R any](slice []T, f func(T) []R) []R {
	var result []R
	for _, v := range slice {
		result = append(result, f(v)...)
	}
	return result
}

// Partition splits a slice into two based on a predicate
func Partition[T any](slice []T, pred func(T) bool) ([]T, []T) {
	var pass, fail []T
	for _, v := range slice {
		if pred(v) {
			pass = append(pass, v)
		} else {
			fail = append(fail, v)
		}
	}
	return pass, fail
}

// Zip combines two slices into pairs
func Zip[T, U any](slice1 []T, slice2 []U) []struct {
	First  T
	Second U
} {
	minLen := len(slice1)
	if len(slice2) < minLen {
		minLen = len(slice2)
	}

	result := make([]struct {
		First  T
		Second U
	}, minLen)

	for i := 0; i < minLen; i++ {
		result[i] = struct {
			First  T
			Second U
		}{slice1[i], slice2[i]}
	}
	return result
}

// TakeWhile returns elements while predicate is true
func TakeWhile[T any](slice []T, pred func(T) bool) []T {
	for i, v := range slice {
		if !pred(v) {
			return slice[:i]
		}
	}
	return slice
}

// DropWhile removes elements while predicate is true
func DropWhile[T any](slice []T, pred func(T) bool) []T {
	for i, v := range slice {
		if !pred(v) {
			return slice[i:]
		}
	}
	return []T{}
}

// All checks if all elements satisfy the predicate
func All[T any](slice []T, pred func(T) bool) bool {
	for _, v := range slice {
		if !pred(v) {
			return false
		}
	}
	return true
}

// Any checks if any element satisfies the predicate
func Any[T any](slice []T, pred func(T) bool) bool {
	for _, v := range slice {
		if pred(v) {
			return true
		}
	}
	return false
}

// Stream provides lazy evaluation
type Stream[T any] struct {
	next func() (T, bool)
}

// NewStream creates a stream from a slice
func NewStream[T any](slice []T) Stream[T] {
	i := 0
	return Stream[T]{
		next: func() (T, bool) {
			if i >= len(slice) {
				var zero T
				return zero, false
			}
			val := slice[i]
			i++
			return val, true
		},
	}
}

// Map on Stream for lazy transformation
func (s Stream[T]) Map[R any](f func(T) R) Stream[R] {
	return Stream[R]{
		next: func() (R, bool) {
			if v, ok := s.next(); ok {
				return f(v), true
			}
			var zero R
			return zero, false
		},
	}
}

// Filter on Stream for lazy filtering
func (s Stream[T]) Filter(pred func(T) bool) Stream[T] {
	return Stream[T]{
		next: func() (T, bool) {
			for {
				if v, ok := s.next(); ok {
					if pred(v) {
						return v, true
					}
				} else {
					var zero T
					return zero, false
				}
			}
		},
	}
}

// Collect materializes a stream into a slice
func (s Stream[T]) Collect() []T {
	var result []T
	for {
		if v, ok := s.next(); ok {
			result = append(result, v)
		} else {
			break
		}
	}
	return result
}