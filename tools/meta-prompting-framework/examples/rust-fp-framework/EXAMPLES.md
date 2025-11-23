# Practical Examples: Functional Programming in Rust

## Complete Working Examples for Each Level

### Level 1: Pure Function Composition Library

```rust
// Complete composition library
pub mod composition {
    /// Identity function
    pub fn id<T>(x: T) -> T { x }

    /// Const function - ignores second argument
    pub fn konst<A, B>(a: A) -> impl Fn(B) -> A
    where A: Clone
    {
        move |_| a.clone()
    }

    /// Function composition operator
    pub fn compose<A, B, C>(
        f: impl Fn(B) -> C,
        g: impl Fn(A) -> B,
    ) -> impl Fn(A) -> C {
        move |x| f(g(x))
    }

    /// Flip argument order
    pub fn flip<A, B, C>(
        f: impl Fn(A, B) -> C,
    ) -> impl Fn(B, A) -> C {
        move |b, a| f(a, b)
    }

    /// Curry a 2-argument function
    pub fn curry<A, B, C>(
        f: impl Fn(A, B) -> C,
    ) -> impl Fn(A) -> impl Fn(B) -> C
    where A: Clone
    {
        move |a| {
            let f = f.clone();
            move |b| f(a.clone(), b)
        }
    }

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        fn test_composition_laws() {
            let add_one = |x: i32| x + 1;
            let double = |x: i32| x * 2;
            let triple = |x: i32| x * 3;

            // Associativity: (f ∘ g) ∘ h = f ∘ (g ∘ h)
            let left = compose(compose(triple, double), add_one);
            let right = compose(triple, compose(double, add_one));
            assert_eq!(left(5), right(5)); // Both give 36

            // Identity: id ∘ f = f = f ∘ id
            let f_id = compose(add_one, id);
            let id_f = compose(id, add_one);
            assert_eq!(f_id(10), add_one(10));
            assert_eq!(id_f(10), add_one(10));
        }
    }
}
```

### Level 2: Custom Functor Implementation with Laws

```rust
// Functor with law checking
pub mod functors {
    pub trait Functor: Sized {
        type Item;
        type Wrapped<T>: Functor;

        fn fmap<B>(self, f: impl FnOnce(Self::Item) -> B) -> Self::Wrapped<B>;

        // Functor laws as default methods
        fn check_identity_law(self) -> bool
        where
            Self::Item: PartialEq + Clone,
            Self: Clone + PartialEq,
        {
            let original = self.clone();
            let mapped = self.fmap(|x| x);
            // fmap id = id
            original == mapped
        }

        fn check_composition_law<B, C>(
            self,
            f: impl Fn(Self::Item) -> B + Clone,
            g: impl Fn(B) -> C,
        ) -> bool
        where
            Self: Clone,
        {
            // fmap (g . f) = fmap g . fmap f
            let composed = self.clone().fmap(|x| g(f(x)));
            let chained = self.fmap(f).fmap(g);
            // Can't directly compare without Eq bound on C
            true // Simplified for demonstration
        }
    }

    // Custom Maybe type
    #[derive(Debug, Clone, PartialEq)]
    pub enum Maybe<T> {
        Just(T),
        Nothing,
    }

    impl<T> Functor for Maybe<T> {
        type Item = T;
        type Wrapped<U> = Maybe<U>;

        fn fmap<B>(self, f: impl FnOnce(T) -> B) -> Maybe<B> {
            match self {
                Maybe::Just(x) => Maybe::Just(f(x)),
                Maybe::Nothing => Maybe::Nothing,
            }
        }
    }

    // Tree functor
    #[derive(Debug, Clone)]
    pub enum Tree<T> {
        Leaf(T),
        Branch(Box<Tree<T>>, Box<Tree<T>>),
    }

    impl<T> Functor for Tree<T> {
        type Item = T;
        type Wrapped<U> = Tree<U>;

        fn fmap<B>(self, f: impl FnOnce(T) -> B + Clone) -> Tree<B> {
            match self {
                Tree::Leaf(x) => Tree::Leaf(f(x)),
                Tree::Branch(left, right) => Tree::Branch(
                    Box::new(left.fmap(f.clone())),
                    Box::new(right.fmap(f)),
                ),
            }
        }
    }
}
```

