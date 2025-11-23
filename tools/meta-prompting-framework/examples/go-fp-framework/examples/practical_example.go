package examples

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"time"
)

// Practical Example: A functional data processing pipeline
// This example combines multiple levels of the framework

// Domain types
type User struct {
	ID        string
	Name      string
	Email     string
	Age       int
	CreatedAt time.Time
	Score     float64
}

type ProcessedUser struct {
	User
	Category    string
	RiskScore   float64
	Processed   time.Time
	ValidatedAt *time.Time
}

// Level 3: Error handling with Result type
type UserProcessor struct {
	validators []func(User) Result[User]
	enrichers  []func(User) Result[User]
}

// Level 1: Function composition for validation
func (p *UserProcessor) AddValidator(v func(User) Result[User]) *UserProcessor {
	p.validators = append(p.validators, v)
	return p
}

// Level 2: Generic map operation
func (p *UserProcessor) ProcessBatch(users []User) []Result[ProcessedUser] {
	return Map(users, p.ProcessSingle)
}

// Level 3: Monadic error composition
func (p *UserProcessor) ProcessSingle(user User) Result[ProcessedUser] {
	// Chain validators
	result := Ok(user)
	for _, validator := range p.validators {
		result = result.FlatMap(validator)
	}

	// Chain enrichers
	for _, enricher := range p.enrichers {
		result = result.FlatMap(enricher)
	}

	// Transform to ProcessedUser
	return result.Map(func(u User) ProcessedUser {
		now := time.Now()
		return ProcessedUser{
			User:        u,
			Category:    categorizeUser(u),
			RiskScore:   calculateRiskScore(u),
			Processed:   now,
			ValidatedAt: &now,
		}
	})
}

// Validation functions using Result type
func validateAge(user User) Result[User] {
	if user.Age < 18 || user.Age > 120 {
		return Err[User](fmt.Errorf("invalid age: %d", user.Age))
	}
	return Ok(user)
}

func validateEmail(user User) Result[User] {
	if len(user.Email) < 3 || len(user.Email) > 100 {
		return Err[User](errors.New("invalid email length"))
	}
	return Ok(user)
}

func validateScore(user User) Result[User] {
	if user.Score < 0 || user.Score > 100 {
		return Err[User](fmt.Errorf("invalid score: %.2f", user.Score))
	}
	return Ok(user)
}

// Helper functions
func categorizeUser(user User) string {
	switch {
	case user.Score >= 80:
		return "premium"
	case user.Score >= 50:
		return "standard"
	default:
		return "basic"
	}
}

func calculateRiskScore(user User) float64 {
	base := 50.0
	if user.Age < 25 {
		base += 10
	}
	if user.Score < 30 {
		base += 20
	}
	if time.Since(user.CreatedAt) < 30*24*time.Hour {
		base += 15
	}
	return base
}

// Level 4: Concurrent processing pipeline
type ConcurrentUserPipeline struct {
	processor *UserProcessor
	workers   int
}

func NewConcurrentPipeline(workers int) *ConcurrentUserPipeline {
	processor := &UserProcessor{}
	processor.AddValidator(func(u User) Result[User] { return validateAge(u) })
	processor.AddValidator(func(u User) Result[User] { return validateEmail(u) })
	processor.AddValidator(func(u User) Result[User] { return validateScore(u) })

	return &ConcurrentUserPipeline{
		processor: processor,
		workers:   workers,
	}
}

// Level 4: Channel-based streaming with Level 2 generics
func (p *ConcurrentUserPipeline) StreamProcess(ctx context.Context, input <-chan User) <-chan Result[ProcessedUser] {
	output := make(chan Result[ProcessedUser])

	// Fan-out: distribute work to multiple workers
	workerInputs := make([]chan User, p.workers)
	for i := 0; i < p.workers; i++ {
		workerInputs[i] = make(chan User, 10)
	}

	// Distributor
	go func() {
		defer func() {
			for _, ch := range workerInputs {
				close(ch)
			}
		}()

		i := 0
		for user := range input {
			select {
			case workerInputs[i%p.workers] <- user:
				i++
			case <-ctx.Done():
				return
			}
		}
	}()

	// Workers
	workerOutputs := make([]<-chan Result[ProcessedUser], p.workers)
	for i := 0; i < p.workers; i++ {
		workerOutput := make(chan Result[ProcessedUser])
		workerOutputs[i] = workerOutput

		go func(input <-chan User, output chan<- Result[ProcessedUser]) {
			defer close(output)
			for user := range input {
				select {
				case output <- p.processor.ProcessSingle(user):
				case <-ctx.Done():
					return
				}
			}
		}(workerInputs[i], workerOutput)
	}

	// Fan-in: merge results
	go func() {
		defer close(output)
		for result := range FanIn(workerOutputs...) {
			select {
			case output <- result:
			case <-ctx.Done():
				return
			}
		}
	}()

	return output
}

