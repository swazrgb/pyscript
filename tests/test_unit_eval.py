"""Unit tests for Python interpreter."""

from custom_components.pyscript.const import CONF_ALLOW_ALL_IMPORTS, DOMAIN
from custom_components.pyscript.eval import AstEval
from custom_components.pyscript.function import Function
from custom_components.pyscript.global_ctx import GlobalContext, GlobalContextMgr
from custom_components.pyscript.state import State
from pytest_homeassistant_custom_component.common import MockConfigEntry

evalTests = [
    ["1", 1],
    ["1+1", 2],
    ["1+2*3-2", 5],
    ["1-1", 0],
    ["4/2", 2],
    ["4**2", 16],
    ["4<<2", 16],
    ["16>>2", 4],
    ["18 ^ 2", 16],
    ["16 | 2", 18],
    ["0x37 & 0x6c ", 0x24],
    ["11 // 2", 5],
    ["not True", False],
    ["not False", True],
    ["z = 1+2+3; a = z + 1; a + 3", 10],
    ["z = 1+2+3; a = z + 1; a - 3", 4],
    ["x = 1; -x", -1],
    ["z = 5; +z", 5],
    ["~0xff", -256],
    ["x = 1; x < 2", 1],
    ["x = 1; x <= 1", 1],
    ["x = 1; 0 < x < 2", 1],
    ["x = 1; 2 > x > 0", 1],
    ["x = 1; 2 > x >= 1", 1],
    ["x = 1; 0 < x < 2 < -x", 0],
    ["x = [1,2,3]; del x[1:2]; x", [1, 3]],
    ["x = [1,2,3]; del x[1::]; x", [1]],
    ["1 and 2", 2],
    ["1 and 0", 0],
    ["0 or 1", 1],
    ["0 or 0", 0],
    ["f'{1} {2:02d} {3:.1f}'", "1 02 3.0"],
    [["x = None", "x is None"], True],
    ["None is not None", False],
    ["10 in {5, 9, 10, 20}", True],
    ["10 not in {5, 9, 10, 20}", False],
    ["sym_local + 10", 20],
    ["z = 'foo'; z + 'bar'", "foobar"],
    ["xyz.y = 5; xyz.y = 2 + int(xyz.y); int(xyz.y)", 7],
    ["xyz.y = 'bar'; xyz.y += '2'; xyz.y", "bar2"],
    ["z = 'abcd'; z.find('c')", 2],
    ["'abcd'.upper().lower().upper()", "ABCD"],
    ["len('abcd')", 4],
    ["6 if 1-1 else 2", 2],
    ["x = 1; x += 3; x", 4],
    ["z = [1,2,3]; [z[1], z[-1]]", [2, 3]],
    ["'{1} {0}'.format('one', 'two')", "two one"],
    ["'%d, %d' % (23, 45)", "23, 45"],
    ["x = [[1,2,3]]; sum(*x)", 6],
    ["args = [1, 5, 10]; {6, *args, 15}", {1, 5, 6, 10, 15}],
    ["args = [1, 5, 10]; [6, *args, 15]", [6, 1, 5, 10, 15]],
    ["kw = {'x': 1, 'y': 5}; {**kw}", {"x": 1, "y": 5}],
    ["kw = {'x': 1, 'y': 5}; kw2 = {'z': 10}; {**kw, **kw2}", {"x": 1, "y": 5, "z": 10}],
    ["[*iter([1, 2, 3])]", [1, 2, 3]],
    ["{*iter([1, 2, 3])}", {1, 2, 3}],
    ["if 1: x = 10\nelse: x = 20\nx", 10],
    ["if 0: x = 10\nelse: x = 20\nx", 20],
    ["i = 0\nwhile i < 5: i += 1\ni", 5],
    ["i = 0\nwhile i < 5: i += 2\ni", 6],
    ["i = 0\nwhile i < 5:\n    i += 1\n    if i == 3: break\n2 * i", 6],
    ["i = 0; k = 10\nwhile i < 5:\n    i += 1\n    if i <= 2: continue\n    k += 1\nk + i", 18],
    ["i = 1; break; i = 1/0", None],
    ["s = 0;\nfor i in range(5):\n    s += i\ns", 10],
    ["s = 0;\nfor i in iter([10,20,30]):\n    s += i\ns", 60],
    ["z = {'foo': 'bar', 'foo2': 12}; z['foo'] = 'bar2'; z", {"foo": "bar2", "foo2": 12}],
    ["z = {'foo': 'bar', 'foo2': 12}; z['foo'] = 'bar2'; z.keys()", {"foo", "foo2"}],
    ["z = {'foo', 'bar', 12}; z", {"foo", "bar", 12}],
    ["x = dict(key1 = 'value1', key2 = 'value2'); x", {"key1": "value1", "key2": "value2"}],
    [
        "x = dict(key1 = 'value1', key2 = 'value2', key3 = 'value3'); del x['key1']; x",
        {"key2": "value2", "key3": "value3"},
    ],
    [
        "x = dict(key1 = 'value1', key2 = 'value2', key3 = 'value3'); del x[['key1', 'key2']]; x",
        {"key3": "value3"},
    ],
    ["z = {'foo', 'bar', 12}; z.remove(12); z.add(20); z", {"foo", "bar", 20}],
    ["z = [0, 1, 2, 3, 4, 5, 6]; z[1:5:2] = [4, 5]; z", [0, 4, 2, 5, 4, 5, 6]],
    ["[0, 1, 2, 3, 4, 5, 6, 7, 8][1:5:2]", [1, 3]],
    ["[0, 1, 2, 3, 4, 5, 6, 7, 8][1:5]", [1, 2, 3, 4]],
    ["[0, 1, 2, 3, 4, 5, 6, 7, 8][1::3]", [1, 4, 7]],
    ["[0, 1, 2, 3, 4, 5, 6, 7, 8][4::]", [4, 5, 6, 7, 8]],
    ["[0, 1, 2, 3, 4, 5, 6, 7, 8][4:]", [4, 5, 6, 7, 8]],
    ["[0, 1, 2, 3, 4, 5, 6, 7, 8][:6:2]", [0, 2, 4]],
    ["[0, 1, 2, 3, 4, 5, 6, 7, 8][:4:]", [0, 1, 2, 3]],
    ["[0, 1, 2, 3, 4, 5, 6, 7, 8][::2]", [0, 2, 4, 6, 8]],
    ["[0, 1, 2, 3, 4, 5, 6, 7, 8][::]", [0, 1, 2, 3, 4, 5, 6, 7, 8]],
    ["z = [0, 1, 2, 3, 4, 5, 6, 7, 8]; z[1:5:2] = [6, 8]; z", [0, 6, 2, 8, 4, 5, 6, 7, 8]],
    ["z = [0, 1, 2, 3, 4, 5, 6, 7, 8]; z[1:5] = [10, 11]; z", [0, 10, 11, 5, 6, 7, 8]],
    ["z = [0, 1, 2, 3, 4, 5, 6, 7, 8]; z[1::3] = [10, 11, 12]; z", [0, 10, 2, 3, 11, 5, 6, 12, 8]],
    ["z = [0, 1, 2, 3, 4, 5, 6, 7, 8]; z[4::] = [10, 11, 12, 13]; z", [0, 1, 2, 3, 10, 11, 12, 13]],
    ["z = [0, 1, 2, 3, 4, 5, 6, 7, 8]; z[4:] = [10, 11, 12, 13, 14]; z", [0, 1, 2, 3, 10, 11, 12, 13, 14]],
    ["z = [0, 1, 2, 3, 4, 5, 6, 7, 8]; z[:6:2] = [10, 11, 12]; z", [10, 1, 11, 3, 12, 5, 6, 7, 8]],
    ["z = [0, 1, 2, 3, 4, 5, 6, 7, 8]; z[:4:] = [10, 11, 12, 13]; z", [10, 11, 12, 13, 4, 5, 6, 7, 8]],
    ["z = [0, 1, 2, 3, 4, 5, 6, 7, 8]; z[::2] = [10, 11, 12, 13, 14]; z", [10, 1, 11, 3, 12, 5, 13, 7, 14]],
    [
        "z = [0, 1, 2, 3, 4, 5, 6, 7, 8]; z[::] = [10, 11, 12, 13, 14, 15, 16, 17]; z",
        [10, 11, 12, 13, 14, 15, 16, 17],
    ],
    ["(x, y) = (1, 2); [x, y]", [1, 2]],
    ["a, b = (x, y) = (1, 2); [a, b, x, y]", [1, 2, 1, 2]],
    ["y = [1,2]; (x, y[0]) = (3, 4); [x, y]", [3, [4, 2]]],
    ["((x, y), (z, t)) = ((1, 2), (3, 4)); [x, y, z, t]", [1, 2, 3, 4]],
    ["z = [1,2,3]; ((x, y), (z[2], t)) = ((1, 2), (20, 4)); [x, y, z, t]", [1, 2, [1, 2, 20], 4]],
    ["a, b, c = [1,2,3]; [a, b, c]", [1, 2, 3]],
    ["a, b, c = iter([1,2,3]); [a, b, c]", [1, 2, 3]],
    ["tuples = [(1, 2), (3, 4), (5, 6)]; a, b = zip(*tuples); [a, b]", [(1, 3, 5), (2, 4, 6)]],
    ["a, *y, w, z = range(3); [a, y, w, z]", [0, [], 1, 2]],
    ["a, *y, w, z = range(4); [a, y, w, z]", [0, [1], 2, 3]],
    ["a, *y, w, z = range(6); [a, y, w, z]", [0, [1, 2, 3], 4, 5]],
    ["x = [0, 1]; i = 0; i, x[i] = 1, 2; [i, x]", [1, [0, 2]]],
    ["d = {'x': 123}; d['x'] += 10; d", {"x": 133}],
    ["d = [20, 30]; d[1] += 10; d", [20, 40]],
    ["func = lambda m=2: 2 * m; [func(), func(3), func(m=4)]", [4, 6, 8]],
    ["y = 5; y = y + (x := 2 * y); [x, y]", [10, 15]],
    ["Foo = type('Foo', (), {'x': 100}); Foo.x = 10; Foo.x", 10],
    ["Foo = type('Foo', (), {'x': 100}); Foo.x += 10; Foo.x", 110],
    ["Foo = [type('Foo', (), {'x': 100})]; Foo[0].x = 10; Foo[0].x", 10],
    ["Foo = [type('Foo', (), {'x': [100, 101]})]; Foo[0].x[1] = 10; Foo[0].x", [100, 10]],
    ["Foo = [type('Foo', (), {'x': [0, [[100, 101]]]})]; Foo[0].x[1][0][1] = 10; Foo[0].x[1]", [[100, 10]]],
    [
        "Foo = [type('Foo', (), {'x': [0, [[100, 101, 102, 103]]]})]; Foo[0].x[1][0][1:2] = [11, 12]; Foo[0].x[1]",
        [[100, 11, 12, 102, 103]],
    ],
    [
        "pyscript.var1 = 1; pyscript.var2 = 2; set(state.names('pyscript'))",
        {"pyscript.var1", "pyscript.var2"},
    ],
    [
        """
state.set("pyscript.var1", 100, attr1=1, attr2=3.5)
chk1 = [pyscript.var1.attr1, pyscript.var1.attr2]
pyscript.var1 += "xyz"
chk2 = [pyscript.var1.attr1, pyscript.var1.attr2]
state.set("pyscript.var1", 200, attr3 = 'abc')
chk3 = [pyscript.var1.attr1, pyscript.var1.attr2, pyscript.var1.attr3]
chk4 = state.get_attr("pyscript.var1")
state.set("pyscript.var1", pyscript.var1, {})
chk5 = state.get_attr("pyscript.var1")
[chk1, chk2, chk3, chk4, chk5]
""",
        [[1, 3.5], [1, 3.5], [1, 3.5, "abc"], {"attr1": 1, "attr2": 3.5, "attr3": "abc"}, {}],
    ],
    ["eval('1+2')", 3],
    ["x = 5; eval('2 * x')", 10],
    ["x = 5; exec('x = 2 * x'); x", 10],
    ["eval('xyz', {'xyz': 10})", 10],
    ["g = {'xyz': 10}; eval('xyz', g, {})", 10],
    ["g = {'xyz': 10}; eval('xyz', {}, g)", 10],
    ["g = {'xyz': 10}; exec('xyz = 20', {}, g); g", {"xyz": 20}],
    ["g = {'xyz': 10}; xyz = 'abc'; exec('xyz = 20', g, {}); [g['xyz'], xyz]", [10, "abc"]],
    ["g = {'xyz': 10}; exec('xyz = 20', {}, g); g", {"xyz": 20}],
    ["x = 18; locals()['x']", 18],
    ["import math; globals()['math'].sqrt(1024)", 32],
    ["import math; exec('xyz = math.floor(5.6)'); xyz", 5],
    ["import random as rand, math as m\n[rand.uniform(10,10), m.sqrt(1024)]", [10, 32]],
    ["import cmath\ncmath.sqrt(complex(3, 4))", 2 + 1j],
    ["from math import sqrt as sqroot\nsqroot(1024)", 32],
    ["from math import sin, cos, sqrt\nsqrt(1024)", 32],
    ["from math import *\nsqrt(1024)", 32],
    ["from math import sin, floor, sqrt; [sqrt(9), floor(10.5)]", [3, 10]],
    ["from math import *; [sqrt(9), floor(10.5)]", [3, 10]],
    ["from math import floor as floor_alt, sqrt as sqrt_alt; [sqrt_alt(9), floor_alt(10.5)]", [3, 10]],
    ["task.executor(sum, range(5))", 10],
    ["task.executor(int, 'ff', base=16)", 255],
    ["[i for i in range(7) if i != 5 if i != 3]", [0, 1, 2, 4, 6]],
    [
        "i = 100; k = 10; [[k * i for i in range(3) for k in range(5)], i, k]",
        [[0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 0, 2, 4, 6, 8], 100, 10],
    ],
    [
        "i = 100; k = 10; [[[k * i for i in range(3)] for k in range(5)], i, k]",
        [[[0, 0, 0], [0, 1, 2], [0, 2, 4], [0, 3, 6], [0, 4, 8]], 100, 10],
    ],
    [
        "i = 100; k = 10; [{k * i for i in range(3) for k in range(5)}, i, k]",
        [{0, 1, 2, 3, 4, 6, 8}, 100, 10],
    ],
    [
        "i = 100; k = 10; [[{k * i for i in range(3)} for k in range(5)], i, k]",
        [[{0}, {0, 1, 2}, {0, 2, 4}, {0, 3, 6}, {0, 4, 8}], 100, 10],
    ],
    ["i = [10]; [[i[0] for i[0] in range(5)], i]", [[0, 1, 2, 3, 4], [4]]],
    ["i = [10]; [{i[0] for i[0] in range(5)}, i]", [{0, 1, 2, 3, 4}, [4]]],
    [
        """
matrix = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
[val for sublist in matrix for val in sublist if val != 8]
""",
        [1, 2, 3, 4, 5, 6, 7, 9],
    ],
    [
        """
matrix = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
[val for sublist in matrix if sublist[0] != 4 for val in sublist if val != 8]
""",
        [1, 2, 3, 6, 7, 9],
    ],
    [
        """
# check short-circuit of nested if
cnt = 0
def no_op(i):
    global cnt
    cnt += 1
    return i
[i for i in range(7) if no_op(i) != 5 if no_op(i) != 3] + [cnt]
""",
        [0, 1, 2, 4, 6, 13],
    ],
    ["{i for i in range(7) if i != 5 if i != 3}", {0, 1, 2, 4, 6}],
    [
        """
matrix = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
{val for sublist in matrix for val in sublist if val != 8}
""",
        {1, 2, 3, 4, 5, 6, 7, 9},
    ],
    [
        """
matrix = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
{val for sublist in matrix if sublist[0] != 4 for val in sublist if val != 8}
""",
        {1, 2, 3, 6, 7, 9},
    ],
    [
        """
# check short-circuit of nested if
cnt = 0
def no_op(i):
    global cnt
    cnt += 1
    return i
[{i for i in range(7) if no_op(i) != 5 if no_op(i) != 3}, cnt]
""",
        [{0, 1, 2, 4, 6}, 13],
    ],
    ["{str(i):i for i in range(5) if i != 3}", {"0": 0, "1": 1, "2": 2, "4": 4}],
    ["i = 100; [{str(i):i for i in range(5) if i != 3}, i]", [{"0": 0, "1": 1, "2": 2, "4": 4}, 100]],
    ["{v:k for k,v in {str(i):i for i in range(5)}.items()}", {0: "0", 1: "1", 2: "2", 3: "3", 4: "4"}],
    [
        "{f'{i}+{k}':i+k for i in range(3) for k in range(3)}",
        {"0+0": 0, "0+1": 1, "0+2": 2, "1+0": 1, "1+1": 2, "1+2": 3, "2+0": 2, "2+1": 3, "2+2": 4},
    ],
    [
        "{f'{i}+{k}':i+k for i in range(3) for k in range(3) if k <= i}",
        {"0+0": 0, "1+0": 1, "1+1": 2, "2+0": 2, "2+1": 3, "2+2": 4},
    ],
    ["def f(l=5): return [i for i in range(l)];\nf(6)", [0, 1, 2, 3, 4, 5]],
    ["def f(l=5): return {i+j for i,j in zip(range(l), range(l))};\nf()", {0, 2, 4, 6, 8}],
    [
        "def f(l=5): return {i:j for i,j in zip(range(l), range(1,l+1))};\nf()",
        {0: 1, 1: 2, 2: 3, 3: 4, 4: 5},
    ],
    [
        """
d = {"x": 1, "y": 2, "z": 3}
s = []
for k, v in d.items():
    s.append(f"{k}: {v}")
s
""",
        ["x: 1", "y: 2", "z: 3"],
    ],
    [
        """
d = {"x": 1, "y": 2, "z": 3}
i = 0
s = []
k = [0, 0, 0]
for k[i], v in d.items():
    s.append([k.copy(), v])
    i += 1
s
""",
        [[["x", 0, 0], 1], [["x", "y", 0], 2], [["x", "y", "z"], 3]],
    ],
    [
        """
def foo(bar=6):
    if bar == 5:
        return
    else:
        return 2 * bar
[foo(), foo(5), foo('xxx')]
""",
        [12, None, "xxxxxx"],
    ],
    [
        """
bar = 100
def foo(bar=6):
    bar += 2
    return eval('bar')
    bar += 5
    return 1000
[foo(), foo(5), bar]
""",
        [8, 7, 100],
    ],
    [
        """
bar = 100
def foo(bar=6):
    bar += 2
    del bar
    return eval('bar')
    bar += 5
    return 1000
[foo(), foo(5), bar]
""",
        [100, 100, 100],
    ],
    [
        """
bar = 100
bar2 = 1000
bar3 = 100
def foo(arg=6):
    global bar, bar2, bar3
    bar += arg
    bar2 = 1001
    del bar3
    return bar
    bar += arg
    return 1000
[foo(), foo(5), bar, bar2]
""",
        [106, 111, 111, 1001],
    ],
    [
        """
def func():
    global x
    x = 134
func()
x
""",
        134,
    ],
    [
        """
def foo0(arg=6):
    bar = 100
    bar2 = 1000
    bar3 = 100
    def foo1(arg=6):
        nonlocal bar, bar2, bar3
        bar += arg
        bar2 = 1001
        del bar3
        return bar
        bar += arg
        return 1000
    return [foo1(arg), bar, bar2]
[foo0(), foo0(5)]
""",
        [[106, 106, 1001], [105, 105, 1001]],
    ],
    [
        """
bar = 50
bar2 = 500
bar3 = 50
def foo0(arg=6):
    bar = 100
    bar2 = 1000
    bar3 = 100
    def foo1(arg=6):
        nonlocal bar, bar2, bar3
        bar += arg
        bar2 = 1001
        del bar3
        return eval('bar')
        bar += arg
        return 1000
    return [foo1(arg), bar, eval('bar2')]
[foo0(), foo0(5)]
""",
        [[106, 106, 1001], [105, 105, 1001]],
    ],
    [
        """
bar = 50
bar2 = 500
bar3 = 50
def foo0(arg=6):
    bar = 100
    bar2 = 1000
    bar3 = 100
    def foo1(arg=6):
        nonlocal bar, bar2, bar3
        bar += arg
        bar2 = 1001
        del bar3
        return eval('bar')
        bar += arg
        return 1000
    # on real python, eval('[foo1(arg), bar, bar2]') doesn't yield
    # the same result as our code; if we eval each entry then they
    # get the same result
    return [eval('foo1(arg)'), eval('bar'), eval('bar2')]
[foo0(), foo0(5), eval('bar'), eval('bar2')]
""",
        [[106, 106, 1001], [105, 105, 1001], 50, 500],
    ],
    [
        """
def f():
    def b():
        return s+g
    s = "hello "
    return b
b = f()
g = "world"
b()
""",
        "hello world",
    ],
    [
        """
@dec_test("abc")
def foo(cnt=4):
    sum = 0
    for i in range(cnt):
        sum += i
        if i == 6:
            return 1000 + sum
        if i == 7:
            break
    return sum
[foo(3), foo(6), foo(10), foo(20), foo()]
""",
        [sum(range(3)), sum(range(6)), 1000 + sum(range(7)), 1000 + sum(range(7)), sum(range(4))],
    ],
    [
        """
def foo(cnt=5):
    sum = 0
    for i in range(cnt):
        if i == 4:
            continue
        if i == 8:
            break
        sum += i
    return sum
[foo(3), foo(6), foo(10), foo(20), foo()]
""",
        [sum(range(3)), sum(range(6)) - 4, sum(range(9)) - 4 - 8, sum(range(9)) - 4 - 8, sum(range(5)) - 4],
    ],
    [
        """
def foo(cnt=5):
    sum = 0
    for i in range(cnt):
        if i == 8:
            break
        sum += i
    else:
        return 1000 + sum
    return sum
[foo(3), foo(6), foo(10), foo(20), foo()]
""",
        [
            sum(range(3)) + 1000,
            sum(range(6)) + 1000,
            sum(range(9)) - 8,
            sum(range(9)) - 8,
            sum(range(5)) + 1000,
        ],
    ],
    [
        """
def foo(cnt=5):
    sum = 0
    i = 0
    while i < cnt:
        if i == 8:
            break
        sum += i
        i += 1
    else:
        return 1000 + sum
    return sum
[foo(3), foo(6), foo(10), foo(20), foo()]
""",
        [
            sum(range(3)) + 1000,
            sum(range(6)) + 1000,
            sum(range(9)) - 8,
            sum(range(9)) - 8,
            sum(range(5)) + 1000,
        ],
    ],
    [
        """
def foo(cnt):
    sum = 0
    for i in range(cnt):
        sum += i
        if i != 6:
            pass
        else:
            return 1000 + sum
        if i == 7:
            break
    return sum
[foo(3), foo(6), foo(10), foo(20)]
""",
        [sum(range(3)), sum(range(6)), 1000 + sum(range(7)), 1000 + sum(range(7))],
    ],
    [
        """
def foo(cnt):
    sum = 0
    i = 0
    while i < cnt:
        sum += i
        if i != 6:
            pass
        else:
            return 1000 + sum
        if i == 7:
            break
        i += 1
    return sum
[foo(3), foo(6), foo(10), foo(20)]
""",
        [sum(range(3)), sum(range(6)), 1000 + sum(range(7)), 1000 + sum(range(7))],
    ],
    [
        """
def foo(x=30, *args, y = 123, **kwargs):
    return [x, y, args, kwargs]
[foo(a = 10, b = 3), foo(40, 7, 8, 9, a = 10, y = 3), foo(x=42)]
""",
        [[30, 123, (), {"a": 10, "b": 3}], [40, 3, (7, 8, 9), {"a": 10}], [42, 123, (), {}]],
    ],
    [
        """
def foo(*args):
    return [*args]
lst = [6, 10]
[foo(2, 3, 10) + [*lst], [foo(*lst), *lst]]
""",
        [[2, 3, 10, 6, 10], [[6, 10], 6, 10]],
    ],
    [
        """
def foo(arg1=None, **kwargs):
    return [arg1, kwargs]
[foo(), foo(arg1=1), foo(arg2=20), foo(arg1=10, arg2=20), foo(**{'arg2': 30})]
""",
        [[None, {}], [1, {}], [None, {"arg2": 20}], [10, {"arg2": 20}], [None, {"arg2": 30}]],
    ],
    [
        """
def func(exc):
    try:
        x = 1
        if exc:
            raise exc
    except NameError as err:
        x += 100
    except (NameError, OSError) as err:
        x += 200
    except Exception as err:
        x += 300
        return x
    else:
        x += 10
    finally:
        x += 2
    x += 1
    return x
[func(None), func(NameError("x")), func(OSError("x")), func(ValueError("x"))]
""",
        [14, 104, 204, 301],
    ],
    [
        """
def func(exc):
    try:
        x = 1
        if exc:
            raise exc
    except NameError as err:
        x += 100
    except (NameError, OSError) as err:
        x += 200
    except Exception as err:
        x += 300
        return x
    else:
        return x + 10
    finally:
        x += 2
        return x
    x += 1
    return x
[func(None), func(NameError("x")), func(OSError("x")), func(ValueError("x"))]
""",
        [3, 103, 203, 303],
    ],
    [
        """
class Test:
    x = 10
    def __init__(self, value):
        self.y = value

    def set_x(self, value):
        Test.x += 2
        self.x = value

    def set_y(self, value):
        self.y = value

    def get(self):
        return [self.x, self.y]

t1 = Test(20)
t2 = Test(40)
Test.x = 5
[t1.get(), t2.get(), t1.set_x(100), t1.get(), t2.get(), Test.x]
""",
        [[5, 20], [5, 40], None, [100, 20], [7, 40], 7],
    ],
    [
        """
i = 10
def f():
    return i
i = 42
f()
""",
        42,
    ],
    [
        """
class Ctx:
    def __init__(self, msgs, val):
        self.val = val
        self.msgs = msgs

    def get(self):
        return self.val

    def __enter__(self):
        self.msgs.append(f"__enter__ {self.val}")
        return self

    def __exit__(self, type, value, traceback):
        self.msgs.append(f"__exit__ {self.val}")

msgs = []
x = [None, None]

with Ctx(msgs, 5) as x[0], Ctx(msgs, 10) as x[1]:
    msgs.append(x[0].get())
    msgs.append(x[1].get())

try:
    with Ctx(msgs, 5) as x[0], Ctx(msgs, 10) as x[1]:
        msgs.append(x[0].get())
        msgs.append(x[1].get())
        1/0
except Exception as exc:
    msgs.append(f"got {exc}")

for i in range(5):
    with Ctx(msgs, 5 + i) as x[0], Ctx(msgs, 10 + i) as x[1]:
        msgs.append(x[0].get())
        if i == 0:
            continue
        msgs.append(x[1].get())
        if i >= 1:
            break

def func(i):
    x = [None, None]
    with Ctx(msgs, 5 + i) as x[0], Ctx(msgs, 10 + i) as x[1]:
        msgs.append(x[0].get())
        if i == 1:
            return x[1].get()
        msgs.append(x[1].get())
        if i == 2:
            return x[1].get() * 2
    return 0
msgs.append(func(0))
msgs.append(func(1))
msgs.append(func(2))
msgs
""",
        [
            "__enter__ 5",
            "__enter__ 10",
            5,
            10,
            "__exit__ 10",
            "__exit__ 5",
            "__enter__ 5",
            "__enter__ 10",
            5,
            10,
            "__exit__ 10",
            "__exit__ 5",
            "got division by zero",
            "__enter__ 5",
            "__enter__ 10",
            5,
            "__exit__ 10",
            "__exit__ 5",
            "__enter__ 6",
            "__enter__ 11",
            6,
            11,
            "__exit__ 11",
            "__exit__ 6",
            "__enter__ 5",
            "__enter__ 10",
            5,
            10,
            "__exit__ 10",
            "__exit__ 5",
            0,
            "__enter__ 6",
            "__enter__ 11",
            6,
            "__exit__ 11",
            "__exit__ 6",
            11,
            "__enter__ 7",
            "__enter__ 12",
            7,
            12,
            "__exit__ 12",
            "__exit__ 7",
            24,
        ],
    ],
    [
        """
def func1(m):
    def func2():
        m[0] += 1
        return m[0]

    def func3():
        n[0] += 10
        return n[0]

    n = m
    return func2, func3

f2, f3 = func1([10])
[f2(), f3(), f2(), f3(), f2(), f3()]
""",
        [11, 21, 22, 32, 33, 43],
    ],
    [
        """
def func1(m=0):
    def func2():
        nonlocal m
        m += 1
        return eval("m")

    def func3():
        nonlocal n
        n += 10
        return n

    n = m
    return func2, func3

f2, f3 = func1(10)
f4, f5 = func1(50)
[f2(), f3(), f4(), f5(), f2(), f3(), f4(), f5(), f2(), f3(), f4(), f5()]
""",
        [11, 20, 51, 60, 12, 30, 52, 70, 13, 40, 53, 80],
    ],
    [
        """
def func():
    k = 10
    def f1():
        nonlocal i
        i += 2
        return i
    def f2():
        nonlocal k
        k += 5
        return k
    i = 40
    k += 5
    return f1, f2
f1, f2 = func()
[f1(), f2(), f1(), f2(), f1(), f2()]
""",
        [42, 20, 44, 25, 46, 30],
    ],
    [
        """
def f1():
    return 100

def func():
    def f2(x):
        nonlocal y
        y += f1(2*x)
        return y

    def f1(x):
        nonlocal y
        y += x
        return y

    y = 1
    return f1, f2

f3, f4 = func()
[f3(2), f4(3), f3(4), f4(5)]
""",
        [3, 12, 16, 42],
    ],
    [
        """
def func():
    def f1():
        nonlocal i
        del i
        i = 20
        return i + 1

    def f2():
        return 2 * i

    i = 10
    return f1, f2

f1, f2 = func()
[f2(), f1(), f2()]
""",
        [20, 21, 40],
    ],
    [
        """
def func():
    def func2():
        z = x + 2
        return z
    x = 1
    return func2()
func()
""",
        3,
    ],
]


