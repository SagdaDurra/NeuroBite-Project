# Task F: Evaluation Function

## 1. Overview

The Evaluation Function is used to evaluate the current game state and measure how favorable it is for the AI player.

It calculates a numerical score based on the AI's recipe progress, the player's recipe progress, and the AI's ability to block the opponent.

A positive score indicates an advantage for the AI, while a negative score indicates an advantage for the player.

## 2. Evaluation Factors

The function considers three main factors:

### 2.1 AI Recipe Progress (+10)

The AI receives 10 points for each ingredient it collects that belongs to its own recipe.

### 2.2 Opponent Recipe Progress (-10)

The AI loses 10 points for each ingredient the player collects that belongs to the player's recipe.

This penalizes game states where the opponent is closer to completing their recipe.

### 2.3 Blocking Bonus (+5)

The AI receives 5 bonus points for each ingredient it collects that belongs to the player's recipe.

This rewards the AI for preventing the opponent from collecting ingredients they need.

## 3. Evaluation Formula

The evaluation score is calculated using the following formula:

```text
Evaluation Score =
    (AI Progress × 10)
  - (Player Progress × 10)
  + (Blocking Count × 5)
```

## 4. Implementation

The function is implemented in:

`src/Game/algorithms/evaluation.py`

Function name:

`evaluate_state(game_state)`

The function performs the following steps:

1. Extracts the AI and player recipes.
2. Retrieves the ingredients collected by both players.
3. Calculates the AI's recipe progress.
4. Calculates the player's recipe progress.
5. Calculates the blocking count.
6. Applies the evaluation formula.
7. Returns the final numerical score.

## 5. Example

Consider the following game state:

- AI Recipe: chicken, rice, water
- Player Recipe: pasta, milk, cheese
- AI Collected Ingredients: chicken, cheese
- Player Collected Ingredients: pasta, milk

Calculations:

- AI Progress = 1 → 1 × 10 = +10
- Player Progress = 2 → 2 × 10 = -20
- Blocking Count = 1 → 1 × 5 = +5

Final Score:

```text
10 - 20 + 5 = -5
```

The result is -5, which indicates that the current game state favors the player.

## 6. Integration

The Evaluation Function is designed to support the Minimax algorithm with Alpha-Beta Pruning in Task G.

It provides a numerical score that helps the AI compare possible game states and select better moves.

## 7. Conclusion

The Evaluation Function helps the AI make strategic decisions by rewarding recipe progress, penalizing opponent progress, and encouraging blocking actions.