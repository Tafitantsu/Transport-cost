from copy import deepcopy
from typing import List, Optional, Tuple, Dict

EPSILON_SS = 1e-6
DEBUG_STEPPING_STONE_VERBOSE = False # Set to False to disable detailed logs by default


def _dfs_build_path(
    matrix: List[List[Optional[float]]],
    r0: int, c0: int,  # The Non-Basic Cell (NBC) we are building a path for
    curr_r: int, curr_c: int, # Current basic cell in the path being built
    path: List[Tuple[int, int]], # Path of basic cells built so far (includes curr_r, curr_c)
    came_from_horizontal: bool # True if the move TO (curr_r, curr_c) was horizontal
) -> Optional[List[Tuple[int, int]]]:
    """
    Recursive DFS to find a Stepping Stone path.
    Path is [p1, p2, ..., pk]. Loop is NBC -> p1 -> ... -> pk -> NBC.
    pk must connect to NBC. k must be odd and >=3.
    """
    n_rows = len(matrix)
    n_cols = len(matrix[0])

    if DEBUG_STEPPING_STONE_VERBOSE:
        print(f"  DFS: At basic ({curr_r},{curr_c}). Path: {path}. From H: {came_from_horizontal}. NBC: ({r0},{c0})")

    if len(path) > n_rows * n_cols : # Max path length guard
        return None

    # Try to complete the loop:
    # The path is the list of *basic* cells. NBC is (r0,c0).
    # Total cells in loop = len(path) + 1. This must be even. So len(path) must be odd.
    # Minimum path length is 3 basic cells (for a 4-cell loop like NBC-p1-p2-p3-NBC).

    # If the last move TO (curr_r, curr_c) was HORIZONTAL, the next (connecting) move is VERTICAL.
    # This means (curr_r, curr_c) must be in the same column as NBC (c0) but a different row (r0).
    if came_from_horizontal:
        if curr_c == c0 and curr_r != r0: # Potential V-closure to NBC
            if len(path) >= 3 and len(path) % 2 == 1:
                if DEBUG_STEPPING_STONE_VERBOSE: print(f"    DFS: Path complete (V-closure)! NBC({r0},{c0}), Path: {path}")
                return list(path)

        # If not complete, explore further VERTICALLY from (curr_r, curr_c)
        for next_r in range(n_rows):
            if next_r == curr_r: continue

            if (matrix[next_r][curr_c] is not None and matrix[next_r][curr_c] > EPSILON_SS / 10) and \
               (next_r, curr_c) not in path: # Must be basic and not already in path
                path.append((next_r, curr_c))
                found_path = _dfs_build_path(matrix, r0, c0, next_r, curr_c, path, False) # Move was vertical
                if found_path:
                    return found_path
                path.pop() # Backtrack

    # If the last move TO (curr_r, curr_c) was VERTICAL, the next (connecting) move is HORIZONTAL.
    # This means (curr_r, curr_c) must be in the same row as NBC (r0) but a different column (c0).
    else: # came_from_vertical
        if curr_r == r0 and curr_c != c0: # Potential H-closure to NBC
            if len(path) >= 3 and len(path) % 2 == 1:
                if DEBUG_STEPPING_STONE_VERBOSE: print(f"    DFS: Path complete (H-closure)! NBC({r0},{c0}), Path: {path}")
                return list(path)

        # If not complete, explore further HORIZONTALLY from (curr_r, curr_c)
        for next_c in range(n_cols):
            if next_c == curr_c: continue

            if (matrix[curr_r][next_c] is not None and matrix[curr_r][next_c] > EPSILON_SS / 10) and \
               (curr_r, next_c) not in path: # Must be basic and not already in path
                path.append((curr_r, next_c))
                found_path = _dfs_build_path(matrix, r0, c0, curr_r, next_c, path, True) # Move was horizontal
                if found_path:
                    return found_path
                path.pop() # Backtrack

    return None