async def run_one_test(test_data):
    """Run one interpreter test."""
    source, expect = test_data
    global_ctx = GlobalContext("test", global_sym_table={}, manager=GlobalContextMgr)
    ast = AstEval("test", global_ctx=global_ctx)
    ast.parse(source)
    if ast.get_exception() is not None:
        print(f"Parsing {source} failed: {ast.get_exception()}")
    # print(ast.dump())
    result = await ast.eval({"sym_local": 10})
    assert result == expect


async def test_eval(hass):
    """Test interpreter."""
    hass.data[DOMAIN] = MockConfigEntry(domain=DOMAIN, data={CONF_ALLOW_ALL_IMPORTS: False})
    Function.init(hass)
    State.init(hass)
    State.register_functions()

    for test_data in evalTests:
        await run_one_test(test_data)


evalTestsExceptions = [
    [None, "parsing error compile() arg 1 must be a string, bytes or AST object"],
    ["1+", "syntax error invalid syntax (test, line 1)"],
    ["1+'x'", "Exception in test line 1 column 2: unsupported operand type(s) for +: 'int' and 'str'"],
    ["xx", "Exception in test line 1 column 0: name 'xx' is not defined"],
    ["(x, y) = (1, 2, 4)", "Exception in test line 1 column 16: too many values to unpack (expected 2)"],
    [
        "(x, y) = iter([1, 2, 4])",
        "Exception in test line 1 column 21: too many values to unpack (expected 2)",
    ],
    ["(x, y, z) = (1, 2)", "Exception in test line 1 column 16: too few values to unpack (expected 3)"],
    [
        "(x, y, z) = iter([1, 2])",
        "Exception in test line 1 column 21: too few values to unpack (expected 3)",
    ],
    ["(x, y) = 1", "Exception in test line 1 column 9: cannot unpack non-iterable object"],
    [
        "a, *y, w, z = range(2)",
        "Exception in test line 1 column 20: too few values to unpack (expected at least 3)",
    ],
    ["assert 1 == 0, 'this is an error'", "Exception in test line 1 column 15: this is an error"],
    ["assert 1 == 0", "Exception in test line 1 column 12: "],
    [
        "import math; math.sinXYZ",
        "Exception in test line 1 column 13: module 'math' has no attribute 'sinXYZ'",
    ],
    ["del xx", "Exception in test line 1 column 0: name 'xx' is not defined"],
    ["return", "Exception in test line 1 column 0: return statement outside function"],
    ["break", "Exception in test line 1 column 0: break statement outside loop"],
    ["continue", "Exception in test line 1 column 0: continue statement outside loop"],
    ["raise", "Exception in test line 1 column 0: No active exception to reraise"],
    ["yield", "Exception in test line 1 column 0: test: not implemented ast ast_yield"],
    ["task.executor(5)", "Exception in test line 1 column 14: function is not callable by task.executor()"],
    [
        "state.get('pyscript.xyz1.abc')",
        "Exception in test line 1 column 10: name 'pyscript.xyz1' is not defined",
    ],
    [
        "pyscript.xyz1 = 1; state.get('pyscript.xyz1.abc')",
        "Exception in test line 1 column 29: state 'pyscript.xyz1' has no attribute 'abc'",
    ],
    [
        "import cmath; exec('xyz = cmath.sqrt(complex(3, 4))', {})",
        "Exception in test line 1 column 54: Exception in exec() line 1 column 6: name 'cmath.sqrt' is not defined",
    ],
    ["func1(1)", "Exception in test line 1 column 0: name 'func1' is not defined"],
    [
        "def func(a):\n    pass\nfunc()",
        "Exception in test line 3 column 0: func() missing 1 required positional arguments",
    ],
    [
        "def func(a):\n    pass\nfunc(1, 2)",
        "Exception in test line 3 column 8: func() called with too many positional arguments",
    ],
    [
        "def func(a=1):\n    pass\nfunc(1, a=3)",
        "Exception in test line 3 column 5: func() got multiple values for argument 'a'",
    ],
    [
        "def func(*a, b):\n    pass\nfunc(1, 2)",
        "Exception in test line 3 column 8: func() missing required keyword-only arguments",
    ],
    [
        "from .xyz import abc",
        "Exception in test line 1 column 0: attempted relative import with no known parent package",
    ],
    [
        "from ...xyz import abc",
        "Exception in test line 1 column 0: attempted relative import with no known parent package",
    ],
    [
        "from . import abc",
        "Exception in test line 1 column 0: attempted relative import with no known parent package",
    ],
    ["import asyncio", "Exception in test line 1 column 0: import of asyncio not allowed"],
    ["import xyzabc123", "Exception in test line 1 column 0: import of xyzabc123 not allowed"],
    ["from asyncio import xyz", "Exception in test line 1 column 0: import from asyncio not allowed"],
    [
        """
def func():
    nonlocal x
    x = 1
func()
""",
        "Exception in test line 2 column 0: no binding for nonlocal 'x' found",
    ],
    [
        """
def func():
    nonlocal x
    x += 1
func()
""",
        "Exception in test line 2 column 0: no binding for nonlocal 'x' found",
    ],
    [
        """
def func():
    global x
    return x
func()
""",
        "Exception in func(), test line 4 column 11: global name 'x' is not defined",
    ],
    [
        """
def func():
    x = 1
    eval('1 + y')
func()
""",
        "Exception in test line 4 column 9: Exception in func(), eval() line 1 column 4: name 'y' is not defined",
    ],
    [
        """
try:
    d = {}
    x = d["bad_key"]
except KeyError:
    raise
""",
        "Exception in test line 4 column 10: 'bad_key'",
    ],
    [
        """
def func():
    def func2():
        nonlocal x
        del x
        del x
    x = 1
    func2()
func()
""",
        "Exception in func2(), test line 6 column 8: name 'x' is not defined",
    ],
    [
        """
def func():
    def func2():
        z = x + 2
        return z
        del x
    x = 1
    return func2()
func()
""",
        "Exception in func2(), test line 4 column 12: name 'x' is not defined",
    ],
]


async def run_one_test_exception(test_data):
    """Run one interpreter test that generates an exception."""
    source, expect = test_data
    global_ctx = GlobalContext("test", global_sym_table={}, manager=GlobalContextMgr)
    ast = AstEval("test", global_ctx=global_ctx)
    ast.parse(source)
    exc = ast.get_exception()
    if exc is not None:
        assert exc == expect
        return
    await ast.eval()
    exc = ast.get_exception()
    if exc is not None:
        assert exc == expect
        return
    assert False


async def test_eval_exceptions(hass):
    """Test interpreter exceptions."""
    hass.data[DOMAIN] = MockConfigEntry(domain=DOMAIN, data={CONF_ALLOW_ALL_IMPORTS: False})
    Function.init(hass)
    State.init(hass)
    State.register_functions()

    for test_data in evalTestsExceptions:
        await run_one_test_exception(test_data)
