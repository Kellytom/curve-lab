"""The Python twin of reduction/reduce.ts: Chebyshev truncation + 5-grid
quantization, exact in Fraction. The coefficients must be IDENTICAL to the
TypeScript port's - the algorithm is deterministic in exact arithmetic."""
import json, sys, math
from fractions import Fraction
sys.set_int_max_str_digits(200000)
sys.path.insert(0, '.')
from curve_lab.measure import to_fraction, curve_polynomials

def fr(n, d=1):
    from math import gcd
    if hasattr(n, 'numerator'): n, d = n.numerator, n.denominator
    g = gcd(abs(n), abs(d)) or 1
    return (n // g, d // g)
def f_add(a, b): return fr(a[0]*b[1] + b[0]*a[1], a[1]*b[1])
def f_sub(a, b): return fr(a[0]*b[1] - b[0]*a[1], a[1]*b[1])
def f_mul(a, b): return fr(a[0]*b[0], a[1]*b[1])
def f_div(a, b): return fr(a[0]*b[1], a[1]*b[0])
import decimal
def f_num(a):
    decimal.getcontext().prec = 12
    return float(decimal.Decimal(a[0]) / decimal.Decimal(a[1]))
def evaluate(p, x):
    total = (0, 1)
    for c in reversed(p): total = f_add(f_mul(total, x), c)
    return total
def trim(p):
    q = list(p)
    while q and q[-1] == (0, 1): q.pop()
    return q

def scale_and_shift(power, alpha, beta):
    scaled = [f_mul(c, fr(alpha[0]**i, alpha[1]**i)) for i, c in enumerate(power)]
    shifted = list(scaled)
    for k in range(len(shifted) - 1, 0, -1):
        shifted[k-1] = f_add(shifted[k-1], f_mul(shifted[k], beta))
    return trim(shifted)

def power_to_chebyshev(power):
    n = len(power)
    T = [[(1,1)], [(0,1), (1,1)]]
    for i in range(1, n):
        twice = [f_mul(c, (2,1)) for c in T[i]]
        nxt = [(0,1)] * (len(T[i]) + 1)
        for k, c in enumerate(twice):
            if k + 1 < len(nxt): nxt[k+1] = f_add(nxt[k+1], c)
        for k, c in enumerate(T[i-1]):
            if k < len(nxt): nxt[k] = f_sub(nxt[k], c)
        T.append(trim(nxt))
    matrix = []
    for i in range(n):
        row = [(0,1)] * n
        for k, c in enumerate(T[i]):
            if k < n: row[k] = c
        matrix.append(row)
    aug = [row + [(1,1) if k == i else (0,1) for k in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col][0] != 0), None)
        if pivot is None: raise ValueError('singular Chebyshev matrix')
        aug[col], aug[pivot] = aug[pivot], aug[col]
        inv = fr(aug[col][col][1], aug[col][col][0])
        aug[col] = [f_mul(v, inv) for v in aug[col]]
        for r in range(n):
            if r == col or aug[r][col][0] == 0: continue
            factor = aug[r][col]
            aug[r] = [f_sub(v, f_mul(factor, aug[col][k])) for k, v in enumerate(aug[r])]
    inverse = [[aug[i][n + k] for k in range(n)] for i in range(n)]
    cheb = [(0,1)] * n
    for i in range(n):
        for k in range(n):
            cheb[i] = f_add(cheb[i], f_mul(inverse[i][k], power[k]))
    return trim(cheb)

def truncate(cheb, degree, five_power=0):
    tail = (0,1)
    for i in range(degree + 1, len(cheb)):
        tail = f_add(tail, (abs(cheb[i][0]), cheb[i][1]))
    T = [[(1,1)], [(0,1), (1,1)]]
    for i in range(1, degree):
        twice = [f_mul(c, (2,1)) for c in T[i]]
        nxt = [(0,1)] * (len(T[i]) + 1)
        for k, c in enumerate(twice):
            if k + 1 < len(nxt): nxt[k+1] = f_add(nxt[k+1], c)
        for k, c in enumerate(T[i-1]):
            if k < len(nxt): nxt[k] = f_sub(nxt[k], c)
        T.append(trim(nxt))
    power = [(0,1)] * (degree + 1)
    for i, c in enumerate(cheb[:degree + 1]):
        if c[0] == 0: continue
        for k in range(min(len(T[i]), len(power))):
            power[k] = f_add(power[k], f_mul(c, T[i][k]))
    grid = fr(5 ** five_power)
    delta = (0,1)
    quantized = []
    for c in power:
        # exact integer rounding: no floats anywhere near the huge fractions
        q, r = divmod(c[0], c[1])
        if 2 * r >= c[1]: q += 1
        on_grid = (q, grid[1])
        diff = f_sub(on_grid, c)
        delta = f_add(delta, (abs(diff[0]), diff[1]))
        quantized.append(on_grid)
    return {'cheb': cheb, 'coeffs': trim(quantized), 'tailBound': f_add(tail, delta)}

def reduce_at(exact, size, degree, pieces, five_power=0):
    out = []
    for i in range(pieces):
        lo, hi = i / pieces, (i + 1) / pieces
        alpha = fr(int(round((hi - lo) * 5e8)), 1000000000)
        beta = fr(int(round((lo + hi) * 5e8)), 1000000000)
        mapped = scale_and_shift(exact, alpha, beta)
        cheb = power_to_chebyshev(mapped)
        piece = truncate(cheb, degree, five_power)
        out.append({**piece, 'lo': lo, 'hi': hi})
    worst = max(out, key=lambda p: f_num(p['tailBound']))
    return {'pieces': out, 'degree': degree, 'piecesCount': len(out),
            'bound': worst['tailBound'], 'boundShare': f_num(worst['tailBound']) / size,
            'size': size}

def reduce_curve(exact, size, degree=11, dial=0.0005, max_pieces=64):
    pieces = 1
    result = reduce_at(exact, size, degree, pieces, 0)
    while result['boundShare'] > dial and pieces < max_pieces:
        pieces *= 2
        result = reduce_at(exact, size, degree, pieces, 0)
    five_power = 0
    while result['boundShare'] > dial and five_power < 9:
        five_power += 1
        result = reduce_at(exact, size, degree, pieces, five_power)
    return {**result, 'met': result['boundShare'] <= dial, 'five_power': five_power}

if __name__ == '__main__':
    root = __import__('pathlib').Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root))
    from curve_lab.measure import to_fraction, curve_polynomials
    reg = json.load(open(root / 'workbench' / 'curve-registry.json'))
    c = [r for r in reg['curves'] if r['uid'] == 'c-0001'][0]
    u = [to_fraction(v) for v in c['speedX']]
    v = [to_fraction(v) for v in c['speedY']]
    x_poly, y_poly = curve_polynomials(u, v)
    exact = [fr(f.numerator, f.denominator) for f in x_poly]
    result = reduce_curve(exact, 20.0, 11, 0.0005, 64)
    json.dump({'pieces': [{'lo': p['lo'], 'hi': p['hi'],
                           'coeffs': [[q[0], q[1]] for q in p['coeffs']]} for p in result['pieces']]},
              open(root / 'reduction' / 'parity' / 'reduce-reference.json', 'w'), indent=1)
    print('python twin: pieces', result['piecesCount'], '· met', result['met'],
          '· boundShare', f"{result['boundShare']:.2e}")
