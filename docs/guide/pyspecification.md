# With pyspecification

Formulas have no `if`: they compute **how much**. Real policies also need **which
calculation applies**: "teachers on full-time contracts get 50% of salary, part-timers
15%, everyone else 10%". That is a job for
[pyspecification](https://aaltatan.github.io/pyspecification/), which builds composable
yes/no rules from the same kind of objects.

- pyspecification decides **whether** a rule applies,
- pyformula computes the **number** when it does.

```bash
uv add pyformula pyspecification
```

## Example: an end-of-year bonus policy

```python
from dataclasses import dataclass
from decimal import Decimal

from pyspecification import ObjectRulesRegistry, Predicate

from pyformula import Formula, VariablesRegistry


@dataclass
class Employee:
    name: str
    role: str
    contract: str
    salary: Decimal
    years: int


rules = ObjectRulesRegistry[Employee, bool](operator="logical")
numbers = VariablesRegistry[Employee]()


@rules.rule()
def role__eq(employee: Employee, role: str) -> bool:
    return employee.role == role


@rules.rule()
def contract__eq(employee: Employee, contract: str) -> bool:
    return employee.contract == contract


@numbers.variable()
def salary(employee: Employee) -> Decimal:
    return employee.salary


@numbers.variable()
def years(employee: Employee) -> int:
    return employee.years


@dataclass(frozen=True)
class Case:
    when: Predicate[Employee, bool]
    then: Formula[Employee]


@dataclass(frozen=True)
class Policy:
    cases: list[Case]
    otherwise: Formula[Employee]

    def __call__(self, employee: Employee) -> Decimal:
        for case in self.cases:
            if case.when(employee):
                return case.then(employee)

        return self.otherwise(employee)


full_time = contract__eq("full_time")

bonus = Policy(
    cases=[
        Case(role__eq("admin") & full_time, salary * Decimal("0.25")),
        Case(role__eq("teacher") & full_time, salary * Decimal("0.50") + years * 20),
        Case(role__eq("teacher") & contract__eq("part_time"), salary * Decimal("0.15")),
    ],
    otherwise=salary * Decimal("0.10"),
)

staff = [
    Employee("Huda", "teacher", "full_time", Decimal("1200"), years=8),
    Employee("Sami", "teacher", "part_time", Decimal("600"), years=2),
    Employee("Lina", "admin", "full_time", Decimal("1500"), years=4),
    Employee("Omar", "driver", "full_time", Decimal("700"), years=10),
]

assert [bonus(e) for e in staff] == [Decimal("760.00"), Decimal("90.00"), Decimal("375.00"), Decimal("70.00")]
```

The first matching case wins, so order the cases from most to least specific.

## Both halves as JSON

Each half has its own compiler, so a whole policy can be stored and edited as data:

```python
import json

from pyspecification import PredicateCompiler

from pyformula import FormulaCompiler, decimal_literal

when = PredicateCompiler(
    rules.rules,
    lambda wrapper: Predicate(lambda _: wrapper["operator"] == "all", operator="logical"),
)
then = FormulaCompiler(numbers.variables, literal=decimal_literal)

STORED_POLICY = json.loads("""
{
  "cases": [
    {
      "when": {"operator": "all", "expressions": [
        {"name": "role__eq", "args": ["teacher"], "kwargs": {}, "inverse": false},
        {"name": "contract__eq", "args": ["full_time"], "kwargs": {}, "inverse": false}
      ]},
      "then": {"operator": "add", "expressions": [
        {"operator": "multiply", "expressions": ["salary", 0.5]},
        {"operator": "multiply", "expressions": ["years", 20]}
      ]}
    }
  ],
  "otherwise": {"operator": "multiply", "expressions": ["salary", 0.1]}
}
""")

stored_bonus = Policy(
    cases=[Case(when.compile(c["when"]), then.compile(c["then"])) for c in STORED_POLICY["cases"]],
    otherwise=then.compile(STORED_POLICY["otherwise"]),
)

assert stored_bonus(staff[0]) == Decimal("760.0")
assert stored_bonus(staff[1]) == Decimal("60.0")
```

Both compilers check everything when the policy is loaded, and both add JSON-path notes
to their errors, so an editor can point at the exact case that is wrong.

## Explaining the result

pyspecification can say why a case did **not** apply, which turns a surprising number
into an answer:

```python
sami = staff[1]
first_case = bonus.cases[1]

assert [str(f) for f in first_case.when.failures(sami)] == ["contract__eq('full_time')"]
```

A family package, pyruleset, packages this "first matching case" pattern; its
`{"when": ...}` node plugs into the formula schema through
[`nodes=`](json-schema.md#extra-node-shapes).
