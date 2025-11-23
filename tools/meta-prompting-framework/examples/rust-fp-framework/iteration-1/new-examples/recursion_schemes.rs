// Advanced Recursion Schemes in Rust

use std::rc::Rc;
use std::marker::PhantomData;

// Base functor trait
trait Functor {
    type F<T>;
    fn fmap<A, B>(fa: Self::F<A>, f: impl FnOnce(A) -> B) -> Self::F<B>;
}

// Fix point for recursive types
#[derive(Clone)]
struct Fix<F: Functor>(Rc<F::F<Fix<F>>>);

impl<F: Functor> Fix<F> {
    fn new(f: F::F<Fix<F>>) -> Self {
        Fix(Rc::new(f))
    }

    fn unfix(&self) -> &F::F<Fix<F>> {
        &self.0
    }
}

// Either type for apomorphisms
enum Either<L, R> {
    Left(L),
    Right(R),
}

// List functor
#[derive(Clone)]
enum ListF<A, R> {
    Nil,
    Cons(A, R),
}

struct ListFunctor<A>(PhantomData<A>);

impl<A: Clone> Functor for ListFunctor<A> {
    type F<T> = ListF<A, T>;

    fn fmap<B, C>(fa: ListF<A, B>, f: impl FnOnce(B) -> C) -> ListF<A, C> {
        match fa {
            ListF::Nil => ListF::Nil,
            ListF::Cons(a, b) => ListF::Cons(a, f(b)),
        }
    }
}

// Tree functor
#[derive(Clone)]
enum TreeF<A, R> {
    Leaf(A),
    Node(R, R),
}

struct TreeFunctor<A>(PhantomData<A>);

impl<A: Clone> Functor for TreeFunctor<A> {
    type F<T> = TreeF<A, T>;

    fn fmap<B, C>(fa: TreeF<A, B>, f: impl FnOnce(B) -> C) -> TreeF<A, C> {
        match fa {
            TreeF::Leaf(a) => TreeF::Leaf(a),
            TreeF::Node(l, r) => TreeF::Node(f(l), f(r)),
        }
    }
}

// =============================================================================
// CATAMORPHISM (fold)
// =============================================================================

fn cata<F: Functor, A>(
    fix: &Fix<F>,
    alg: impl Fn(&F::F<A>) -> A + Clone,
) -> A
where
    F::F<A>: Clone,
{
    fn cata_helper<F: Functor, A>(
        fix: &Fix<F>,
        alg: &dyn Fn(&F::F<A>) -> A,
    ) -> A
    where
        F::F<A>: Clone,
    {
        let base = fix.unfix();
        let mapped = F::fmap(base.clone(), |f| cata_helper(&f, alg));
        alg(&mapped)
    }
    cata_helper(fix, &alg)
}

// Example: Sum a list
fn sum_list(list: &Fix<ListFunctor<i32>>) -> i32 {
    cata(list, |lst| match lst {
        ListF::Nil => 0,
        ListF::Cons(x, sum) => x + sum,
    })
}

// =============================================================================
// ANAMORPHISM (unfold)
// =============================================================================

fn ana<F: Functor, A: Clone>(
    seed: A,
    coalg: impl Fn(A) -> F::F<A> + Clone,
) -> Fix<F> {
    let base = coalg(seed.clone());
    let mapped = F::fmap(base, |a| ana(a, coalg.clone()));
    Fix::new(mapped)
}

// Example: Generate range as list
fn range(start: i32, end: i32) -> Fix<ListFunctor<i32>> {
    ana((start, end), |(s, e)| {
        if s >= e {
            ListF::Nil
        } else {
            ListF::Cons(s, (s + 1, e))
        }
    })
}

// =============================================================================
// PARAMORPHISM (fold with access to substructure)
// =============================================================================

fn para<F: Functor, A>(
    fix: &Fix<F>,
    alg: impl Fn(&F::F<(Fix<F>, A)>) -> A + Clone,
) -> A
where
    F::F<(Fix<F>, A)>: Clone,
{
    fn para_helper<F: Functor, A>(
        fix: &Fix<F>,
        alg: &dyn Fn(&F::F<(Fix<F>, A)>) -> A,
    ) -> (Fix<F>, A)
    where
        F::F<(Fix<F>, A)>: Clone,
    {
        let base = fix.unfix();
        let mapped = F::fmap(base.clone(), |f| para_helper(&f, alg));
        let result = alg(&mapped);
        (fix.clone(), result)
    }
    para_helper(fix, &alg).1
}

// Example: Safe tail function using paramorphism
fn safe_tail(list: &Fix<ListFunctor<i32>>) -> Option<Fix<ListFunctor<i32>>> {
    para(list, |lst| match lst {
        ListF::Nil => None,
        ListF::Cons(_, (sublist, _)) => {
            // We have access to the original sublist!
            Some(sublist.clone())
        }
    })
}

