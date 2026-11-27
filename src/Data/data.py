"""
data.py  --  AI Smart Kitchen & MasterChef  (Owner: Squad 1, Task B)
====================================================================
Single source of truth for the whole project. Every other module imports from here:

    uninformed.py  (Squad 1)  -> RULES, get_applicable_rules, apply_rule, is_goal
    informed.py    (Squad 2)  -> RULES, GOAL_DISHES, DISH_RAW_REQUIREMENTS, rule cost
    games.py       (Squad 3)  -> GAME_INGREDIENTS, GAME_RECIPES
    genetic.py     (Squad 4)  -> MEALS, get_meals_by_type
    app.py         (Squad 4)  -> INGREDIENTS (for the fridge checklist), everything else

TEAM RULE: after this file is locked, do NOT edit it without notifying everyone.

--------------------------------------------------------------------
STATE-SPACE MODEL (important for the search algorithms)
--------------------------------------------------------------------
* A STATE is a frozenset of item names the user currently has
  (raw ingredients + intermediate items + finished dishes).
* A RULE is a dict:
      {"id": int, "name": str, "inputs": [..], "output": str, "action": str, "cost": int}
  A rule is APPLICABLE when all its inputs are in the state.
  ("name" is a short label; "action" is the longer description shown in the UI / tree edges.)
* Applying a rule CONSUMES its inputs and ADDS its output (Minecraft-style crafting):
      new_state = (state - inputs) | {output}
  Use apply_rule(state, rule) so everyone does it identically.
* Each item exists ONCE (set semantics, no quantities) -> keeps the state space small.
* A GOAL state is any state that contains a dish from GOAL_DISHES (a name in MEALS).
* cost = preparation time in MINUTES (used by UCS / A*).
  Every rule is one "step" (used by BFS and DLS depth).
"""

# ======================================================================
# 1) INGREDIENTS
# ======================================================================
# Raw ingredients the user can tick in the "Smart Fridge" tab (15 total).
INGREDIENTS = [
    "flour", "water", "eggs", "tomato", "garlic", "cheese", "beef", "pasta",
    "milk", "rice", "chicken", "potato", "onion", "bread", "oil",
]

# Items produced by rules (not in the fridge, created while cooking).
INTERMEDIATE_ITEMS = [
    "dough", "pizza_base", "tomato_sauce", "white_sauce", "pancake_batter",
    "cooked_rice", "fried_eggs", "grilled_chicken", "beef_mix", "boiled_potato",
    "cooked_pasta", "toast", "chopped_salad",
]

