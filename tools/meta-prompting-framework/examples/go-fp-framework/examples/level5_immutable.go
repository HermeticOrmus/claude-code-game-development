package examples

// Level 5: Immutability patterns and persistent data structures

// ImmutableList is a persistent linked list
type ImmutableList[T any] struct {
	head *T
	tail *ImmutableList[T]
	size int
}

// NewList creates an empty list
func NewList[T any]() *ImmutableList[T] {
	return &ImmutableList[T]{size: 0}
}

// Prepend adds element to the front (O(1))
func (l *ImmutableList[T]) Prepend(value T) *ImmutableList[T] {
	return &ImmutableList[T]{
		head: &value,
		tail: l,
		size: l.size + 1,
	}
}

// Head returns the first element
func (l *ImmutableList[T]) Head() (T, bool) {
	if l.head == nil {
		var zero T
		return zero, false
	}
	return *l.head, true
}

// Tail returns the list without the first element
func (l *ImmutableList[T]) Tail() *ImmutableList[T] {
	if l.tail == nil {
		return NewList[T]()
	}
	return l.tail
}

// Size returns the number of elements
func (l *ImmutableList[T]) Size() int {
	return l.size
}

// Map creates a new list with transformed elements
func (l *ImmutableList[T]) Map[R any](f func(T) R) *ImmutableList[R] {
	if l.head == nil {
		return NewList[R]()
	}
	newValue := f(*l.head)
	return l.tail.Map(f).Prepend(newValue)
}

// Filter creates a new list with matching elements
func (l *ImmutableList[T]) Filter(pred func(T) bool) *ImmutableList[T] {
	if l.head == nil {
		return NewList[T]()
	}
	filtered := l.tail.Filter(pred)
	if pred(*l.head) {
		return filtered.Prepend(*l.head)
	}
	return filtered
}

// ToSlice converts to a mutable slice
func (l *ImmutableList[T]) ToSlice() []T {
	result := make([]T, 0, l.size)
	current := l
	for current.head != nil {
		result = append(result, *current.head)
		current = current.tail
	}
	return result
}

// ImmutableMap is a persistent map using path copying
type ImmutableMap[K comparable, V any] struct {
	root *mapNode[K, V]
	size int
}

type mapNode[K comparable, V any] struct {
	key    K
	value  V
	left   *mapNode[K, V]
	right  *mapNode[K, V]
	height int
}

// NewMap creates an empty map
func NewMap[K comparable, V any]() *ImmutableMap[K, V] {
	return &ImmutableMap[K, V]{size: 0}
}

// Set returns a new map with the key-value pair
func (m *ImmutableMap[K, V]) Set(key K, value V) *ImmutableMap[K, V] {
	newRoot, added := m.root.set(key, value)
	newSize := m.size
	if added {
		newSize++
	}
	return &ImmutableMap[K, V]{
		root: newRoot,
		size: newSize,
	}
}

func (n *mapNode[K, V]) set(key K, value V) (*mapNode[K, V], bool) {
	if n == nil {
		return &mapNode[K, V]{
			key:    key,
			value:  value,
			height: 1,
		}, true
	}

	// Create new node (path copying)
	newNode := *n
	added := false

	if key < n.key {
		newNode.left, added = n.left.set(key, value)
	} else if key > n.key {
		newNode.right, added = n.right.set(key, value)
	} else {
		newNode.value = value
		return &newNode, false
	}

	// Update height and rebalance if needed
	newNode.updateHeight()
	return newNode.rebalance(), added
}

func (n *mapNode[K, V]) updateHeight() {
	leftHeight := 0
	rightHeight := 0
	if n.left != nil {
		leftHeight = n.left.height
	}
	if n.right != nil {
		rightHeight = n.right.height
	}
	n.height = max(leftHeight, rightHeight) + 1
}

func (n *mapNode[K, V]) rebalance() *mapNode[K, V] {
	// Simplified - would implement AVL rotations
	return n
}

// Get retrieves a value by key
func (m *ImmutableMap[K, V]) Get(key K) (V, bool) {
	node := m.root.find(key)
	if node == nil {
		var zero V
		return zero, false
	}
	return node.value, true
}

func (n *mapNode[K, V]) find(key K) *mapNode[K, V] {
	if n == nil {
		return nil
	}
	if key < n.key {
		return n.left.find(key)
	}
	if key > n.key {
		return n.right.find(key)
	}
	return n
}