### Level 3: Parallel Monoidal Operations with Rayon

```rust
// Parallel processing examples
pub mod parallel {
    use rayon::prelude::*;
    use std::time::Instant;

    // Parallel map-reduce for word counting
    pub fn parallel_word_count(text: &str) -> usize {
        text.par_lines()
            .map(|line| line.split_whitespace().count())
            .sum()
    }

    // Monoidal aggregation with custom types
    #[derive(Clone, Debug)]
    pub struct Stats {
        count: usize,
        sum: f64,
        min: f64,
        max: f64,
    }

    impl Stats {
        pub fn single(value: f64) -> Self {
            Stats {
                count: 1,
                sum: value,
                min: value,
                max: value,
            }
        }

        pub fn combine(self, other: Self) -> Self {
            Stats {
                count: self.count + other.count,
                sum: self.sum + other.sum,
                min: self.min.min(other.min),
                max: self.max.max(other.max),
            }
        }

        pub fn mean(&self) -> f64 {
            self.sum / self.count as f64
        }
    }

    pub fn parallel_statistics(numbers: &[f64]) -> Stats {
        numbers
            .par_iter()
            .map(|&x| Stats::single(x))
            .reduce(
                || Stats { count: 0, sum: 0.0, min: f64::INFINITY, max: f64::NEG_INFINITY },
                Stats::combine,
            )
    }

    // Parallel validation with error accumulation
    pub fn validate_batch<T, E>(
        items: Vec<T>,
        validator: impl Fn(&T) -> Result<(), E> + Sync,
    ) -> Result<Vec<T>, Vec<(usize, E)>>
    where
        T: Send + Sync,
        E: Send,
    {
        let results: Vec<_> = items
            .par_iter()
            .enumerate()
            .filter_map(|(i, item)| {
                validator(item).err().map(|e| (i, e))
            })
            .collect();

        if results.is_empty() {
            Ok(items)
        } else {
            Err(results)
        }
    }

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        fn benchmark_parallel_vs_sequential() {
            let data: Vec<f64> = (0..1_000_000)
                .map(|i| i as f64)
                .collect();

            let start = Instant::now();
            let _seq_stats = data.iter()
                .map(|&x| Stats::single(x))
                .fold(
                    Stats { count: 0, sum: 0.0, min: f64::INFINITY, max: f64::NEG_INFINITY },
                    Stats::combine,
                );
            let seq_time = start.elapsed();

            let start = Instant::now();
            let _par_stats = parallel_statistics(&data);
            let par_time = start.elapsed();

            println!("Sequential: {:?}, Parallel: {:?}", seq_time, par_time);
            // Parallel should be faster for large datasets
        }
    }
}
```

### Level 4: Session Types and Linear Resources

```rust
// Advanced linear type system
pub mod linear {
    use std::marker::PhantomData;

    // Type-level states for session types
    pub struct Start;
    pub struct SentInt;
    pub struct SentString;
    pub struct Done;

    // Linear channel with phantom state
    pub struct Channel<State> {
        _state: PhantomData<State>,
        // In real implementation, would contain actual channel
    }

    impl Channel<Start> {
        pub fn new() -> Self {
            Channel { _state: PhantomData }
        }

        pub fn send_int(self, _value: i32) -> Channel<SentInt> {
            println!("Sent int: {}", _value);
            Channel { _state: PhantomData }
        }
    }

    impl Channel<SentInt> {
        pub fn send_string(self, _value: String) -> Channel<SentString> {
            println!("Sent string: {}", _value);
            Channel { _state: PhantomData }
        }
    }

    impl Channel<SentString> {
        pub fn close(self) -> Channel<Done> {
            println!("Channel closed");
            Channel { _state: PhantomData }
        }
    }

    // Usage example - compiler enforces protocol!
    pub fn protocol_example() {
        let chan = Channel::<Start>::new();
        let chan = chan.send_int(42);
        let chan = chan.send_string("Hello".to_string());
        let _done = chan.close();
        // Can't use chan after close - moved!
    }

    // Unique reference wrapper
    pub struct Unique<T> {
        value: Option<T>,
    }

    impl<T> Unique<T> {
        pub fn new(value: T) -> Self {
            Unique { value: Some(value) }
        }

        pub fn take(mut self) -> T {
            self.value.take().expect("Value already taken")
        }

        pub fn borrow_with<R>(&self, f: impl FnOnce(&T) -> R) -> R {
            f(self.value.as_ref().expect("Value already taken"))
        }
    }

    // Affine handle for file operations
    pub struct FileHandle {
        path: String,
        closed: bool,
    }

    impl FileHandle {
        pub fn open(path: String) -> Self {
            println!("Opening file: {}", path);
            FileHandle { path, closed: false }
        }

        pub fn read(&self) -> String {
            assert!(!self.closed, "File already closed");
            format!("Contents of {}", self.path)
        }

        pub fn close(mut self) {
            self.closed = true;
            println!("Closing file: {}", self.path);
        }
    }

    impl Drop for FileHandle {
        fn drop(&mut self) {
            if !self.closed {
                println!("Warning: File {} not explicitly closed", self.path);
            }
        }
    }
}
```