# ======================================================================
# 2) CRAFTING RULES  (29 rules: 13 intermediate + 16 dish rules)
# ======================================================================
RULES = [
    # ---------------- intermediate preparations ----------------
    {"id": 1,  "name": "Knead dough",        "inputs": ["flour", "water"],    "output": "dough",           "action": "Knead dough (flour + water)",          "cost": 10},
    {"id": 2,  "name": "Shape pizza base",   "inputs": ["dough", "oil"],      "output": "pizza_base",      "action": "Shape pizza base (dough + oil)",       "cost": 8},
    {"id": 3,  "name": "Cook tomato sauce",  "inputs": ["tomato", "garlic"],  "output": "tomato_sauce",    "action": "Cook tomato sauce (tomato + garlic)",  "cost": 8},
    {"id": 4,  "name": "Make white sauce",   "inputs": ["milk", "flour"],     "output": "white_sauce",     "action": "Make white sauce (milk + flour)",      "cost": 7},
    {"id": 5,  "name": "Mix pancake batter", "inputs": ["flour", "milk"],     "output": "pancake_batter",  "action": "Mix pancake batter (flour + milk)",    "cost": 5},
    {"id": 6,  "name": "Boil rice",          "inputs": ["rice", "water"],     "output": "cooked_rice",     "action": "Boil rice (rice + water)",             "cost": 15},
    {"id": 7,  "name": "Fry eggs",           "inputs": ["eggs", "oil"],       "output": "fried_eggs",      "action": "Fry eggs (eggs + oil)",                "cost": 5},
    {"id": 8,  "name": "Grill chicken",      "inputs": ["chicken", "oil"],    "output": "grilled_chicken", "action": "Grill chicken (chicken + oil)",        "cost": 15},
    {"id": 9,  "name": "Season beef",        "inputs": ["beef", "onion"],     "output": "beef_mix",        "action": "Mix & season beef (beef + onion)",     "cost": 10},
    {"id": 10, "name": "Boil potato",        "inputs": ["potato", "water"],   "output": "boiled_potato",   "action": "Boil potato (potato + water)",         "cost": 12},
    {"id": 11, "name": "Boil pasta",         "inputs": ["pasta", "water"],    "output": "cooked_pasta",    "action": "Boil pasta (pasta + water)",           "cost": 10},
    {"id": 12, "name": "Toast bread",        "inputs": ["bread", "oil"],      "output": "toast",           "action": "Toast bread (bread + oil)",            "cost": 3},
    {"id": 13, "name": "Chop salad",         "inputs": ["tomato", "onion"],   "output": "chopped_salad",   "action": "Chop salad (tomato + onion)",          "cost": 4},

    # ---------------- Breakfast dishes ----------------
    {"id": 14, "name": "Make omelette",      "inputs": ["fried_eggs", "cheese"],         "output": "Omelette",     "action": "Fold omelette (fried eggs + cheese)",        "cost": 4},
    {"id": 15, "name": "Make cheese toast",  "inputs": ["toast", "cheese"],              "output": "Cheese Toast", "action": "Melt cheese on toast",                       "cost": 4},
    {"id": 16, "name": "Make egg sandwich",  "inputs": ["fried_eggs", "bread"],          "output": "Egg Sandwich", "action": "Assemble egg sandwich",                      "cost": 4},
    {"id": 17, "name": "Make pancakes",      "inputs": ["pancake_batter", "eggs"],       "output": "Pancakes",     "action": "Cook pancakes (batter + eggs)",              "cost": 8},
    {"id": 18, "name": "Make shakshuka",     "inputs": ["fried_eggs", "tomato_sauce"],   "output": "Shakshuka",    "action": "Simmer eggs in tomato sauce",                "cost": 8},

    # ---------------- Lunch dishes ----------------
    {"id": 19, "name": "Make chicken rice",  "inputs": ["grilled_chicken", "cooked_rice"],   "output": "Chicken Rice",  "action": "Plate chicken over rice",               "cost": 6},
    {"id": 20, "name": "Make beef burger",   "inputs": ["beef_mix", "bread"],                "output": "Beef Burger",   "action": "Grill burger patty & assemble",         "cost": 10},
    {"id": 21, "name": "Make chicken salad", "inputs": ["grilled_chicken", "chopped_salad"], "output": "Chicken Salad", "action": "Top salad with grilled chicken",        "cost": 3},
    {"id": 22, "name": "Make beef rice bowl", "inputs": ["beef_mix", "cooked_rice"],         "output": "Beef Rice Bowl", "action": "Serve seasoned beef over rice",        "cost": 6},
    {"id": 23, "name": "Make tomato rice",   "inputs": ["cooked_rice", "tomato_sauce"],      "output": "Tomato Rice",   "action": "Stir tomato sauce into rice",           "cost": 5},

    # ---------------- Dinner dishes ----------------
    {"id": 24, "name": "Make spaghetti pomodoro", "inputs": ["cooked_pasta", "tomato_sauce"],           "output": "Spaghetti Pomodoro",     "action": "Toss pasta in tomato sauce",              "cost": 5},
    {"id": 25, "name": "Make mac and cheese",     "inputs": ["cooked_pasta", "white_sauce", "cheese"],  "output": "Mac and Cheese",         "action": "Bake pasta with white sauce & cheese",    "cost": 6},
    {"id": 26, "name": "Bake pizza (dough)",      "inputs": ["pizza_base", "tomato_sauce", "cheese"],   "output": "Cheese Pizza",           "action": "Bake pizza from dough base",              "cost": 10},
    {"id": 27, "name": "Roast beef & potato",     "inputs": ["beef_mix", "boiled_potato"],              "output": "Beef Potato Plate",      "action": "Roast beef with potatoes",                "cost": 15},
    {"id": 28, "name": "Plate chicken & potato",  "inputs": ["grilled_chicken", "boiled_potato"],       "output": "Grilled Chicken Potato", "action": "Plate grilled chicken with potatoes",     "cost": 5},

    # ---------------- Alternative route (makes BFS != UCS in the demo) ----------------
    # Cheese Pizza via bread: FEWER steps (BFS prefers it) but MORE expensive (UCS prefers dough route).
    {"id": 29, "name": "Bake pizza (bread)", "inputs": ["bread", "tomato_sauce", "cheese"], "output": "Cheese Pizza", "action": "Quick bread pizza (bread + sauce + cheese)", "cost": 35},
]

