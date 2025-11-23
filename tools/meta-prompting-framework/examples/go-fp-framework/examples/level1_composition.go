package examples

// Level 1: First-class functions and composition examples

// Compose combines two functions into one
func Compose[A, B, C any](f func(B) C, g func(A) B) func(A) C {
	return func(a A) C {
		return f(g(a))
	}
}

// Pipe is like Compose but with reversed order (more intuitive for pipelines)
func Pipe[A, B, C any](f func(A) B, g func(B) C) func(A) C {
	return func(a A) C {
		return g(f(a))
	}
}

// Identity function - categorical identity morphism
func Identity[T any](x T) T {
	return x
}

// Curry2 converts a 2-argument function into a curried form
func Curry2[A, B, R any](f func(A, B) R) func(A) func(B) R {
	return func(a A) func(B) R {
		return func(b B) R {
			return f(a, b)
		}
	}
}

// Uncurry2 reverses currying
func Uncurry2[A, B, R any](f func(A) func(B) R) func(A, B) R {
	return func(a A, b B) R {
		return f(a)(b)
	}
}

// Partial application helper
func Partial[A, B, R any](f func(A, B) R, a A) func(B) R {
	return func(b B) R {
		return f(a, b)
	}
}

// Memoize caches function results
func Memoize[K comparable, V any](f func(K) V) func(K) V {
	cache := make(map[K]V)
	return func(k K) V {
		if v, ok := cache[k]; ok {
			return v
		}
		v := f(k)
		cache[k] = v
		return v
	}
}

// Example usage:
func ExampleComposition() {
	// Basic composition
	addOne := func(x int) int { return x + 1 }
	double := func(x int) int { return x * 2 }

	// Compose: first double, then add one
	doubleThenAddOne := Compose(addOne, double)
	// Result: (5 * 2) + 1 = 11

	// Pipe: first add one, then double
	addOneThenDouble := Pipe(addOne, double)
	// Result: (5 + 1) * 2 = 12

	// Currying example
	add := func(a, b int) int { return a + b }
	curriedAdd := Curry2(add)
	add5 := curriedAdd(5) // Partial application
	// add5(3) returns 8

	// Memoization for expensive operations
	fibonacci := Memoize(func(n int) int {
		if n <= 1 {
			return n
		}
		// This would normally be recursive and slow
		return n // simplified for example
	})
}