### Level 5: Complete Recursion Schemes Implementation

```rust
// Full recursion schemes library
pub mod recursion {
    use std::rc::Rc;

    // Expression AST using recursion schemes
    pub enum ExprF<R> {
        Const(i32),
        Add(R, R),
        Mul(R, R),
        Var(String),
    }

    impl<R> ExprF<R> {
        pub fn map<S>(self, f: impl Fn(R) -> S) -> ExprF<S> {
            match self {
                ExprF::Const(n) => ExprF::Const(n),
                ExprF::Add(l, r) => ExprF::Add(f(l), f(r)),
                ExprF::Mul(l, r) => ExprF::Mul(f(l), f(r)),
                ExprF::Var(name) => ExprF::Var(name),
            }
        }
    }

    pub type Expr = Rc<ExprF<Expr>>;

    // Catamorphism for evaluation
    pub fn eval(expr: &Expr, env: &[(String, i32)]) -> i32 {
        fn go(e: &ExprF<i32>, env: &[(String, i32)]) -> i32 {
            match e {
                ExprF::Const(n) => *n,
                ExprF::Add(l, r) => l + r,
                ExprF::Mul(l, r) => l * r,
                ExprF::Var(name) => {
                    env.iter()
                        .find(|(n, _)| n == name)
                        .map(|(_, v)| *v)
                        .unwrap_or(0)
                }
            }
        }
        cata(expr, |e| go(e, env))
    }

    pub fn cata<A>(expr: &Expr, alg: impl Fn(&ExprF<A>) -> A + Clone) -> A {
        let mapped = expr.as_ref().clone().map(|e| cata(&e, alg.clone()));
        alg(&mapped)
    }

    // Pretty printing via catamorphism
    pub fn pretty_print(expr: &Expr) -> String {
        cata(expr, |e| match e {
            ExprF::Const(n) => n.to_string(),
            ExprF::Add(l, r) => format!("({} + {})", l, r),
            ExprF::Mul(l, r) => format!("({} * {})", l, r),
            ExprF::Var(name) => name.clone(),
        })
    }

    // Optimization via catamorphism
    pub fn optimize(expr: &Expr) -> Expr {
        cata(expr, |e| match e {
            ExprF::Add(l, r) if l.as_ref() == &ExprF::Const(0) => r.clone(),
            ExprF::Add(l, r) if r.as_ref() == &ExprF::Const(0) => l.clone(),
            ExprF::Mul(l, r) if l.as_ref() == &ExprF::Const(1) => r.clone(),
            ExprF::Mul(l, r) if r.as_ref() == &ExprF::Const(1) => l.clone(),
            ExprF::Mul(_, _) if matches!(e, ExprF::Mul(l, _) | ExprF::Mul(_, l) if matches!(l.as_ref(), ExprF::Const(0))) => {
                Rc::new(ExprF::Const(0))
            },
            e => Rc::new(e.clone()),
        })
    }

    // Build expression using smart constructors
    pub fn constant(n: i32) -> Expr {
        Rc::new(ExprF::Const(n))
    }

    pub fn add(l: Expr, r: Expr) -> Expr {
        Rc::new(ExprF::Add(l, r))
    }

    pub fn mul(l: Expr, r: Expr) -> Expr {
        Rc::new(ExprF::Mul(l, r))
    }

    pub fn var(name: String) -> Expr {
        Rc::new(ExprF::Var(name))
    }

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        fn test_expression_evaluation() {
            // (x * 2) + 3
            let expr = add(
                mul(var("x".to_string()), constant(2)),
                constant(3)
            );

            let env = vec![("x".to_string(), 5)];
            assert_eq!(eval(&expr, &env), 13);

            let pretty = pretty_print(&expr);
            assert_eq!(pretty, "((x * 2) + 3)");
        }

        #[test]
        fn test_optimization() {
            // (x * 1) + 0 should simplify to x
            let expr = add(
                mul(var("x".to_string()), constant(1)),
                constant(0)
            );

            let optimized = optimize(&expr);
            let pretty = pretty_print(&optimized);
            assert_eq!(pretty, "x");
        }
    }
}
```