# ======================================================================
# 3) MEALS  (15 ready meals with nutrition + price)
# ======================================================================
# type     : "breakfast" | "lunch" | "dinner"  (used by the Genetic Algorithm slots)
# calories : kcal per serving      protein : grams      price : EGP per serving
# requires : raw ingredients needed for the standard recipe (heuristic / UI hints)
MEALS = [
    # ---- Breakfast ----
    {"name": "Omelette",     "type": "breakfast", "calories": 320, "protein": 20, "price": 25, "requires": ["eggs", "oil", "cheese"]},
    {"name": "Cheese Toast", "type": "breakfast", "calories": 350, "protein": 14, "price": 20, "requires": ["bread", "oil", "cheese"]},
    {"name": "Egg Sandwich", "type": "breakfast", "calories": 400, "protein": 18, "price": 28, "requires": ["eggs", "oil", "bread"]},
    {"name": "Pancakes",     "type": "breakfast", "calories": 450, "protein": 12, "price": 22, "requires": ["flour", "milk", "eggs"]},
    {"name": "Shakshuka",    "type": "breakfast", "calories": 300, "protein": 16, "price": 30, "requires": ["eggs", "oil", "tomato", "garlic"]},
    # ---- Lunch ----
    {"name": "Chicken Rice",   "type": "lunch", "calories": 650, "protein": 42, "price": 70, "requires": ["chicken", "oil", "rice", "water"]},
    {"name": "Beef Burger",    "type": "lunch", "calories": 700, "protein": 35, "price": 65, "requires": ["beef", "onion", "bread"]},
    {"name": "Chicken Salad",  "type": "lunch", "calories": 380, "protein": 35, "price": 55, "requires": ["chicken", "oil", "tomato", "onion"]},
    {"name": "Beef Rice Bowl", "type": "lunch", "calories": 620, "protein": 33, "price": 68, "requires": ["beef", "onion", "rice", "water"]},
    {"name": "Tomato Rice",    "type": "lunch", "calories": 480, "protein": 10, "price": 25, "requires": ["rice", "water", "tomato", "garlic"]},
    # ---- Dinner ----
    {"name": "Spaghetti Pomodoro",     "type": "dinner", "calories": 520, "protein": 16, "price": 35, "requires": ["pasta", "water", "tomato", "garlic"]},
    {"name": "Mac and Cheese",         "type": "dinner", "calories": 650, "protein": 24, "price": 45, "requires": ["pasta", "water", "milk", "flour", "cheese"]},
    {"name": "Cheese Pizza",           "type": "dinner", "calories": 750, "protein": 30, "price": 60, "requires": ["flour", "water", "oil", "tomato", "garlic", "cheese"]},
    {"name": "Beef Potato Plate",      "type": "dinner", "calories": 680, "protein": 38, "price": 75, "requires": ["beef", "onion", "potato", "water"]},
    {"name": "Grilled Chicken Potato", "type": "dinner", "calories": 600, "protein": 40, "price": 60, "requires": ["chicken", "oil", "potato", "water"]},
]

# ======================================================================
# 4) DERIVED LOOKUPS (built automatically - do not edit by hand)
# ======================================================================
MEALS_BY_NAME = {m["name"]: m for m in MEALS}
GOAL_DISHES = frozenset(MEALS_BY_NAME)                       # all finished dishes
DISH_RAW_REQUIREMENTS = {m["name"]: list(m["requires"]) for m in MEALS}
RULES_BY_ID = {r["id"]: r for r in RULES}
RULES_BY_OUTPUT = {}
for _r in RULES:
    RULES_BY_OUTPUT.setdefault(_r["output"], []).append(_r)
MIN_RULE_COST = min(r["cost"] for r in RULES)                # handy lower bound for heuristics

# ======================================================================
# 5) HELPER FUNCTIONS  (everyone should use these so behaviour stays identical)
# ======================================================================
def to_state(items):
    """Convert any iterable of item names to a state (frozenset)."""
    return frozenset(items)


def get_applicable_rules(state):
    """All rules whose inputs are fully contained in `state`.
    Returned in ascending rule-id order -> deterministic search (same tree every run)."""
    state = to_state(state)
    return [r for r in RULES if all(i in state for i in r["inputs"])]


