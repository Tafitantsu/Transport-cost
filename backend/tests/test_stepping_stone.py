import unittest
from unittest.mock import patch
import sys
import os
from copy import deepcopy

# Adjust path to import solvers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solvers.stepping_stone import solve_stepping_stone, _find_closed_path, EPSILON_SS
from solvers.cno import solve_coin_nord_ouest

# Set to True to see extensive logs from the solver during tests
DEBUG_SOLVER_LOGS = False # Set to False for cleaner default test output
if DEBUG_SOLVER_LOGS:
    # This is a bit of a hack to enable debug prints in the solver module
    # by modifying its global variable before tests run.
    import solvers.stepping_stone as ss_module
    ss_module.DEBUG_STEPPING_STONE_VERBOSE = True
else: # Ensure it's off if not explicitly on for tests
    import solvers.stepping_stone as ss_module
    if hasattr(ss_module, 'DEBUG_STEPPING_STONE_VERBOSE'): # Check if attr exists
        ss_module.DEBUG_STEPPING_STONE_VERBOSE = False


class TestSteppingStoneSolver(unittest.TestCase):

    def assertPathContainsSameNodes(self, found_path, expected_path_nodes, msg=None):
        if found_path is None and expected_path_nodes is None:
            return # Both None is OK
        if found_path is None or expected_path_nodes is None:
            self.fail(f"Path mismatch: one is None, other is not. Found: {found_path}, Expected: {expected_path_nodes}. {msg or ''}")

        self.assertEqual(len(found_path), len(expected_path_nodes),
                         f"Path lengths differ. Found {len(found_path)}: {found_path}, Expected {len(expected_path_nodes)}: {expected_path_nodes}. {msg or ''}")

        # Check if all expected nodes are in found_path (order doesn't strictly matter for this helper)
        # For actual delta calculation, order is critical and must match the +/- sequence.
        # This helper is more for "did it find the right set of cells for the loop".
        for node in expected_path_nodes:
            self.assertIn(node, found_path, f"Node {node} from expected not in found path {found_path}. {msg or ''}")
        # And vice-versa (redundant if lengths are same, but good check)
        for node in found_path:
            self.assertIn(node, expected_path_nodes, f"Node {node} from found path not in expected {expected_path_nodes}. {msg or ''}")


    def test_find_closed_path_2x2_simple(self):
        """Test _find_closed_path for a simple 2x2 matrix."""
        # Matrix:
        #  10   N    (N at 0,1)
        #   5  15
        matrix = [[10.0, None], [5.0, 15.0]]
        r_nb, c_nb = 0, 1 # Non-basic cell

        # Expected loop: (0,1)+ -> (0,0)- -> (1,0)+ -> (1,1)-
        # Path of basic cells, order matters for delta:
        # Start H from (0,1) to (0,0). Path node 1: (0,0)
        # From (0,0) V to (1,0). Path node 2: (1,0)
        # From (1,0) H to (1,1) to complete with (0,1)'s column. Path node 3: (1,1)
        # Expected path list: [(0,0), (1,0), (1,1)] (sign pattern for delta: -, +, -)
        expected_path = [(0,0), (1,0), (1,1)]

        found_path = _find_closed_path(matrix, r_nb, c_nb)
        self.assertIsNotNone(found_path, f"Expected a path for NB({r_nb},{c_nb}), got None.")
        if found_path: # To satisfy type checker and proceed
             self.assertListEqual(found_path, expected_path,
                                 f"Path for NB({r_nb},{c_nb}) incorrect. Got: {found_path}, Expected: {expected_path}")

    def test_find_closed_path_2x2_alternate_nb(self):
        """Test _find_closed_path for the other non-basic cell in a 2x2 matrix."""
        # Matrix:
        #  10   5
        #   N  15    (N at 1,0)
        matrix = [[10.0, 5.0], [None, 15.0]]
        r_nb, c_nb = 1, 0 # Non-basic cell

        # Expected loop: (1,0)+ -> (1,1)- -> (0,1)+ -> (0,0)-
        # Path of basic cells, order for delta: [(1,1), (0,1), (0,0)]
        expected_path = [(1,1), (0,1), (0,0)]

        found_path = _find_closed_path(matrix, r_nb, c_nb)
        self.assertIsNotNone(found_path, f"Expected a path for NB({r_nb},{c_nb}), got None.")
        if found_path:
            self.assertListEqual(found_path, expected_path,
                                 f"Path for NB({r_nb},{c_nb}) incorrect. Got: {found_path}, Expected: {expected_path}")


    def test_find_closed_path_no_path(self):
        """Test case where no closed path exists."""
        matrix = [[10.0, None], [None, None]] # NB at (0,1)
        r_nb, c_nb = 0, 1
        found_path = _find_closed_path(matrix, r_nb, c_nb)
        self.assertIsNone(found_path, f"Expected no path for NB({r_nb},{c_nb}), but got {found_path}")

        matrix_disconnected = [[10.0, None, None], [None, 20.0, None], [None, None, 30.0]]
        r_nb_disc, c_nb_disc = 0, 1 # Non-basic cell
        found_path_disc = _find_closed_path(matrix_disconnected, r_nb_disc, c_nb_disc)
        self.assertIsNone(found_path_disc, f"Expected no path for disconnected NB({r_nb_disc},{c_nb_disc}), but got {found_path_disc}")


    def test_find_closed_path_with_epsilon(self):
        """Test path finding where an EPSILON value is part of the path."""
        matrix = [[10.0, None], [EPSILON_SS, 20.0]] # NB at (0,1)
        r_nb, c_nb = 0, 1
        # Expected path for (0,1): [(0,0), (1,0), (1,1)] (EPSILON_SS at (1,0) is basic)
        expected_path = [(0,0), (1,0), (1,1)]
        found_path = _find_closed_path(matrix, r_nb, c_nb)
        self.assertIsNotNone(found_path, f"Expected a path with Epsilon for NB({r_nb},{c_nb}), got None.")
        if found_path:
            self.assertListEqual(found_path, expected_path,
                                 f"Path with Epsilon for NB({r_nb},{c_nb}) incorrect. Got: {found_path}, Expected: {expected_path}")

    def test_find_closed_path_2x3_simple(self):
        """Test a 2x3 matrix path."""
        # Matrix:
        #  10   N  20   (N at 0,1)
        #  N    5  30
        matrix = [[10.0, None, 20.0], [None, 5.0, 30.0]]
        r_nb, c_nb = 0, 1
        # Path for (0,1)+ -> (0,2)- -> (1,2)+ -> (1,1)-
        # Basic cells: [(0,2), (1,2), (1,1)]
        expected_path = [(0,2), (1,2), (1,1)]
        found_path = _find_closed_path(matrix, r_nb, c_nb)
        self.assertIsNotNone(found_path, f"Expected path for 2x3 NB({r_nb},{c_nb}), got None.")
        if found_path:
            self.assertListEqual(found_path, expected_path,
                                 f"Path for 2x3 NB({r_nb},{c_nb}) incorrect. Got: {found_path}, Expected: {expected_path}")


    def calculate_expected_cost(self, allocation, costs):
        total_cost = 0
        if allocation is None:
            return 0
        for r in range(len(allocation)):
            for c in range(len(allocation[0])):
                val = allocation[r][c]
                if val is not None and val > 0: # Changed EPSILON_SS to 0
                    total_cost += val * costs[r][c]
        return total_cost

    # Keep the integration tests, but they will now use the real _find_closed_path
    # @patch('solvers.stepping_stone._find_closed_path') # Remove patch for integration tests
    def test_optimal_solution_already(self): # Renamed, no mock
        """
        Test case where the initial solution is already optimal.
        Uses real _find_closed_path.
        """
        # Example known to be optimal or very simple
        offres = [10, 20]
        demandes = [15, 15]
        couts = [[1, 2], [3, 1]] # Optimal: [[0,10],[15,5]] Cost: 10*2 + 15*3 + 5*1 = 20+45+5 = 70
                                 # CNO: [[10,N],[5,10]] Cost: 10*1 + 5*3 + 10*1 = 10+15+10=35
                                 # This CNO example is optimal for these costs.

        initial_solution_cno = solve_coin_nord_ouest(offres.copy(), demandes.copy(), couts)
        # CNO for this: [[10,None],[5,10]] (if demands were [15,10])
        # For demands [15,15]: CNO [[10,N],[5,15]] (3 allocs, (0,1) is NB)
        # Cost: 10*1 + 5*3 + 15*1 = 10+15+15=40
        # Let's use this CNO result:
        initial_alloc = initial_solution_cno["allocation"] # [[10.0, None], [5.0, 15.0]]
        initial_cost = self.calculate_expected_cost(initial_alloc, couts) # 40.0

        initial_solution_dict = {
            "allocation": deepcopy(initial_alloc),
            "cout_total": initial_cost
        }

        # Temporarily enable verbose logging for this specific test if needed for debugging pathfinder
        # global DEBUG_SOLVER_LOGS, ss_module # if you want to toggle it here
        # original_debug_flag = ss_module.DEBUG_STEPPING_STONE_VERBOSE
        # ss_module.DEBUG_STEPPING_STONE_VERBOSE = True

        optimized_result = solve_stepping_stone(initial_solution_dict, couts)

        # ss_module.DEBUG_STEPPING_STONE_VERBOSE = original_debug_flag # Restore

        self.assertIsNotNone(optimized_result["allocation"])
        # For an optimal solution, allocation should not change
        for r_idx in range(len(initial_alloc)):
            for c_idx in range(len(initial_alloc[0])):
                expected_val = initial_alloc[r_idx][c_idx]
                actual_val = optimized_result["allocation"][r_idx][c_idx]
                if expected_val is None:
                    self.assertIsNone(actual_val, f"Cell ({r_idx},{c_idx}) should be None, got {actual_val}")
                else:
                    self.assertIsNotNone(actual_val, f"Cell ({r_idx},{c_idx}) should not be None if expected was {expected_val}")
                    self.assertAlmostEqual(expected_val, actual_val, places=5, msg=f"Cell ({r_idx},{c_idx})")

        self.assertAlmostEqual(initial_cost, optimized_result["cout_total"], places=5,
                             msg="Cost should not change for an already optimal solution.")


    def test_single_iteration_improvement_real_pathfinder(self):
        """
        Test a single iteration improvement using the actual _find_closed_path.
        """
        initial_alloc_matrix = [[10.0, 20.0], [None, 20.0]]
        costs_for_improvement = [[5.0,1.0],[1.0,5.0]]
        # Non-basic cell (1,0). Expected path: [(0,0), (0,1), (1,1)]
        # Delta for (1,0): C[1][0]-C[0][0]+C[0][1]-C[1][1] = 1-5+1-5 = -8.

        initial_solution_dict = {
            "allocation": deepcopy(initial_alloc_matrix),
            "cout_total": self.calculate_expected_cost(initial_alloc_matrix, costs_for_improvement) # Should be 170
        }

        # original_debug_flag = ss_module.DEBUG_STEPPING_STONE_VERBOSE
        # ss_module.DEBUG_STEPPING_STONE_VERBOSE = True
        optimized_result = solve_stepping_stone(initial_solution_dict, costs_for_improvement)
        # ss_module.DEBUG_STEPPING_STONE_VERBOSE = original_debug_flag

        # Expected after one iteration with theta=10 (from cell (0,0) which has 10):
        # (1,0) gets +10 --> alloc[1][0] = 10
        # (0,0) gets -10 --> alloc[0][0] = 0 (becomes None)
        # (0,1) gets +10 --> alloc[0][1] = 30
        # (1,1) gets -10 --> alloc[1][1] = 10
        expected_allocation_after_one_step = [[None, 30.0], [10.0, 10.0]]
        expected_cost_after_one_step = self.calculate_expected_cost(expected_allocation_after_one_step, costs_for_improvement) # Should be 90.0

        self.assertIsNotNone(optimized_result["allocation"], "Result allocation is None")
        for r_idx in range(len(expected_allocation_after_one_step)):
            for c_idx in range(len(expected_allocation_after_one_step[0])):
                expected_val = expected_allocation_after_one_step[r_idx][c_idx]
                actual_val = optimized_result["allocation"][r_idx][c_idx]
                try:
                    if expected_val is None:
                        self.assertIsNone(actual_val, f"Cell ({r_idx},{c_idx}) expected None, got {actual_val}")
                    else:
                        self.assertIsNotNone(actual_val, f"Cell ({r_idx},{c_idx}) expected {expected_val}, got None")
                        self.assertAlmostEqual(expected_val, actual_val, places=5, msg=f"Cell ({r_idx},{c_idx})")
                except AssertionError as e:
                    print("\n---- DEBUG: Test Failed in test_single_iteration_improvement_real_pathfinder ----")
                    print(f"Failed assertion: {e}")
                    print("Expected Allocation (after one step):")
                    for row_print in expected_allocation_after_one_step:
                        print([f"{x:.2f}" if x is not None else "None" for x in row_print])
                    print("Actual Allocation from Solver:")
                    for row_print in optimized_result["allocation"]:
                        print([f"{x:.2f}" if x is not None else "None" for x in row_print])
                    print(f"Actual Total Cost from Solver: {optimized_result['cout_total']:.2f}")
                    print(f"DEBUG SS Info: Initial alloc for solver: {initial_solution_dict['allocation']}")
                    print("---- END DEBUG ----")
                    raise e

        self.assertAlmostEqual(expected_cost_after_one_step, optimized_result["cout_total"], places=5)

if __name__ == '__main__':
    # To run with verbose solver logs, set DEBUG_SOLVER_LOGS = True at the top
    # Or, from command line:
    # DEBUG_STEPPING_STONE_VERBOSE=True python -m unittest backend.tests.test_stepping_stone
    unittest.main()