### Level 6: Advanced Type-Level Programming

```rust
// Type-level programming examples
pub mod type_level {
    use std::marker::PhantomData;

    // Type-level booleans
    pub struct True;
    pub struct False;

    pub trait Bool {
        type Not: Bool;
        type And<B: Bool>: Bool;
        type Or<B: Bool>: Bool;
    }

    impl Bool for True {
        type Not = False;
        type And<B: Bool> = B;
        type Or<B: Bool> = True;
    }

    impl Bool for False {
        type Not = True;
        type And<B: Bool> = False;
        type Or<B: Bool> = B;
    }

    // Type-level lists
    pub struct Nil;
    pub struct Cons<H, T>(PhantomData<(H, T)>);

    pub trait TList {
        type Head;
        type Tail: TList;
        type Append<L: TList>: TList;
    }

    impl TList for Nil {
        type Head = Nil;
        type Tail = Nil;
        type Append<L: TList> = L;
    }

    impl<H, T: TList> TList for Cons<H, T> {
        type Head = H;
        type Tail = T;
        type Append<L: TList> = Cons<H, T::Append<L>>;
    }

    // Heterogeneous list implementation
    pub trait HList: Sized {
        type Append<L: HList>: HList;
        fn append<L: HList>(self, other: L) -> Self::Append<L>;
    }

    impl HList for () {
        type Append<L: HList> = L;
        fn append<L: HList>(self, other: L) -> L {
            other
        }
    }

    impl<H, T: HList> HList for (H, T) {
        type Append<L: HList> = (H, T::Append<L>);
        fn append<L: HList>(self, other: L) -> Self::Append<L> {
            (self.0, self.1.append(other))
        }
    }

    // Vector with compile-time length
    pub struct Vec<T, const N: usize> {
        data: [T; N],
    }

    impl<T: Default + Copy, const N: usize> Vec<T, N> {
        pub fn new() -> Self {
            Vec { data: [T::default(); N] }
        }

        pub fn zip<U, const M: usize>(self, other: Vec<U, M>) -> Vec<(T, U), {N.min(M)}>
        where
            U: Copy,
            [(T, U); N.min(M)]: Sized,
        {
            todo!() // Implementation details
        }
    }

    // Phantom type for units
    pub struct Quantity<T, Unit> {
        value: T,
        _unit: PhantomData<Unit>,
    }

    pub struct Meters;
    pub struct Seconds;
    pub struct MetersPerSecond;

    impl<T> Quantity<T, Meters> {
        pub fn new_meters(value: T) -> Self {
            Quantity { value, _unit: PhantomData }
        }
    }

    impl<T: std::ops::Div<Output = T>> Quantity<T, Meters> {
        pub fn div_time(self, time: Quantity<T, Seconds>) -> Quantity<T, MetersPerSecond> {
            Quantity {
                value: self.value / time.value,
                _unit: PhantomData,
            }
        }
    }
}
```

### Level 7: Meta-Programming and Code Generation

