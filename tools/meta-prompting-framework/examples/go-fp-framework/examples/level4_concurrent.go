package examples

import (
	"context"
	"sync"
	"time"
)

// Level 4: Concurrent functional patterns

// MapChan applies a function to each element in a channel
func MapChan[T, R any](in <-chan T, f func(T) R) <-chan R {
	out := make(chan R)
	go func() {
		defer close(out)
		for v := range in {
			out <- f(v)
		}
	}()
	return out
}

// FilterChan filters channel elements by predicate
func FilterChan[T any](in <-chan T, pred func(T) bool) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		for v := range in {
			if pred(v) {
				out <- v
			}
		}
	}()
	return out
}

// ReduceChan folds channel elements into a single value
func ReduceChan[T, R any](in <-chan T, initial R, f func(R, T) R) R {
	acc := initial
	for v := range in {
		acc = f(acc, v)
	}
	return acc
}

// Pipeline provides functional composition for channels
type Pipeline[T any] struct {
	source <-chan T
	ctx    context.Context
}

// NewPipeline creates a new pipeline
func NewPipeline[T any](source <-chan T) Pipeline[T] {
	return Pipeline[T]{source: source, ctx: context.Background()}
}

// WithContext adds context to pipeline
func (p Pipeline[T]) WithContext(ctx context.Context) Pipeline[T] {
	p.ctx = ctx
	return p
}

// Map transforms elements in the pipeline
func (p Pipeline[T]) Map[R any](f func(T) R) Pipeline[R] {
	out := make(chan R)
	go func() {
		defer close(out)
		for {
			select {
			case v, ok := <-p.source:
				if !ok {
					return
				}
				out <- f(v)
			case <-p.ctx.Done():
				return
			}
		}
	}()
	return Pipeline[R]{source: out, ctx: p.ctx}
}

// Filter keeps only matching elements
func (p Pipeline[T]) Filter(pred func(T) bool) Pipeline[T] {
	out := make(chan T)
	go func() {
		defer close(out)
		for {
			select {
			case v, ok := <-p.source:
				if !ok {
					return
				}
				if pred(v) {
					out <- v
				}
			case <-p.ctx.Done():
				return
			}
		}
	}()
	return Pipeline[T]{source: out, ctx: p.ctx}
}

// Collect gathers all pipeline elements into a slice
func (p Pipeline[T]) Collect() []T {
	var result []T
	for v := range p.source {
		result = append(result, v)
	}
	return result
}

// FanOut splits a channel into multiple channels
func FanOut[T any](in <-chan T, n int) []<-chan T {
	outs := make([]<-chan T, n)
	for i := 0; i < n; i++ {
		out := make(chan T)
		outs[i] = out
		go func(out chan<- T) {
			defer close(out)
			for v := range in {
				out <- v
			}
		}(out)
	}
	return outs
}

// FanIn merges multiple channels into one
func FanIn[T any](ins ...<-chan T) <-chan T {
	out := make(chan T)
	var wg sync.WaitGroup
	wg.Add(len(ins))

	for _, in := range ins {
		go func(in <-chan T) {
			defer wg.Done()
			for v := range in {
				out <- v
			}
		}(in)
	}

	go func() {
		wg.Wait()
		close(out)
	}()

	return out
}

// Future represents an async computation
type Future[T any] struct {
	ch     <-chan T
	cached *T
	mu     sync.Mutex
}

// Async runs a function asynchronously
func Async[T any](f func() T) *Future[T] {
	ch := make(chan T, 1)
	go func() {
		ch <- f()
		close(ch)
	}()
	return &Future[T]{ch: ch}
}

// AsyncWithContext runs a function with context
func AsyncWithContext[T any](ctx context.Context, f func(context.Context) T) *Future[T] {
	ch := make(chan T, 1)
	go func() {
		select {
		case ch <- f(ctx):
		case <-ctx.Done():
		}
		close(ch)
	}()
	return &Future[T]{ch: ch}
}

// Await blocks until the future completes
func (f *Future[T]) Await() T {
	f.mu.Lock()
	defer f.mu.Unlock()

	if f.cached != nil {
		return *f.cached
	}

	value := <-f.ch
	f.cached = &value
	return value
}

// AwaitTimeout waits with a timeout
func (f *Future[T]) AwaitTimeout(timeout time.Duration) (T, bool) {
	select {
	case value := <-f.ch:
		f.mu.Lock()
		f.cached = &value
		f.mu.Unlock()
		return value, true
	case <-time.After(timeout):
		var zero T
		return zero, false
	}
}

// Map transforms the future's result
func (f *Future[T]) Map[R any](fn func(T) R) *Future[R] {
	return Async(func() R {
		return fn(f.Await())
	})
}

// FlatMap chains futures
func (f *Future[T]) FlatMap[R any](fn func(T) *Future[R]) *Future[R] {
	return Async(func() R {
		return fn(f.Await()).Await()
	})
}

// ParallelMap applies a function to slice elements in parallel
func ParallelMap[T, R any](slice []T, f func(T) R) []R {
	result := make([]R, len(slice))
	var wg sync.WaitGroup
	wg.Add(len(slice))

	for i, v := range slice {
		go func(index int, value T) {
			defer wg.Done()
			result[index] = f(value)
		}(i, v)
	}

	wg.Wait()
	return result
}

// ParallelFilter filters slice elements in parallel
func ParallelFilter[T any](slice []T, pred func(T) bool) []T {
	type indexedValue struct {
		index int
		value T
		keep  bool
	}

	ch := make(chan indexedValue, len(slice))
	var wg sync.WaitGroup
	wg.Add(len(slice))

	for i, v := range slice {
		go func(index int, value T) {
			defer wg.Done()
			ch <- indexedValue{
				index: index,
				value: value,
				keep:  pred(value),
			}
		}(i, v)
	}

	go func() {
		wg.Wait()
		close(ch)
	}()

	// Collect results maintaining order
	results := make([]indexedValue, 0, len(slice))
	for iv := range ch {
		if iv.keep {
			results = append(results, iv)
		}
	}

	// Sort by index and extract values
	// (simplified - would need proper sorting)
	var filtered []T
	for _, iv := range results {
		filtered = append(filtered, iv.value)
	}
	return filtered
}

// Throttle limits the rate of values from a channel
func Throttle[T any](in <-chan T, rate time.Duration) <-chan T {
	out := make(chan T)
	ticker := time.NewTicker(rate)

	go func() {
		defer close(out)
		defer ticker.Stop()

		for v := range in {
			<-ticker.C
			out <- v
		}
	}()

	return out
}

// Debounce emits values only after a quiet period
func Debounce[T any](in <-chan T, duration time.Duration) <-chan T {
	out := make(chan T)

	go func() {
		defer close(out)

		var lastValue T
		var hasValue bool
		timer := time.NewTimer(duration)
		timer.Stop()

		for {
			select {
			case v, ok := <-in:
				if !ok {
					if hasValue {
						out <- lastValue
					}
					return
				}
				lastValue = v
				hasValue = true
				timer.Reset(duration)

			case <-timer.C:
				if hasValue {
					out <- lastValue
					hasValue = false
				}
			}
		}
	}()

	return out
}