def _find_closed_path(matrix: List[List[Optional[float]]], r0: int, c0: int) -> Optional[List[Tuple[int, int]]]:
    n_rows = len(matrix)
    n_cols = len(matrix[0])
    if DEBUG_STEPPING_STONE_VERBOSE: print(f"\nFinding path for non-basic cell ({r0}, {c0})")

    # Try starting with a horizontal move from NBC (r0,c0) to a basic cell p1 = (r0,c1)
    for c1 in range(n_cols):
        if c1 == c0: continue

        if matrix[r0][c1] is not None and matrix[r0][c1] > EPSILON_SS / 10:
            if DEBUG_STEPPING_STONE_VERBOSE: print(f"  Path Search: Init H from NB({r0},{c0}) to Basic p1=({r0},{c1})")
            path = _dfs_build_path(matrix, r0, c0, r0, c1, [(r0,c1)], True)
            if path: # _dfs_build_path now ensures path validity (len >=3, odd, and correct closure)
                return path

    for r1 in range(n_rows):
        if r1 == r0: continue

        if matrix[r1][c0] is not None and matrix[r1][c0] > EPSILON_SS / 10:
            if DEBUG_STEPPING_STONE_VERBOSE: print(f"  Path Search: Init V from NB({r0},{c0}) to Basic p1=({r1},{c0})")
            path = _dfs_build_path(matrix, r0, c0, r1, c0, [(r1,c0)], False)
            if path:
                return path

    if DEBUG_STEPPING_STONE_VERBOSE: print(f"  No valid path found for NB({r0},{c0})")
    return None