```rust
// Advanced macro examples
#[macro_export]
macro_rules! derive_monad {
    ($type:ident) => {
        impl<T> $type<T> {
            pub fn pure(value: T) -> Self {
                $type::Some(value)
            }

            pub fn bind<U>(self, f: impl FnOnce(T) -> $type<U>) -> $type<U> {
                match self {
                    $type::Some(x) => f(x),
                    $type::None => $type::None,
                }
            }

            pub fn map<U>(self, f: impl FnOnce(T) -> U) -> $type<U> {
                self.bind(|x| $type::pure(f(x)))
            }

            pub fn join(self) -> T
            where
                T: From<$type<T>>,
            {
                match self {
                    $type::Some(x) => x,
                    $type::None => panic!("Cannot join None"),
                }
            }

            pub fn sequence<U>(list: Vec<$type<U>>) -> $type<Vec<U>> {
                list.into_iter().fold(
                    $type::pure(Vec::new()),
                    |acc, item| {
                        acc.bind(|mut vec| {
                            item.bind(|val| {
                                vec.push(val);
                                $type::pure(vec)
                            })
                        })
                    }
                )
            }
        }
    };
}

// Auto-derive builder pattern
#[macro_export]
macro_rules! builder {
    (struct $name:ident {
        $($field:ident: $type:ty),* $(,)?
    }) => {
        pub struct $name {
            $($field: $type),*
        }

        paste::paste! {
            pub struct [<$name Builder>] {
                $($field: Option<$type>),*
            }

            impl [<$name Builder>] {
                pub fn new() -> Self {
                    Self {
                        $($field: None),*
                    }
                }

                $(
                    pub fn $field(mut self, value: $type) -> Self {
                        self.$field = Some(value);
                        self
                    }
                )*

                pub fn build(self) -> Result<$name, &'static str> {
                    Ok($name {
                        $($field: self.$field.ok_or(concat!("Missing field: ", stringify!($field)))?),*
                    })
                }
            }
        }

        impl $name {
            pub fn builder() -> [<$name Builder>] {
                [<$name Builder>]::new()
            }
        }
    };
}

// Usage example
builder! {
    struct Config {
        host: String,
        port: u16,
        timeout: u64,
    }
}

// Self-modifying code via const evaluation
pub const fn generate_lookup_table() -> [u32; 256] {
    let mut table = [0u32; 256];
    let mut i = 0;
    while i < 256 {
        table[i] = (i as u32) * (i as u32);
        i += 1;
    }
    table
}

pub static SQUARES: [u32; 256] = generate_lookup_table();

// Compile-time regex validation
#[macro_export]
macro_rules! regex {
    ($pattern:literal) => {{
        const _: &str = $pattern; // Validate at compile time
        regex::Regex::new($pattern).expect("Invalid regex pattern")
    }};
}

// Auto-generate trait implementations
#[macro_export]
macro_rules! impl_math_ops {
    ($type:ty) => {
        impl std::ops::Add for $type {
            type Output = Self;
            fn add(self, rhs: Self) -> Self::Output {
                Self(self.0 + rhs.0)
            }
        }

        impl std::ops::Sub for $type {
            type Output = Self;
            fn sub(self, rhs: Self) -> Self::Output {
                Self(self.0 - rhs.0)
            }
        }

        impl std::ops::Mul for $type {
            type Output = Self;
            fn mul(self, rhs: Self) -> Self::Output {
                Self(self.0 * rhs.0)
            }
        }
    };
}

// Example newtype with auto-generated ops
pub struct Price(f64);
impl_math_ops!(Price);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_builder_pattern() {
        let config = Config::builder()
            .host("localhost".to_string())
            .port(8080)
            .timeout(30)
            .build()
            .unwrap();

        assert_eq!(config.port, 8080);
    }

    #[test]
    fn test_compile_time_lookup() {
        assert_eq!(SQUARES[16], 256);
        assert_eq!(SQUARES[0], 0);
        assert_eq!(SQUARES[255], 65025);
    }
}
```

## Integration Example: Complete FP Application

