// Comonadic patterns in Rust

use std::rc::Rc;

// Base Comonad trait
trait Comonad: Sized {
    type Item;
    type Wrapped<T>;

    fn extract(&self) -> Self::Item;
    fn duplicate(&self) -> Self::Wrapped<Self>;
    fn extend<B, F>(&self, f: F) -> Self::Wrapped<B>
    where
        F: Fn(&Self) -> B;
}

// Store Comonad: Position-indexed computation
#[derive(Clone)]
struct Store<S: Clone, A> {
    lookup: Rc<dyn Fn(S) -> A>,
    position: S,
}

impl<S: Clone, A: Clone> Store<S, A> {
    fn new<F>(position: S, lookup: F) -> Self
    where
        F: Fn(S) -> A + 'static,
    {
        Store {
            lookup: Rc::new(lookup),
            position,
        }
    }

    fn seek(&self, new_position: S) -> Self {
        Store {
            lookup: self.lookup.clone(),
            position: new_position,
        }
    }

    fn experiment<B>(&self, f: impl Fn(S) -> B) -> B {
        f(self.position.clone())
    }
}

impl<S: Clone, A: Clone> Comonad for Store<S, A> {
    type Item = A;
    type Wrapped<T> = Store<S, T>;

    fn extract(&self) -> A {
        (self.lookup)(self.position.clone())
    }

    fn duplicate(&self) -> Store<S, Store<S, A>> {
        let lookup_clone = self.lookup.clone();
        Store {
            lookup: Rc::new(move |s| Store {
                lookup: lookup_clone.clone(),
                position: s,
            }),
            position: self.position.clone(),
        }
    }

    fn extend<B, F>(&self, f: F) -> Store<S, B>
    where
        F: Fn(&Store<S, A>) -> B + 'static,
    {
        let lookup_clone = self.lookup.clone();
        Store {
            lookup: Rc::new(move |s| {
                let store = Store {
                    lookup: lookup_clone.clone(),
                    position: s,
                };
                f(&store)
            }),
            position: self.position.clone(),
        }
    }
}

// Conway's Game of Life using Store Comonad
type Grid<T> = Store<(i32, i32), T>;

fn neighbors(pos: (i32, i32)) -> Vec<(i32, i32)> {
    let (x, y) = pos;
    vec![
        (x-1, y-1), (x, y-1), (x+1, y-1),
        (x-1, y),             (x+1, y),
        (x-1, y+1), (x, y+1), (x+1, y+1),
    ]
}

fn conway_rule(grid: &Grid<bool>) -> bool {
    let alive = grid.extract();
    let alive_neighbors = neighbors(grid.position.clone())
        .into_iter()
        .filter(|&pos| grid.seek(pos).extract())
        .count();

    matches!((alive, alive_neighbors), (true, 2..=3) | (false, 3))
}

fn game_of_life_step(grid: Grid<bool>) -> Grid<bool> {
    grid.extend(conway_rule)
}

// Example: 2D grid computations
fn grid_example() {
    let initial_grid = Store::new(
        (0, 0),
        |pos: (i32, i32)| {
            // Glider pattern
            matches!(pos, (0, 1) | (1, 2) | (2, 0) | (2, 1) | (2, 2))
        }
    );

    let next_gen = game_of_life_step(initial_grid);

    // Check cell at position (1, 1)
    let cell_1_1 = next_gen.seek((1, 1)).extract();
    println!("Cell (1, 1) after one generation: {}", cell_1_1);
}

// Env Comonad: Dependency injection
#[derive(Clone)]
struct Env<E: Clone, A> {
    env: E,
    value: A,
}

impl<E: Clone, A: Clone> Comonad for Env<E, A> {
    type Item = A;
    type Wrapped<T> = Env<E, T>;

    fn extract(&self) -> A {
        self.value.clone()
    }

    fn duplicate(&self) -> Env<E, Env<E, A>> {
        Env {
            env: self.env.clone(),
            value: self.clone(),
        }
    }

    fn extend<B, F>(&self, f: F) -> Env<E, B>
    where
        F: Fn(&Env<E, A>) -> B,
    {
        Env {
            env: self.env.clone(),
            value: f(self),
        }
    }
}

// Dependency injection example
#[derive(Clone)]
struct Config {
    debug: bool,
    max_retries: usize,
}

fn process_with_config(env: &Env<Config, String>) -> String {
    let config = &env.env;
    let data = &env.value;

    if config.debug {
        format!("DEBUG: Processing '{}' with {} retries", data, config.max_retries)
    } else {
        format!("Processing '{}'", data)
    }
}

