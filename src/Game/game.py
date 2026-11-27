import random
from itertools import combinations

from src.Data.data import (
    GAME_INGREDIENTS,
    GAME_RECIPES,
    GAME_TABLE_SIZE,
    GAME_RECIPE_SIZE
)


def create_game_state():

    # Generate all possible pairs of recipes
    recipe_pairs = list(combinations(GAME_RECIPES, 2))

    # Find valid recipe pairs
    valid_pairs = []

    for recipe1, recipe2 in recipe_pairs:

        required_items = (
            set(recipe1["ingredients"]) |
            set(recipe2["ingredients"])
        )

        if (
            len(recipe1["ingredients"]) == GAME_RECIPE_SIZE
            and len(recipe2["ingredients"]) == GAME_RECIPE_SIZE
            and len(required_items) <= GAME_RECIPE_SIZE * 2
            and len(required_items) <= GAME_TABLE_SIZE
        ):
            valid_pairs.append((recipe1, recipe2))

    if not valid_pairs:
        raise ValueError("No valid recipe combination found!")

    # Randomly select two recipes
    player_recipe, ai_recipe = random.choice(valid_pairs)

    # Get required ingredients
    required_items = (
        set(player_recipe["ingredients"]) |
        set(ai_recipe["ingredients"])
    )

    # Get extra ingredients
    extra_items = [
        item for item in GAME_INGREDIENTS
        if item not in required_items
    ]

    # Calculate remaining table slots
    remaining_slots = GAME_TABLE_SIZE - len(required_items)

    if len(extra_items) < remaining_slots:
        raise ValueError("Not enough ingredients to fill the table!")

    # Create the table
    table_items = list(required_items)
    table_items.extend(random.sample(extra_items, remaining_slots))

    random.shuffle(table_items)

    # Initialize game state
    game_state = {
        "player_recipe": player_recipe,
        "ai_recipe": ai_recipe,
        "table": table_items,
        "player_items": [],
        "ai_items": [],
        "player_moves": 0,
        "ai_moves": 0,
        "current_turn": "player",
        "game_over": False,
        "winner": None
    }

    return game_state


def determine_winner(game_state):

    # Get each player's recipe
    player_recipe = set(game_state["player_recipe"]["ingredients"])
    ai_recipe = set(game_state["ai_recipe"]["ingredients"])

    # Get collected ingredients
    player_items = set(game_state["player_items"])
    ai_items = set(game_state["ai_items"])

    # Count completed recipe ingredients
    player_progress = len(player_recipe & player_items)
    ai_progress = len(ai_recipe & ai_items)

    # Compare recipe progress
    if player_progress > ai_progress:
        return "player"

    if ai_progress > player_progress:
        return "ai"

    # Count blocked ingredients
    player_blocking = len(ai_recipe & player_items)
    ai_blocking = len(player_recipe & ai_items)

    # Compare blocking
    if player_blocking > ai_blocking:
        return "player"

    if ai_blocking > player_blocking:
        return "ai"

    return "draw"


def make_move(game_state, player, selected_item):

    # Check if the game is already over
    if game_state["game_over"]:
        raise ValueError("The game is already over!")

    # Validate player
    if player not in ("player", "ai"):
        raise ValueError("Invalid player!")

    # Check if the selected item exists on the table
    if selected_item not in game_state["table"]:
        raise ValueError("Selected item is not available on the table!")

    # Check if it is the correct player's turn
    if player != game_state["current_turn"]:
        raise ValueError("It is not this player's turn!")

    # Get the player's moves counter
    moves_key = f"{player}_moves"

    # Check if the player has used all 4 moves
    if game_state[moves_key] >= 4:
        raise ValueError("This player has used all available moves!")

    # Remove the selected item from the table
    game_state["table"].remove(selected_item)

    # Add the item to the player's collected items
    collected_key = f"{player}_items"
    game_state[collected_key].append(selected_item)

    # Increase the player's moves counter
    game_state[moves_key] += 1

    # Check if the player completed the recipe
    recipe_key = f"{player}_recipe"
    required_items = set(game_state[recipe_key]["ingredients"])

    if required_items.issubset(set(game_state[collected_key])):

        game_state["game_over"] = True
        game_state["winner"] = player

    # Check if both players used all 4 moves
    elif (
        game_state["player_moves"] == 4
        and game_state["ai_moves"] == 4
    ):

        game_state["game_over"] = True
        game_state["winner"] = determine_winner(game_state)

    else:

        # Switch turns
        game_state["current_turn"] = (
            "ai" if player == "player" else "player"
        )

    return game_state