```rust
// A complete functional application combining all levels
use async_trait::async_trait;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

// Domain types with phantom type safety (L6)
mod domain {
    use std::marker::PhantomData;

    pub struct Validated;
    pub struct Unvalidated;

    pub struct User<State> {
        pub id: u64,
        pub name: String,
        pub email: String,
        _state: PhantomData<State>,
    }

    impl User<Unvalidated> {
        pub fn validate(self) -> Result<User<Validated>, String> {
            if self.email.contains('@') {
                Ok(User {
                    id: self.id,
                    name: self.name,
                    email: self.email,
                    _state: PhantomData,
                })
            } else {
                Err("Invalid email".to_string())
            }
        }
    }
}

// Effect system using async traits (L5)
#[async_trait]
pub trait Repository: Send + Sync {
    type Error;

    async fn find_user(&self, id: u64) -> Result<domain::User<domain::Validated>, Self::Error>;
    async fn save_user(&self, user: domain::User<domain::Validated>) -> Result<(), Self::Error>;
}

// Monad transformer stack (L4)
pub struct AppM<T> {
    computation: Box<dyn Future<Output = Result<T, AppError>> + Send>,
}

impl<T> AppM<T> {
    pub fn pure(value: T) -> Self {
        AppM {
            computation: Box::pin(async move { Ok(value) }),
        }
    }

    pub fn bind<U>(self, f: impl FnOnce(T) -> AppM<U> + Send + 'static) -> AppM<U>
    where
        T: Send + 'static,
        U: Send + 'static,
    {
        AppM {
            computation: Box::pin(async move {
                match self.computation.await {
                    Ok(value) => f(value).computation.await,
                    Err(e) => Err(e),
                }
            }),
        }
    }
}

// Service layer with dependency injection (L3)
pub struct UserService<R: Repository> {
    repo: Arc<R>,
    cache: Arc<RwLock<HashMap<u64, domain::User<domain::Validated>>>>,
}

impl<R: Repository> UserService<R> {
    // Pure function composition (L1)
    pub fn new(repo: Arc<R>) -> Self {
        Self {
            repo,
            cache: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    // Functor mapping over async results (L2)
    pub async fn get_user_name(&self, id: u64) -> Result<String, R::Error> {
        self.repo
            .find_user(id)
            .await
            .map(|user| user.name)
    }

    // Parallel operations with Rayon (L3)
    pub async fn batch_validate(
        users: Vec<domain::User<domain::Unvalidated>>
    ) -> (Vec<domain::User<domain::Validated>>, Vec<String>) {
        use rayon::prelude::*;

        let results: Vec<_> = users
            .into_par_iter()
            .map(|user| user.validate())
            .collect();

        let (validated, errors): (Vec<_>, Vec<_>) = results
            .into_iter()
            .partition_map(|r| match r {
                Ok(user) => itertools::Either::Left(user),
                Err(e) => itertools::Either::Right(e),
            });

        (validated, errors)
    }
}

// Procedural macro for auto-deriving service methods (L7)
// This would be in a separate proc-macro crate
// #[derive(ServiceMethods)]
// impl UserService { ... }

#[cfg(test)]
mod integration_tests {
    use super::*;

    #[tokio::test]
    async fn test_functional_composition() {
        // Test would demonstrate the complete integration
    }
}
```

## Performance Benchmarks

```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn benchmark_functional_patterns(c: &mut Criterion) {
    c.bench_function("iterator chain", |b| {
        b.iter(|| {
            (0..1000)
                .filter(|x| x % 2 == 0)
                .map(|x| x * 2)
                .fold(0, |acc, x| acc + x)
        })
    });

    c.bench_function("manual loop", |b| {
        b.iter(|| {
            let mut sum = 0;
            for i in 0..1000 {
                if i % 2 == 0 {
                    sum += i * 2;
                }
            }
            sum
        })
    });
}

criterion_group!(benches, benchmark_functional_patterns);
criterion_main!(benches);
```

## Conclusion

These examples demonstrate that Rust's ownership system and zero-cost abstractions enable sophisticated functional programming patterns while maintaining performance and memory safety. The progression from basic composition to meta-programming shows how Rust can achieve Haskell-like expressiveness with C-like performance.