import unittest

from src.Game.game import (
    create_game_state,
    make_move,
    determine_winner
)


class TestGame(unittest.TestCase):

    def setUp(self):

        self.game_state = {
            "player_recipe": {
                "ingredients": ("chicken", "rice", "water")
            },
            "ai_recipe": {
                "ingredients": ("pasta", "milk", "cheese")
            },
            "table": [
                "chicken", "rice", "water",
                "pasta", "milk", "cheese",
                "tomato", "beef"
            ],
            "player_items": [],
            "ai_items": [],
            "player_moves": 0,
            "ai_moves": 0,
            "current_turn": "player",
            "game_over": False,
            "winner": None
        }

    # Test 1: Create game state
    def test_create_game_state(self):

        game = create_game_state()

        self.assertEqual(len(game["table"]), 8)
        self.assertEqual(len(set(game["table"])), 8)

        self.assertEqual(len(game["player_recipe"]["ingredients"]), 3)
        self.assertEqual(len(game["ai_recipe"]["ingredients"]), 3)

        self.assertEqual(game["current_turn"], "player")
        self.assertFalse(game["game_over"])

    # Test 2: Valid move
    def test_valid_move(self):

        make_move(self.game_state, "player", "chicken")

        self.assertNotIn("chicken", self.game_state["table"])
        self.assertIn("chicken", self.game_state["player_items"])

        self.assertEqual(self.game_state["player_moves"], 1)
        self.assertEqual(self.game_state["current_turn"], "ai")

    # Test 3: Invalid item
    def test_invalid_item(self):

        with self.assertRaises(ValueError):
            make_move(self.game_state, "player", "pizza")

    # Test 4: Wrong turn
    def test_wrong_turn(self):

        with self.assertRaises(ValueError):
            make_move(self.game_state, "ai", "pasta")

    # Test 5: Immediate win
    def test_immediate_win(self):

        make_move(self.game_state, "player", "chicken")
        make_move(self.game_state, "ai", "pasta")

        make_move(self.game_state, "player", "rice")
        make_move(self.game_state, "ai", "milk")

        make_move(self.game_state, "player", "water")

        self.assertTrue(self.game_state["game_over"])
        self.assertEqual(self.game_state["winner"], "player")

    # Test 6: Determine winner by progress
    def test_winner_by_progress(self):

        self.game_state["player_items"] = ["chicken", "rice"]
        self.game_state["ai_items"] = ["pasta"]

        winner = determine_winner(self.game_state)

        self.assertEqual(winner, "player")

    # Test 7: Determine winner by blocking
    def test_winner_by_blocking(self):

        self.game_state["player_items"] = ["chicken", "pasta"]
        self.game_state["ai_items"] = ["milk"]

        winner = determine_winner(self.game_state)

        self.assertEqual(winner, "player")

    # Test 8: Draw
    def test_draw(self):

        self.game_state["player_items"] = [
            "chicken", "rice", "pasta", "tomato"
        ]

        self.game_state["ai_items"] = [
            "milk", "cheese", "water", "beef"
        ]

        winner = determine_winner(self.game_state)

        self.assertEqual(winner, "draw")

    # Test 9: Shared ingredient
    def test_shared_ingredient(self):

        self.game_state["player_recipe"]["ingredients"] = (
            "chicken", "rice", "garlic"
        )

        self.game_state["ai_recipe"]["ingredients"] = (
            "pasta", "milk", "garlic"
        )

        make_move(self.game_state, "player", "garlic")

        self.assertIn("garlic", self.game_state["player_items"])
        self.assertNotIn("garlic", self.game_state["table"])
        self.assertEqual(self.game_state["player_moves"], 1)

    # Test 10: Neutral ingredient
    def test_neutral_ingredient(self):

        make_move(self.game_state, "player", "tomato")

        self.assertIn("tomato", self.game_state["player_items"])

        player_recipe = set(
            self.game_state["player_recipe"]["ingredients"]
        )

        self.assertNotIn("tomato", player_recipe)

    # Test 11: Game ends after all moves
    def test_game_ends_after_all_moves(self):

        make_move(self.game_state, "player", "chicken")
        make_move(self.game_state, "ai", "milk")

        make_move(self.game_state, "player", "rice")
        make_move(self.game_state, "ai", "cheese")

        make_move(self.game_state, "player", "pasta")
        make_move(self.game_state, "ai", "water")

        make_move(self.game_state, "player", "tomato")
        make_move(self.game_state, "ai", "beef")

        self.assertTrue(self.game_state["game_over"])
        self.assertEqual(self.game_state["winner"], "draw")

    # Test 12: Move after game over
    def test_move_after_game_over(self):

        self.game_state["game_over"] = True

        with self.assertRaises(ValueError):
            make_move(self.game_state, "player", "chicken")


if __name__ == "__main__":
    unittest.main()