def apply_rule(state, rule):
    """Consume the rule's inputs and add its output. Returns a NEW frozenset."""
    return (to_state(state) - frozenset(rule["inputs"])) | {rule["output"]}


def get_goal_dishes_in_state(state):
    """List of finished dishes currently present in `state`."""
    return sorted(i for i in to_state(state) if i in GOAL_DISHES)


def is_goal(state):
    """True if the state already contains a finished dish."""
    return any(i in GOAL_DISHES for i in to_state(state))


def get_meal(name):
    """Meal dict by name (KeyError if unknown)."""
    return MEALS_BY_NAME[name]


def get_meals_by_type(meal_type=None):
    """Meals filtered by 'breakfast' / 'lunch' / 'dinner'; all meals if None."""
    if meal_type is None:
        return list(MEALS)
    return [m for m in MEALS if m["type"] == meal_type]


# ======================================================================
# 6) TABLE GAME DATA  (for games.py - Squad 3)
# ======================================================================
# Pool of ingredients the shared table of 8 is drawn from (random.sample(GAME_INGREDIENTS, 8)).
GAME_INGREDIENTS = [
    "flour", "water", "eggs", "tomato", "garlic", "cheese", "beef", "pasta",
    "milk", "rice", "chicken", "potato",
]

# Secret 3-ingredient recipes the player / AI can be dealt (24 recipes).
# Each uses 3 DIFFERENT ingredients from GAME_INGREDIENTS; many share ingredients on purpose,
# so grabbing one item can both help you AND block the opponent.
GAME_RECIPES = [
    {"name": "Spaghetti Pomodoro",  "ingredients": ("pasta", "tomato", "garlic")},
    {"name": "Cheese Pizza",        "ingredients": ("flour", "tomato", "cheese")},
    {"name": "Chicken Rice",        "ingredients": ("chicken", "rice", "water")},
    {"name": "Beef Potato Plate",   "ingredients": ("beef", "potato", "garlic")},
    {"name": "Mac and Cheese",      "ingredients": ("pasta", "milk", "cheese")},
    {"name": "Omelette",            "ingredients": ("eggs", "cheese", "milk")},
    {"name": "Fresh Dough",         "ingredients": ("flour", "water", "eggs")},
    {"name": "Chicken Potato",      "ingredients": ("chicken", "potato", "garlic")},
    {"name": "Pancakes",            "ingredients": ("flour", "milk", "eggs")},
    {"name": "Shakshuka",           "ingredients": ("eggs", "tomato", "garlic")},
    {"name": "Tomato Rice",         "ingredients": ("rice", "tomato", "garlic")},
    {"name": "Beef Rice Bowl",      "ingredients": ("beef", "rice", "water")},
    {"name": "Cheesy Potato Bake",  "ingredients": ("potato", "cheese", "milk")},
    {"name": "Beef Pasta",          "ingredients": ("beef", "pasta", "tomato")},
    {"name": "Chicken Pasta",       "ingredients": ("chicken", "pasta", "cheese")},
    {"name": "Chicken Tomato Stew", "ingredients": ("chicken", "tomato", "garlic")},
    {"name": "Cheesy Rice",         "ingredients": ("rice", "cheese", "milk")},
    {"name": "Egg Fried Rice",      "ingredients": ("eggs", "rice", "garlic")},
    {"name": "Mashed Potato",       "ingredients": ("potato", "milk", "garlic")},
    {"name": "Egg Potato Salad",    "ingredients": ("eggs", "potato", "water")},
    {"name": "Cheese Bread",        "ingredients": ("flour", "cheese", "water")},
    {"name": "Beef Stew",           "ingredients": ("beef", "potato", "tomato")},
    {"name": "Chicken Soup",        "ingredients": ("chicken", "water", "potato")},
    {"name": "Cheese Pasta Bake",   "ingredients": ("pasta", "cheese", "tomato")},
]
GAME_TABLE_SIZE = 8
GAME_RECIPE_SIZE = 3

# ======================================================================
# 7) SELF-CHECK  ->  run:  python data.py
# ======================================================================
def _reachable_dishes(start_items, max_states=50000):
    """Exhaustive DFS from a start state; returns set of dishes that can be produced."""
    start = to_state(start_items)
    seen, stack, found = {start}, [start], set()
    while stack and len(seen) < max_states:
        s = stack.pop()
        found.update(get_goal_dishes_in_state(s))
        for r in get_applicable_rules(s):
            n = apply_rule(s, r)
            if n not in seen:
                seen.add(n)
                stack.append(n)
    return found