// Example: Factorial with paramorphism (access to original number)
fn factorial_para(n: u32) -> u32 {
    let nat_list = ana(n, |x| {
        if x == 0 {
            ListF::Nil
        } else {
            ListF::Cons(x, x - 1)
        }
    });

    para(&nat_list, |lst| match lst {
        ListF::Nil => 1,
        ListF::Cons(x, (_, factorial)) => x * factorial,
    })
}

// =============================================================================
// APOMORPHISM (unfold with early termination)
// =============================================================================

fn apo<F: Functor, A: Clone>(
    seed: A,
    coalg: impl Fn(A) -> F::F<Either<Fix<F>, A>> + Clone,
) -> Fix<F> {
    let base = coalg(seed);
    let mapped = F::fmap(base, |either| match either {
        Either::Left(fix) => fix,
        Either::Right(a) => apo(a, coalg.clone()),
    });
    Fix::new(mapped)
}

// Example: Insert into sorted list with early termination
fn insert_sorted(x: i32, list: &Fix<ListFunctor<i32>>) -> Fix<ListFunctor<i32>> {
    apo((Some(x), list.clone()), |(maybe_x, lst)| {
        match (maybe_x, lst.unfix()) {
            (None, lst) => {
                // Already inserted, just copy rest
                F::fmap(lst.clone(), |r| Either::Left(r))
            }
            (Some(x), ListF::Nil) => {
                // End of list, insert here
                ListF::Cons(x, Either::Left(Fix::new(ListF::Nil)))
            }
            (Some(x), ListF::Cons(y, rest)) if x <= *y => {
                // Found insertion point
                ListF::Cons(x, Either::Right((Some(*y), rest.clone())))
            }
            (Some(x), ListF::Cons(y, rest)) => {
                // Keep looking
                ListF::Cons(*y, Either::Right((Some(x), rest.clone())))
            }
        }
    })
}

// =============================================================================
// HISTOMORPHISM (fold with access to computation history)
// =============================================================================

#[derive(Clone)]
struct Cofree<F: Functor, A> {
    head: A,
    tail: F::F<Box<Cofree<F, A>>>,
}

fn histo<F: Functor, A: Clone>(
    fix: &Fix<F>,
    alg: impl Fn(&F::F<Cofree<F, A>>) -> A + Clone,
) -> A
where
    F::F<Cofree<F, A>>: Clone,
    F::F<Box<Cofree<F, A>>>: Clone,
{
    fn build_cofree<F: Functor, A: Clone>(
        fix: &Fix<F>,
        alg: &dyn Fn(&F::F<Cofree<F, A>>) -> A,
    ) -> Cofree<F, A>
    where
        F::F<Cofree<F, A>>: Clone,
        F::F<Box<Cofree<F, A>>>: Clone,
    {
        let base = fix.unfix();
        let mapped_box = F::fmap(base.clone(), |f| Box::new(build_cofree(&f, alg)));

        // Convert Box<Cofree> to Cofree for alg
        let mapped_cofree = unsafe {
            // This is a simplification; proper implementation would avoid unsafe
            std::mem::transmute_copy::<F::F<Box<Cofree<F, A>>>, F::F<Cofree<F, A>>>(&mapped_box)
        };

        let head = alg(&mapped_cofree);
        Cofree { head, tail: mapped_box }
    }
    build_cofree(fix, &alg).head
}

// Example: Fibonacci with histomorphism (efficient dynamic programming)
fn fibonacci_histo(n: u32) -> u64 {
    let nat_list = ana(n, |x| {
        if x == 0 {
            ListF::Nil
        } else {
            ListF::Cons((), x - 1)
        }
    });

    histo(&nat_list, |lst| match lst {
        ListF::Nil => 0,
        ListF::Cons((), cofree) => {
            match &cofree.tail {
                ListF::Nil => 1,
                ListF::Cons((), inner) => {
                    // We have access to both fib(n-1) and fib(n-2)!
                    cofree.head + inner.head
                }
            }
        }
    })
}

// =============================================================================
// ZYGOMORPHISM (mutually recursive fold)
// =============================================================================

fn zygo<F: Functor, A: Clone, B>(
    fix: &Fix<F>,
    alg_a: impl Fn(&F::F<A>) -> A + Clone,
    alg_b: impl Fn(&F::F<(A, B)>) -> B + Clone,
) -> B
where
    F::F<A>: Clone,
    F::F<(A, B)>: Clone,
{
    fn zygo_helper<F: Functor, A: Clone, B>(
        fix: &Fix<F>,
        alg_a: &dyn Fn(&F::F<A>) -> A,
        alg_b: &dyn Fn(&F::F<(A, B)>) -> B,
    ) -> (A, B)
    where
        F::F<A>: Clone,
        F::F<(A, B)>: Clone,
    {
        let base = fix.unfix();
        let mapped = F::fmap(base.clone(), |f| zygo_helper(&f, alg_a, alg_b));

        // Compute A value
        let mapped_a = unsafe {
            // Simplification: project first component
            std::mem::transmute_copy::<F::F<(A, B)>, F::F<A>>(&mapped)
        };
        let a = alg_a(&mapped_a);

        // Compute B value using both A and B
        let b = alg_b(&mapped);

        (a, b)
    }
    zygo_helper(fix, &alg_a, &alg_b).1
}

