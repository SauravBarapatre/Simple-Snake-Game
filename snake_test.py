import unittest
import random

from snake import GameState


class SnakeGameTests(unittest.TestCase):
    def test_move_forward(self):
        state = GameState.new(10, 10, seed=1)
        head_before = state.snake[0]
        state.step()
        head_after = state.snake[0]
        self.assertEqual(head_after, (head_before[0], head_before[1] + 1))
        self.assertEqual(len(state.snake), 3)

    def test_growth_on_food(self):
        state = GameState.new(10, 10, seed=1)
        head_y, head_x = state.snake[0]
        state.food = (head_y, head_x + 1)
        state.step()
        self.assertEqual(len(state.snake), 4)
        self.assertEqual(state.score, 1)

    def test_wall_collision(self):
        state = GameState.new(5, 5, seed=1)
        state.snake = [(0, 0)]
        state.direction = (-1, 0)
        state.step()
        self.assertFalse(state.alive)

    def test_self_collision(self):
        state = GameState.new(6, 6, seed=1)
        state.snake = [(2, 2), (2, 1), (2, 0), (1, 0), (1, 1), (1, 2)]
        state.direction = (0, -1)
        state.step()
        self.assertFalse(state.alive)

    def test_food_spawns_in_free_cell(self):
        rng = random.Random(1)
        state = GameState(4, 4, rng, [(0, 0)], (0, 1), (0, 0), 0, True)
        food = state.spawn_food()
        self.assertNotIn(food, state.snake)
        self.assertTrue(0 <= food[0] < state.height)
        self.assertTrue(0 <= food[1] < state.width)


if __name__ == "__main__":
    unittest.main()
