# owned_lock
## Rust-like synchronization primitives in Python.

## Index

 - [Brief](#Brief)
 - [Examples](#Example)
 - [References](#References)

## Brief

Synchronization primitives that [own](#what-is-ownership) the data they lock.

In Python data and locks are always adjacent, that is to say this is commonly done:

```py
data = make_important_data()
data_lock = threading.Lock()
print(f"Data {data!r}")  # <__main__.object object @ 0xDEADBEEF> 
```

In Rust the concept of ownership & borrowing is heavily present in every block
you write, so when dealing with a mutex lock (like threading.Lock) you see this:

```rust
let data = make_important_data();
let data_lock = Mutex::new(data);
printlnt!("Data: {:?}", data);  // Compiler error: use after `move`.
```

Since the lock in Rust-land takes ownership of the original data, you must ask
the mutex if you want to interact with the data:

```rust
{
    let data = data_lock.lock();
    println!("Data: {:?}", *data) // Yay we can now use data!
}
```

Where in Python, no such guarentees are made. If you have a lock that protects
access for some data that's just about as effective as a comment on a global
variable in C.

For instance, given the following code:

```py
mapping = {}
mapping_lock = Lock()

def runs_in_thread_a():
    while True:
        with mapping_lock:
            key = randint()
            mapping[key] = str(key)

def runs_in_thread_b():
    with mapping_lock:
        previous = set(mapping.keys())

    while True:
        with mapping_lock:
            diff = set(mapping.keys()).difference(previous)

            if diff:
                print(f"New key(s)! {diff!r}")
```

Given a new third party or contributor that needs to work with the `mapping`.
You best pray they notice `mapping_lock` exists or is documented somewhere else
they're gonna go ahed and perform some unsafe access to access the data.

### TLDR;

#### For Rustaceans

Think of this package as the pure Python version of [Mutex](#rustdoc-mutex)<[RefCell](#rustdoc-refcell)<T>>

#### For Pythonistas

A lock [like any other](#pydoc-threading-Lock) that forces its users to ensure
that the data being locked isn't referenced anywhere else (leaking) leading to,
as a consequence of, the requirement that you must always use lock in order to
access the data (enforced protected access).

## Examples

All the follwing examples will make use of this function to represet crittical state:

```py
def make_important_data() -> object:
    """Some very serious stuff happens here"""
    return object()
```

### Straightforward demo

```py
from owned_lock import Mutex

critical_state = Mutex(make_important_data())

with critical_state.lock() as data:
    print(f"Critical work!!! {data!r}")
```

### Ownership rules at work

### Without exception handling

```py
from owned_lock import Mutex

accessable_from_elsewhere = elsewhere = make_important_data()

locked_state = Mutex(accessable_from_elsewhere)  # Exception! "owned_lock.LeakyReference"
```

### With exception handling

```py
import sys

from owned_lock import Mutex, LeakyReference

accessable_from_elsewhere = elsewhere = make_important_data()

try:
    locked_state = Mutex(accessable_from_elsewhere)
except LeakyReference:
    print(f"It works! {locked_state!r}")
else:
    sys.exit("What happened to the ownership rules?!")
```

## References

###### what-is-ownership

 - https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html

###### rustdoc-refcell

 - https://doc.rust-lang.org/std/cell/struct.RefCell.html

###### rustdoc-mutex

 - https://doc.rust-lang.org/std/sync/struct.Mutex.html

###### pydoc-threading-Lock

 - https://docs.python.org/3/library/threading.html#threading.Lock