// Level 5: Immutable audit log using persistent data structures
type AuditLog struct {
	entries *ImmutableList[AuditEntry]
	index   *ImmutableMap[string, *ImmutableList[AuditEntry]]
}

type AuditEntry struct {
	ID        string
	UserID    string
	Action    string
	Timestamp time.Time
	Details   json.RawMessage
}

func NewAuditLog() *AuditLog {
	return &AuditLog{
		entries: NewList[AuditEntry](),
		index:   NewMap[string, *ImmutableList[AuditEntry]](),
	}
}

// Returns a new immutable audit log with the entry added
func (log *AuditLog) AddEntry(entry AuditEntry) *AuditLog {
	// Add to main list
	newEntries := log.entries.Prepend(entry)

	// Update index
	userEntries, exists := log.index.Get(entry.UserID)
	if !exists {
		userEntries = NewList[AuditEntry]()
	}
	userEntries = userEntries.Prepend(entry)
	newIndex := log.index.Set(entry.UserID, userEntries)

	return &AuditLog{
		entries: newEntries,
		index:   newIndex,
	}
}

// Get entries for a specific user (immutable)
func (log *AuditLog) GetUserEntries(userID string) []AuditEntry {
	entries, exists := log.index.Get(userID)
	if !exists {
		return []AuditEntry{}
	}
	return entries.ToSlice()
}

// Combined example using multiple levels
func ProcessUserDataPipeline(ctx context.Context) {
	// Create sample data source
	users := make(chan User)
	go func() {
		defer close(users)
		for i := 0; i < 100; i++ {
			select {
			case users <- User{
				ID:        fmt.Sprintf("user-%d", i),
				Name:      fmt.Sprintf("User %d", i),
				Email:     fmt.Sprintf("user%d@example.com", i),
				Age:       20 + i%60,
				Score:     float64(i % 101),
				CreatedAt: time.Now().Add(-time.Duration(i) * 24 * time.Hour),
			}:
			case <-ctx.Done():
				return
			}
		}
	}()

	// Level 4: Create concurrent pipeline
	pipeline := NewConcurrentPipeline(4)

	// Level 5: Initialize immutable audit log
	auditLog := NewAuditLog()

	// Process stream
	results := pipeline.StreamProcess(ctx, users)

	// Level 2: Collect and filter results
	var successCount, errorCount int
	for result := range results {
		if result.IsOk() {
			processed := result.Unwrap()

			// Level 5: Add to immutable audit log
			entry := AuditEntry{
				ID:        fmt.Sprintf("audit-%d", successCount),
				UserID:    processed.ID,
				Action:    "user_processed",
				Timestamp: processed.Processed,
				Details:   json.RawMessage(fmt.Sprintf(`{"category":"%s","risk_score":%.2f}`, processed.Category, processed.RiskScore)),
			}
			auditLog = auditLog.AddEntry(entry)
			successCount++
		} else {
			errorCount++
		}
	}

	fmt.Printf("Processing complete: %d successful, %d errors\n", successCount, errorCount)
	fmt.Printf("Audit log has %d entries\n", auditLog.entries.Size())
}

// Level 1 & 3: Functional option pattern with Result type
type ProcessorConfig struct {
	MaxAge      int
	MinScore    float64
	RequireEmail bool
	Timeout      time.Duration
}

type ProcessorOption func(*ProcessorConfig) Result[*ProcessorConfig]

func WithMaxAge(age int) ProcessorOption {
	return func(c *ProcessorConfig) Result[*ProcessorConfig] {
		if age < 0 || age > 150 {
			return Err[*ProcessorConfig](fmt.Errorf("invalid max age: %d", age))
		}
		c.MaxAge = age
		return Ok(c)
	}
}

func WithMinScore(score float64) ProcessorOption {
	return func(c *ProcessorConfig) Result[*ProcessorConfig] {
		if score < 0 || score > 100 {
			return Err[*ProcessorConfig](fmt.Errorf("invalid min score: %.2f", score))
		}
		c.MinScore = score
		return Ok(c)
	}
}

func WithTimeout(timeout time.Duration) ProcessorOption {
	return func(c *ProcessorConfig) Result[*ProcessorConfig] {
		if timeout <= 0 {
			return Err[*ProcessorConfig](errors.New("timeout must be positive"))
		}
		c.Timeout = timeout
		return Ok(c)
	}
}

// Build configuration with validation
func BuildConfig(opts ...ProcessorOption) Result[*ProcessorConfig] {
	config := &ProcessorConfig{
		MaxAge:       120,
		MinScore:     0,
		RequireEmail: true,
		Timeout:      30 * time.Second,
	}

	result := Ok(config)
	for _, opt := range opts {
		result = result.FlatMap(func(c *ProcessorConfig) Result[*ProcessorConfig] {
			return opt(c)
		})
	}

	return result
}