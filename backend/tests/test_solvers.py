import unittest
import sys
import os

# Adjust path to import solvers from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solvers.cno import solve_coin_nord_ouest, EPSILON as CNO_EPSILON
from solvers.hammer import solve_hammer, EPSILON as HAMMER_EPSILON

class TestDegeneracyHandling(unittest.TestCase):

    def count_allocations(self, allocation_matrix):
        count = 0
        has_epsilon = False
        if allocation_matrix is None:
            return 0, False

        for r in range(len(allocation_matrix)):
            for c in range(len(allocation_matrix[0])):
                if allocation_matrix[r][c] is not None and allocation_matrix[r][c] > 1e-9: # Check against small float, not just not None
                    count += 1
                    # Using a direct comparison for epsilon here is okay as we set it explicitly
                    if abs(allocation_matrix[r][c] - CNO_EPSILON) < 1e-9 or \
                       abs(allocation_matrix[r][c] - HAMMER_EPSILON) < 1e-9:
                        has_epsilon = True
        return count, has_epsilon

    def test_cno_degenerate_case(self):
        offres = [20, 30]
        demandes = [20, 30]
        couts = [[1, 2], [3, 4]] # n=2, m=2
        n = len(offres)
        m = len(demandes)
        required_allocations = n + m - 1 # Should be 3

        result = solve_coin_nord_ouest(offres, demandes, couts)
        allocation_matrix = result["allocation"]

        num_actual_allocations, has_epsilon = self.count_allocations(allocation_matrix)

        print(f"\nCNO Degenerate Test:")
        print(f"Offres: {offres}, Demandes: {demandes}")
        print(f"Allocation Matrix: {allocation_matrix}")
        print(f"Number of allocations: {num_actual_allocations}, Required: {required_allocations}")
        print(f"Has Epsilon: {has_epsilon}")

        self.assertEqual(num_actual_allocations, required_allocations, "CNO: Incorrect number of allocations for degenerate case.")
        self.assertTrue(has_epsilon, "CNO: Epsilon allocation was not made for degenerate case.")
        # Expected cost: (20 * 1) + (30 * 4) = 20 + 120 = 140
        expected_cost_cno_degenerate = (20 * 1) + (30 * 4)
        self.assertAlmostEqual(result["cout_total"], expected_cost_cno_degenerate, places=5, msg="CNO: Incorrect total cost for degenerate case.")

    def test_hammer_degenerate_case(self):
        offres = [20, 30]
        demandes = [20, 30]
        couts = [[1, 2], [3, 4]] # n=2, m=2
        n = len(offres)
        m = len(demandes)
        required_allocations = n + m - 1 # Should be 3

        result = solve_hammer(offres, demandes, couts)
        allocation_matrix = result["allocation"]

        num_actual_allocations, has_epsilon = self.count_allocations(allocation_matrix)

        print(f"\nHammer Degenerate Test:")
        print(f"Offres: {offres}, Demandes: {demandes}")
        print(f"Allocation Matrix: {allocation_matrix}")
        print(f"Number of allocations: {num_actual_allocations}, Required: {required_allocations}")
        print(f"Has Epsilon: {has_epsilon}")
        print(f"Total Cost: {result['cout_total']}")

        self.assertEqual(num_actual_allocations, required_allocations, "Hammer: Incorrect number of allocations for degenerate case.")
        self.assertTrue(has_epsilon, "Hammer: Epsilon allocation was not made for degenerate case.")
        # Expected cost: (20 * 1) + (30 * 4) = 140 (assuming same allocation path as CNO for this simple case if epsilon is placed in (0,1))
        # Or, if Hammer places epsilon elsewhere, the cost would be based on the two main allocations.
        # Let's re-calculate based on what Hammer usually does:
        # Penalties: Row0: 2-1=1, Row1: 4-3=1. Col0: 3-1=2, Col1: 4-2=2.
        # Max penalty is 2. Say Col0. Min cost in Col0 is 1 at (0,0). Allocate 20.
        # offres_copy = [0,30], demandes_copy = [0,30]. Cell (0,0)=20.
        # This is degenerate. Remaining is 30 for (1,1).
        # So allocation [[20, EPSILON], [None, 30]] or [[20, None], [EPSILON, 30]]
        # Cost should be 20*couts[0][0] + 30*couts[1][1] = 20*1 + 30*4 = 140
        expected_cost_hammer_degenerate = (20 * 1) + (30 * 4)
        self.assertAlmostEqual(result["cout_total"], expected_cost_hammer_degenerate, places=5, msg="Hammer: Incorrect total cost for degenerate case.")


    def test_cno_larger_degenerate_case(self):
        offres = [50, 60, 40] # n=3
        demandes = [30, 70, 50] # m=3
        couts = [[2, 3, 4], [3, 2, 5], [4, 3, 2]]
        # Total supply = 150, Total demand = 150
        n = len(offres)
        m = len(demandes)
        required_allocations = n + m - 1 # 3 + 3 - 1 = 5

        result = solve_coin_nord_ouest(offres, demandes, couts)
        allocation_matrix = result["allocation"]
        num_actual_allocations, has_epsilon = self.count_allocations(allocation_matrix)

        print(f"\nCNO Larger Degenerate Test:")
        print(f"Offres: {offres}, Demandes: {demandes}")
        print(f"Allocation Matrix: {allocation_matrix}")
        print(f"Number of allocations: {num_actual_allocations}, Required: {required_allocations}")
        print(f"Has Epsilon: {has_epsilon}")

        # This specific case might or might not be degenerate with CNO without epsilon.
        # The key is that if it IS degenerate, epsilon should be added.
        # If it's not degenerate naturally, then num_actual_allocations should still be n+m-1 and has_epsilon would be False.
        # The current implementation of adding epsilon *always* tries to reach n+m-1.
        self.assertEqual(num_actual_allocations, required_allocations, f"CNO Larger: Expected {required_allocations} allocations, got {num_actual_allocations}")
        # Cost = 30*2 + 20*3 + 50*2 + 10*5 + 40*2 = 60 + 60 + 100 + 50 + 80 = 350
        # This case did not have epsilon, so cost calculation is direct.
        expected_cost_cno_larger = (30*2) + (20*3) + (50*2) + (10*5) + (40*2)
        self.assertAlmostEqual(result["cout_total"], expected_cost_cno_larger, places=5, msg="CNO Larger: Incorrect total cost.")
        # If it were degenerate and epsilon was added, the assertion for has_epsilon would be:
        # if result["cout_total"] implies fewer than n+m-1 "real" allocations, self.assertTrue(has_epsilon)
        # However, the current logic is that num_actual_allocations includes epsilon if added.


    def test_hammer_larger_degenerate_case(self):
        offres = [50, 60, 40] # n=3
        demandes = [30, 70, 50] # m=3
        couts = [[2, 3, 4], [3, 2, 5], [4, 3, 2]]
        n = len(offres)
        m = len(demandes)
        required_allocations = n + m - 1 # 5

        result = solve_hammer(offres, demandes, couts)
        allocation_matrix = result["allocation"]
        num_actual_allocations, has_epsilon = self.count_allocations(allocation_matrix)

        print(f"\nHammer Larger Degenerate Test:")
        print(f"Offres: {offres}, Demandes: {demandes}")
        print(f"Allocation Matrix: {allocation_matrix}")
        print(f"Number of allocations: {num_actual_allocations}, Required: {required_allocations}")
        print(f"Has Epsilon: {has_epsilon}")
        print(f"Total Cost: {result['cout_total']}")

        self.assertEqual(num_actual_allocations, required_allocations, f"Hammer Larger: Expected {required_allocations} allocations, got {num_actual_allocations}")
        # Cost = 30*2 + 10*3 + 10*4 + 60*2 + 40*2 = 60 + 30 + 40 + 120 + 80 = 330
        # This case also did not have epsilon, so cost calculation is direct.
        expected_cost_hammer_larger = (30*2) + (10*3) + (10*4) + (60*2) + (40*2)
        self.assertAlmostEqual(result["cout_total"], expected_cost_hammer_larger, places=5, msg="Hammer Larger: Incorrect total cost.")
        # Similar logic to CNO's larger test for has_epsilon.

if __name__ == '__main__':
    unittest.main()
