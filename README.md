# owned_lock
## Rust-like synchronization primitives in Python.

## Index

 - [Brief](#Brief)
 - [Examples](#Example)
 - [References](#References)

## Brief

Synchronization primitives that [own](#what-is-ownership) the data they lock.

I've been using Python for the entirety of my programming career and recently
I've double timed it with Rust for the last two years. Today I absolutely adore
Rusts borrowing and ownership rules and the memory guarentees users stand to
gain from that and as a consequence of those rules I believe that any sync
primitive in Rust is immedietly better because, unless you do some really
unsafe stuff and explicitly drop those promises, **you always have to interact
with the underlying sync mechanism (lock) if you want to use the data it is
responsible for!** This greatly reduces the risk of running up against the well
known villian of mulititasking programming: data races; by forcing the user to
explicitly acknowledge the lock and avoiding unprotected accesses.

### TLDR;

#### For Rustaceans

Think of this package as the pure Python version of [Mutex](#rustdoc-mutex)<[RefCell](rustdoc-refcell)<T>>

#### For Pythonistas

A lock [like any other](pydoc-threading-Lock) that forces its users to ensure
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