fn env_example() {
    let config = Config {
        debug: true,
        max_retries: 3,
    };

    let env = Env {
        env: config,
        value: "Hello, World!".to_string(),
    };

    let result = env.extend(process_with_config);
    println!("Result: {}", result.extract());
}

// Traced Comonad: Computation history
struct Traced<M, A> {
    run: Rc<dyn Fn(M) -> A>,
}

trait Monoid: Clone {
    fn mempty() -> Self;
    fn mappend(&self, other: &Self) -> Self;
}

impl Monoid for String {
    fn mempty() -> Self {
        String::new()
    }

    fn mappend(&self, other: &Self) -> Self {
        format!("{}{}", self, other)
    }
}

impl<M: Monoid, A: Clone + 'static> Comonad for Traced<M, A> {
    type Item = A;
    type Wrapped<T> = Traced<M, T>;

    fn extract(&self) -> A {
        (self.run)(M::mempty())
    }

    fn duplicate(&self) -> Traced<M, Traced<M, A>> {
        let run_clone = self.run.clone();
        Traced {
            run: Rc::new(move |m1: M| {
                let run_inner = run_clone.clone();
                Traced {
                    run: Rc::new(move |m2: M| {
                        (run_inner)(m1.mappend(&m2))
                    }),
                }
            }),
        }
    }

    fn extend<B, F>(&self, f: F) -> Traced<M, B>
    where
        F: Fn(&Traced<M, A>) -> B + 'static,
    {
        let run_clone = self.run.clone();
        Traced {
            run: Rc::new(move |m: M| {
                let traced = Traced {
                    run: Rc::new({
                        let run_inner = run_clone.clone();
                        let m_clone = m.clone();
                        move |m2: M| (run_inner)(m_clone.mappend(&m2))
                    }),
                };
                f(&traced)
            }),
        }
    }
}

// Logging with Traced
fn traced_computation() {
    let traced: Traced<String, usize> = Traced {
        run: Rc::new(|log: String| {
            println!("Log: {}", log);
            log.len()
        }),
    };

    let extended = traced.extend(|t| {
        let length = t.extract();
        length * 2
    });

    println!("Result: {}", extended.extract());
}

// Cofree Comonad: Annotated recursive structures
struct Cofree<F, A> {
    head: A,
    tail: Box<F>,
}

impl<F, A: Clone> Cofree<F, A> {
    fn annotate<B>(self, f: impl Fn(&A) -> B) -> Cofree<F, B> {
        Cofree {
            head: f(&self.head),
            tail: self.tail,
        }
    }
}

// Example: Annotating a tree with depth information
enum TreeF<R> {
    Leaf,
    Node(R, R),
}

type AnnotatedTree<A> = Cofree<TreeF<Box<AnnotatedTree<A>>>, A>;

fn annotate_with_depth(tree: TreeF<()>) -> AnnotatedTree<usize> {
    fn go(tree: TreeF<()>, depth: usize) -> AnnotatedTree<usize> {
        match tree {
            TreeF::Leaf => Cofree {
                head: depth,
                tail: Box::new(TreeF::Leaf),
            },
            TreeF::Node(_, _) => Cofree {
                head: depth,
                tail: Box::new(TreeF::Node(
                    Box::new(go(TreeF::Leaf, depth + 1)),
                    Box::new(go(TreeF::Leaf, depth + 1)),
                )),
            },
        }
    }
    go(tree, 0)
}

// Main function demonstrating all comonads
fn main() {
    println!("=== Store Comonad: Game of Life ===");
    grid_example();

    println!("\n=== Env Comonad: Dependency Injection ===");
    env_example();

    println!("\n=== Traced Comonad: Computation History ===");
    traced_computation();

    println!("\n=== Cofree Comonad: Tree Annotation ===");
    let tree = TreeF::Node((), ());
    let annotated = annotate_with_depth(tree);
    println!("Root depth: {}", annotated.head);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_store_laws() {
        let store = Store::new((0, 0), |(x, y)| x + y);

        // Left identity: extend extract = id
        let extended = store.extend(|s| s.extract());
        assert_eq!(extended.extract(), store.extract());

        // Right identity: extract . duplicate = id
        let duplicated = store.duplicate();
        assert_eq!(duplicated.extract().extract(), store.extract());
    }

    #[test]
    fn test_env_laws() {
        let env = Env {
            env: 42,
            value: "test".to_string(),
        };

        // Associativity of extend
        let f = |e: &Env<i32, String>| e.value.len();
        let g = |n: &Env<i32, usize>| n.extract() * 2;

        let left = env.extend(f).extend(g);
        let right = env.extend(|e| g(&e.extend(f)));

        assert_eq!(left.extract(), right.extract());
    }
}