// Example: Count nodes and sum values simultaneously
fn count_and_sum(tree: &Fix<TreeFunctor<i32>>) -> (usize, i32) {
    let count = zygo(
        tree,
        // Count nodes
        |t| match t {
            TreeF::Leaf(_) => 1,
            TreeF::Node(l, r) => l + r + 1,
        },
        // Sum values while having access to counts
        |t| match t {
            TreeF::Leaf(x) => (*x, 1),
            TreeF::Node((sum_l, count_l), (sum_r, count_r)) => {
                (sum_l + sum_r, count_l + count_r)
            }
        },
    );
    count
}

// =============================================================================
// DYNAMORPHISM (generalized hylomorphism)
// =============================================================================

fn dyna<F: Functor, A: Clone, B>(
    seed: A,
    coalg: impl Fn(A) -> F::F<A> + Clone,
    alg: impl Fn(&F::F<Cofree<F, B>>) -> B + Clone,
) -> B
where
    F::F<Cofree<F, B>>: Clone,
    F::F<Box<Cofree<F, B>>>: Clone,
{
    // First unfold, then fold with history
    let unfolded = ana(seed, coalg);
    histo(&unfolded, alg)
}

// Example: Efficient change-making algorithm
fn make_change(amount: u32, coins: Vec<u32>) -> u32 {
    dyna(
        amount,
        |amt| {
            if amt == 0 {
                ListF::Nil
            } else {
                ListF::Cons(amt, amt - 1)
            }
        },
        |lst| match lst {
            ListF::Nil => 0,
            ListF::Cons(amt, history) => {
                coins.iter()
                    .filter(|&&coin| coin <= *amt)
                    .map(|&coin| {
                        if *amt == coin {
                            1
                        } else {
                            // Access memoized subproblem solutions
                            1 + history.head
                        }
                    })
                    .min()
                    .unwrap_or(u32::MAX)
            }
        },
    )
}

// =============================================================================
// FUTUMORPHISM (fold with access to future computations)
// =============================================================================

#[derive(Clone)]
struct Free<F: Functor, A> {
    inner: FreeInner<F, A>,
}

#[derive(Clone)]
enum FreeInner<F: Functor, A> {
    Pure(A),
    Free(F::F<Box<Free<F, A>>>),
}

fn futu<F: Functor, A: Clone>(
    fix: &Fix<F>,
    alg: impl Fn(&F::F<Free<F, A>>) -> A + Clone,
) -> A
where
    F::F<Free<F, A>>: Clone,
{
    // Futumorphism: dual of histomorphism
    // Allows "looking ahead" in the computation
    unimplemented!("Futumorphism requires more complex implementation")
}

// =============================================================================
// Main and tests
// =============================================================================

fn main() {
    println!("=== Recursion Schemes Examples ===\n");

    // Create a list: [1, 2, 3]
    let list = Fix::new(ListF::Cons(1,
        Fix::new(ListF::Cons(2,
            Fix::new(ListF::Cons(3,
                Fix::new(ListF::Nil)))))));

    println!("List sum (catamorphism): {}", sum_list(&list));

    println!("Range 1..5 (anamorphism): {:?}",
        cata(&range(1, 5), |l| match l {
            ListF::Nil => vec![],
            ListF::Cons(x, rest) => {
                let mut v = vec![*x];
                v.extend(rest);
                v
            }
        }));

    println!("Factorial of 5 (paramorphism): {}", factorial_para(5));

    println!("Fibonacci of 10 (histomorphism): {}", fibonacci_histo(10));

    // Create a tree
    let tree = Fix::new(TreeF::Node(
        Fix::new(TreeF::Leaf(1)),
        Fix::new(TreeF::Node(
            Fix::new(TreeF::Leaf(2)),
            Fix::new(TreeF::Leaf(3))
        ))
    ));

    let (sum, count) = count_and_sum(&tree);
    println!("Tree sum and count (zygomorphism): sum={}, count={}", sum, count);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cata_sum() {
        let list = Fix::new(ListF::Cons(1,
            Fix::new(ListF::Cons(2,
                Fix::new(ListF::Cons(3,
                    Fix::new(ListF::Nil)))))));
        assert_eq!(sum_list(&list), 6);
    }

    #[test]
    fn test_ana_range() {
        let list = range(1, 4);
        let vec = cata(&list, |l| match l {
            ListF::Nil => vec![],
            ListF::Cons(x, rest) => {
                let mut v = vec![*x];
                v.extend(rest);
                v
            }
        });
        assert_eq!(vec, vec![1, 2, 3]);
    }

    #[test]
    fn test_para_factorial() {
        assert_eq!(factorial_para(5), 120);
        assert_eq!(factorial_para(0), 1);
    }

    #[test]
    fn test_histo_fibonacci() {
        assert_eq!(fibonacci_histo(0), 0);
        assert_eq!(fibonacci_histo(1), 1);
        assert_eq!(fibonacci_histo(10), 55);
    }
}