def solve_stepping_stone(initial_solution: Dict, couts: List[List[float]]) -> Dict:
    allocation = deepcopy(initial_solution["allocation"])
    n_rows = len(allocation)
    n_cols = len(allocation[0])

    iteration_count = 0
    MAX_ITERATIONS = (n_rows * n_cols) * 2

    if DEBUG_STEPPING_STONE_VERBOSE:
        cost_val = initial_solution.get('cout_total', 'N/A')
        cost_str = f"{cost_val:.2f}" if isinstance(cost_val, (int, float)) else cost_val
        print(f"Starting Stepping Stone. Initial Allocation (cost: {cost_str}):")
        for r_idx, r_val in enumerate(allocation): print(f"  {r_idx}: {r_val}")

    while iteration_count < MAX_ITERATIONS:
        iteration_count += 1
        if DEBUG_STEPPING_STONE_VERBOSE: print(f"\n--- Iteration {iteration_count} ---")

        most_negative_delta = 0.0
        best_path_info = None

        for r_nb in range(n_rows):
            for c_nb in range(n_cols):
                if allocation[r_nb][c_nb] is None or abs(allocation[r_nb][c_nb] or 0) < EPSILON_SS / 10:
                    path_nodes = _find_closed_path(allocation, r_nb, c_nb)
                    if path_nodes:
                        delta = couts[r_nb][c_nb]
                        current_sign = -1
                        for pr, pc in path_nodes:
                            delta += current_sign * couts[pr][pc]
                            current_sign *= -1

                        if DEBUG_STEPPING_STONE_VERBOSE:
                            print(f"  NB ({r_nb},{c_nb}): Path {path_nodes}, Delta = {delta:.2f}")

                        if delta < most_negative_delta:
                            most_negative_delta = delta
                            best_path_info = (delta, r_nb, c_nb, path_nodes)

        if best_path_info is None or most_negative_delta >= 0: # Changed - (EPSILON_SS / 100) to 0
            if DEBUG_STEPPING_STONE_VERBOSE: print("Solution is optimal or no further improvement found.")
            break

        _, enter_r, enter_c, best_path_nodes = best_path_info
        if DEBUG_STEPPING_STONE_VERBOSE:
            print(f"  Selected for PIVOT: NB ({enter_r},{enter_c}), Path {best_path_nodes}, Delta = {most_negative_delta:.2f}")

        theta = float('inf')
        potential_leaving_cells = []

        for i in range(len(best_path_nodes)):
            if i % 2 == 0:
                pr, pc = best_path_nodes[i]
                alloc_val = allocation[pr][pc]
                if alloc_val is not None:
                   if alloc_val < theta:
                       theta = alloc_val
                       potential_leaving_cells = [(pr, pc)]
                   elif abs(alloc_val - theta) < EPSILON_SS / 100 :
                       potential_leaving_cells.append((pr, pc))

        if DEBUG_STEPPING_STONE_VERBOSE: print(f"  Theta = {theta}, Potential leaving cells: {potential_leaving_cells}")

        if theta == float('inf'):
            if DEBUG_STEPPING_STONE_VERBOSE: print(f"Critical Error: Theta is infinity. Path was {best_path_nodes}. Allocations in path: {[allocation[pr][pc] for pr,pc in best_path_nodes]}. Halting.")
            break

        if DEBUG_STEPPING_STONE_VERBOSE:
            if abs(theta) < EPSILON_SS / 10 and abs(theta) > 1e-9 and not (abs(theta - EPSILON_SS) < EPSILON_SS /10):
                 print(f"Note: Theta ({theta}) is very small (degenerate pivot).")
            elif abs(theta - EPSILON_SS) < EPSILON_SS /10 :
                 print(f"Note: Theta ({theta}) is an EPSILON value (degenerate pivot).")
            elif abs(theta) < 1e-9 :
                 print(f"Note: Theta ({theta}) is effectively zero (degenerate pivot, basis change without flow change).")

        if DEBUG_STEPPING_STONE_VERBOSE: print(f"  Updating allocation. Entering ({enter_r},{enter_c}) gets +{theta}")
        allocation[enter_r][enter_c] = (allocation[enter_r][enter_c] or 0) + theta

        for i in range(len(best_path_nodes)):
            pr, pc = best_path_nodes[i]
            current_cell_val_before_update_in_this_pivot = allocation[pr][pc]

            if i % 2 == 0: # Decrease allocation
                new_val = (current_cell_val_before_update_in_this_pivot or 0) - theta
                allocation[pr][pc] = new_val
            else: # Increase allocation
                new_val = (current_cell_val_before_update_in_this_pivot or 0) + theta
                allocation[pr][pc] = new_val

        if potential_leaving_cells:
            potential_leaving_cells.sort()
            leaving_r, leaving_c = potential_leaving_cells[0]

            if abs(allocation[leaving_r][leaving_c] or 0) < EPSILON_SS / 10:
                 allocation[leaving_r][leaving_c] = None
                 if DEBUG_STEPPING_STONE_VERBOSE: print(f"  Cell ({leaving_r},{leaving_c}) is leaving basis (set to None). Original value was ~{theta:.2f}")
            elif DEBUG_STEPPING_STONE_VERBOSE:
                print(f"  Warning: Candidate leaving cell ({leaving_r},{leaving_c}) did not become zero (value: {allocation[leaving_r][leaving_c]}). Theta was {theta}. Check logic.")
        elif theta > EPSILON_SS / 100 :
             if DEBUG_STEPPING_STONE_VERBOSE: print(f"  Warning: Theta was {theta:.2f} but no potential leaving cells were identified. Check theta calculation or path basic cells.")

        if DEBUG_STEPPING_STONE_VERBOSE:
            print(f"  Allocation after iteration {iteration_count}:")
            for r_idx, r_val in enumerate(allocation): print(f"    {r_idx}: {[f'{x:.2f}' if x is not None else ' None ' for x in r_val]}")

    final_cout_total = 0
    for r_idx in range(n_rows):
        for c_idx in range(n_cols):
            val = allocation[r_idx][c_idx]
            if val is not None and val > 0: # Changed EPSILON_SS to 0
                final_cout_total += val * couts[r_idx][c_idx]

    rounded_final_cout_total = round(final_cout_total, 2)
    if DEBUG_STEPPING_STONE_VERBOSE: print(f"\nStepping Stone finished. Final cost: {rounded_final_cout_total:.2f} (original: {final_cout_total})")
    return {
        "allocation": allocation,
        "cout_total": rounded_final_cout_total
    }
