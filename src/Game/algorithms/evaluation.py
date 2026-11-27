def evaluate_state(game_state):

    # Get recipes
    ai_recipe = set(game_state["ai_recipe"]["ingredients"])
    player_recipe = set(game_state["player_recipe"]["ingredients"])

    # Get collected ingredients
    ai_items = set(game_state["ai_items"])
    player_items = set(game_state["player_items"])

    # Calculate AI recipe progress
    ai_progress = len(ai_recipe & ai_items)

    # Calculate player recipe progress
    player_progress = len(player_recipe & player_items)

    # Calculate blocking count
    blocking_count = len(player_recipe & ai_items)

    # Calculate evaluation score
    score = (
        (ai_progress * 10)
        - (player_progress * 10)
        + (blocking_count * 5)
    )

    return score