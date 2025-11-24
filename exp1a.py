def gcd_basic(a, b):
    r1, r2 = a, b
    print("\nq   r1   r2   r")
    while r2 != 0:
        q = r1 // r2
        r = r1 % r2
        print(q, r1, r2, r)
        r1, r2 = r2, r
    print("GCD =", r1)


def extended_euclid(a, b):
    r1, r2 = a, b
    s1, s2 = 1, 0
    t1, t2 = 0, 1
    print("\nq   r1   r2   r   s1  s2  s   t1  t2  t")
    while r2 != 0:
        q = r1 // r2
        r = r1 % r2
        s = s1 - q * s2
        t = t1 - q * t2

        print(q, r1, r2, r, s1, s2, s, t1, t2, t)

        r1, r2 = r2, r
        s1, s2 = s2, s
        t1, t2 = t2, t

    print("GCD =", r1)
    print("s =", s1, ", t =", t1)


def modular_inverse(a, b):
    r1, r2 = a, b
    s1, s2 = 1, 0
    print("\nq   r1   r2   r   t1  t2  t")
    while r2 != 0:
        q = r1 // r2
        r = r1 % r2
        s = s1 - q * s2

        print(q, r1, r2, r, s1, s2, s)

        r1, r2 = r2, r
        s1, s2 = s2, s

    if r1 != 1:
        print("Modular Inverse does NOT exist")
    else:
        print("Modular Inverse =", s1 % b)


while True:
    print("\n----- MENU -----")
    print("1. Basic Euclidean Algorithm (GCD)")
    print("2. Extended Euclidean Algorithm (GCD, s, t)")
    print("3. Modular Inverse using Euclid")
    print("4. Exit")

    ch = int(input("Enter your choice: "))

    if ch == 4:
        break

    a = int(input("Enter a: "))
    b = int(input("Enter b: "))

    if ch == 1:
        gcd_basic(a, b)
    elif ch == 2:
        extended_euclid(a, b)
    elif ch == 3:
        modular_inverse(a, b)
    else:
        print("Invalid option!")