def validate_data():
    """Raises AssertionError with a clear message if anything is inconsistent."""
    # counts required by the brief
    assert 14 <= len(INGREDIENTS) <= 16, f"Need about 15 raw ingredients, got {len(INGREDIENTS)}"
    assert 25 <= len(RULES) <= 30, f"Need 25-30 rules, got {len(RULES)}"
    assert len(MEALS) == 15, f"Need 15 meals, got {len(MEALS)}"

    # unique ids / names
    assert len({r["id"] for r in RULES}) == len(RULES), "Duplicate rule id"
    assert len({r["name"] for r in RULES}) == len(RULES), "Duplicate rule name"
    assert len(MEALS_BY_NAME) == len(MEALS), "Duplicate meal name"

    # rule structure
    known = set(INGREDIENTS) | set(INTERMEDIATE_ITEMS) | set(GOAL_DISHES)
    for r in RULES:
        assert set(r) == {"id", "name", "inputs", "output", "action", "cost"}, f"Rule {r['id']}: bad keys"
        assert r["cost"] > 0, f"Rule {r['id']}: cost must be > 0"
        assert len(set(r["inputs"])) == len(r["inputs"]), f"Rule {r['id']}: repeated input"
        for i in r["inputs"]:
            assert i in known, f"Rule {r['id']}: unknown input '{i}'"
        assert r["output"] in known, f"Rule {r['id']}: unknown output '{r['output']}'"
        assert r["output"] not in r["inputs"], f"Rule {r['id']}: output used as input"

    # meal structure
    for m in MEALS:
        assert set(m) == {"name", "type", "calories", "protein", "price", "requires"}, f"{m['name']}: bad keys"
        assert m["type"] in ("breakfast", "lunch", "dinner"), f"{m['name']}: bad type"
        assert m["calories"] > 0 and m["protein"] >= 0 and m["price"] > 0, f"{m['name']}: bad numbers"
        for i in m["requires"]:
            assert i in INGREDIENTS, f"{m['name']}: unknown required ingredient '{i}'"

    # at least 4 meals per slot for the Genetic Algorithm
    for t in ("breakfast", "lunch", "dinner"):
        assert len(get_meals_by_type(t)) >= 4, f"Too few {t} meals for the GA"

    # every ingredient is used somewhere
    used = {i for r in RULES for i in r["inputs"]}
    for ing in INGREDIENTS:
        assert ing in used, f"Ingredient '{ing}' is never used by any rule"

    # every meal is craftable from its own 'requires' list
    for m in MEALS:
        assert m["name"] in _reachable_dishes(m["requires"]), f"{m['name']} NOT craftable from its requires"

    # game data
    for g in GAME_RECIPES:
        assert len(g["ingredients"]) == GAME_RECIPE_SIZE, f"Game recipe {g['name']}: wrong size"
        for i in g["ingredients"]:
            assert i in GAME_INGREDIENTS, f"Game recipe {g['name']}: '{i}' not in GAME_INGREDIENTS"
    assert len(GAME_INGREDIENTS) >= GAME_TABLE_SIZE
    assert len(GAME_RECIPES) >= 20, f"Need many 3-ingredient game recipes, got {len(GAME_RECIPES)}"
    assert len({g["name"] for g in GAME_RECIPES}) == len(GAME_RECIPES), "Duplicate game recipe name"
    assert len({frozenset(g["ingredients"]) for g in GAME_RECIPES}) == len(GAME_RECIPES), \
        "Duplicate game recipe (same 3 ingredients)"
    for g in GAME_RECIPES:
        assert len(set(g["ingredients"])) == GAME_RECIPE_SIZE, f"Game recipe {g['name']}: ingredients must be 3 different items"

    # edge case: ingredients that can form NO dish
    assert not _reachable_dishes(["water", "oil"]), "water+oil should not form any dish"
    return True


if __name__ == "__main__":
    validate_data()
    print("data.py OK")
    print(f"  ingredients : {len(INGREDIENTS)}")
    print(f"  rules       : {len(RULES)}")
    print(f"  meals       : {len(MEALS)}  "
          f"(breakfast={len(get_meals_by_type('breakfast'))}, "
          f"lunch={len(get_meals_by_type('lunch'))}, "
          f"dinner={len(get_meals_by_type('dinner'))})")