// Lens provides composable updates for nested structures
type Lens[S, A any] struct {
	Get func(S) A
	Set func(A, S) S
}

// Modify applies a transformation through the lens
func (l Lens[S, A]) Modify(f func(A) A) func(S) S {
	return func(s S) S {
		return l.Set(f(l.Get(s)), s)
	}
}

// Compose combines two lenses
func ComposeLens[S, A, B any](outer Lens[S, A], inner Lens[A, B]) Lens[S, B] {
	return Lens[S, B]{
		Get: func(s S) B {
			return inner.Get(outer.Get(s))
		},
		Set: func(b B, s S) S {
			a := outer.Get(s)
			newA := inner.Set(b, a)
			return outer.Set(newA, s)
		},
	}
}

// Example: Person with nested Address
type Person struct {
	Name    string
	Age     int
	Address Address
}

type Address struct {
	Street  string
	City    string
	Country string
}

// Lenses for Person
var PersonNameLens = Lens[Person, string]{
	Get: func(p Person) string { return p.Name },
	Set: func(name string, p Person) Person {
		p.Name = name
		return p
	},
}

var PersonAddressLens = Lens[Person, Address]{
	Get: func(p Person) Address { return p.Address },
	Set: func(addr Address, p Person) Person {
		p.Address = addr
		return p
	},
}

var AddressCityLens = Lens[Address, string]{
	Get: func(a Address) string { return a.City },
	Set: func(city string, a Address) Address {
		a.City = city
		return a
	},
}

// Compose lenses to update nested field
var PersonCityLens = ComposeLens(PersonAddressLens, AddressCityLens)

// Zipper for tree navigation
type Zipper[T any] struct {
	focus   *Tree[T]
	path    []ZipperContext[T]
	changed bool
}

type Tree[T any] struct {
	Value    T
	Children []*Tree[T]
}

type ZipperContext[T any] struct {
	parent   *Tree[T]
	left     []*Tree[T]
	right    []*Tree[T]
	childIdx int
}

// NewZipper creates a zipper for a tree
func NewZipper[T any](tree *Tree[T]) *Zipper[T] {
	return &Zipper[T]{focus: tree}
}

// Down moves to the first child
func (z *Zipper[T]) Down() *Zipper[T] {
	if len(z.focus.Children) == 0 {
		return z
	}

	newZ := *z
	newZ.path = append([]ZipperContext[T]{
		{
			parent:   z.focus,
			left:     nil,
			right:    z.focus.Children[1:],
			childIdx: 0,
		},
	}, z.path...)
	newZ.focus = z.focus.Children[0]
	return &newZ
}

// Up moves to the parent
func (z *Zipper[T]) Up() *Zipper[T] {
	if len(z.path) == 0 {
		return z
	}

	newZ := *z
	ctx := z.path[0]
	newZ.path = z.path[1:]

	// Reconstruct parent with possibly modified child
	newParent := &Tree[T]{
		Value:    ctx.parent.Value,
		Children: make([]*Tree[T], len(ctx.left)+1+len(ctx.right)),
	}

	copy(newParent.Children, ctx.left)
	newParent.Children[len(ctx.left)] = z.focus
	copy(newParent.Children[len(ctx.left)+1:], ctx.right)

	newZ.focus = newParent
	return &newZ
}

// Right moves to the next sibling
func (z *Zipper[T]) Right() *Zipper[T] {
	if len(z.path) == 0 || len(z.path[0].right) == 0 {
		return z
	}

	newZ := *z
	ctx := z.path[0]

	newZ.path[0] = ZipperContext[T]{
		parent:   ctx.parent,
		left:     append(ctx.left, z.focus),
		right:    ctx.right[1:],
		childIdx: ctx.childIdx + 1,
	}
	newZ.focus = ctx.right[0]

	return &newZ
}

// Update modifies the current focus value
func (z *Zipper[T]) Update(value T) *Zipper[T] {
	newZ := *z
	newZ.focus = &Tree[T]{
		Value:    value,
		Children: z.focus.Children,
	}
	newZ.changed = true
	return &newZ
}

// ToTree reconstructs the complete tree
func (z *Zipper[T]) ToTree() *Tree[T] {
	current := z
	for len(current.path) > 0 {
		current = current.Up()
	}
	return current.focus
}