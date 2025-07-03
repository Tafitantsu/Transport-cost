from copy import deepcopy

EPSILON = 1e-6 # Define a small epsilon value

def solve_hammer(offres, demandes, couts):
    offres_orig = offres[:] # Keep original for reference if needed
    demandes_orig = demandes[:] # Keep original for reference if needed

    # Work with copies for modification during allocation
    current_offres = offres[:]
    current_demandes = demandes[:]

    costs = deepcopy(couts)

    n, m = len(offres_orig), len(demandes_orig)
    allocation = [[None for _ in range(m)] for _ in range(n)]
    total_cost = 0
    num_allocations = 0

    # Keep track of available rows and columns for penalty calculation
    active_rows = list(range(n))
    active_cols = list(range(m))

    while active_rows and active_cols:
        penalties = []

        # Calculate row penalties
        for i in active_rows:
            row_costs_available = [costs[i][j] for j in active_cols]
            if not row_costs_available: continue # Should not happen if active_cols is managed correctly
            if len(row_costs_available) >= 2:
                sorted_row = sorted(row_costs_available)
                penalty = sorted_row[1] - sorted_row[0]
            elif len(row_costs_available) == 1:
                penalty = row_costs_available[0] # Or some large value to prioritize it
            else: # No costs available for this row among active columns
                penalty = -float('inf') # Should not be chosen
            penalties.append(('row', i, penalty))

        # Calculate column penalties
        for j in active_cols:
            col_costs_available = [costs[i][j] for i in active_rows]
            if not col_costs_available: continue
            if len(col_costs_available) >= 2:
                sorted_col = sorted(col_costs_available)
                penalty = sorted_col[1] - sorted_col[0]
            elif len(col_costs_available) == 1:
                penalty = col_costs_available[0]
            else:
                penalty = -float('inf')
            penalties.append(('col', j, penalty))

        if not penalties: # No more valid penalties to calculate
            break

        # Select the largest penalty
        # Sort by penalty (desc), then by cost (asc) for tie-breaking, then by index for stability
        penalties.sort(key=lambda x: (-x[2]))

        # Find best cell in the selected row/column
        best_penalty_type, best_penalty_index, _ = penalties[0]

        selected_i, selected_j = -1, -1

        if best_penalty_type == 'row':
            selected_i = best_penalty_index
            # Find cell with min cost in this row among active columns
            min_row_cost = float('inf')
            for j_col in active_cols:
                if costs[selected_i][j_col] < min_row_cost:
                    min_row_cost = costs[selected_i][j_col]
                    selected_j = j_col
        else: # 'col'
            selected_j = best_penalty_index
            # Find cell with min cost in this col among active rows
            min_col_cost = float('inf')
            for i_row in active_rows:
                if costs[i_row][selected_j] < min_col_cost:
                    min_col_cost = costs[i_row][selected_j]
                    selected_i = i_row

        if selected_i == -1 or selected_j == -1 : # No valid cell found
             # This might happen if all remaining costs are infinity or lists are empty
             # Or if a row/column was exhausted but not removed due to simultaneous exhaustion
             break


        qte = min(current_offres[selected_i], current_demandes[selected_j])

        if qte > 0: # Process actual allocation
            allocation[selected_i][selected_j] = qte
            total_cost += qte * costs[selected_i][selected_j]
            num_allocations += 1

        current_offres[selected_i] -= qte
        current_demandes[selected_j] -= qte

        # Remove row or column if supply/demand is met
        if current_offres[selected_i] == 0 and selected_i in active_rows:
            active_rows.remove(selected_i)
        if current_demandes[selected_j] == 0 and selected_j in active_cols:
            active_cols.remove(selected_j)

    # Degeneracy handling
    required_allocations = n + m - 1

    while num_allocations < required_allocations:
        best_cell_to_add_epsilon = None
        min_cost_for_epsilon = float('inf')

        for r in range(n):
            for c in range(m):
                if allocation[r][c] is None: # If cell is empty
                    # Simple strategy: pick the unused cell with the lowest cost.
                    if costs[r][c] < min_cost_for_epsilon:
                        min_cost_for_epsilon = costs[r][c]
                        best_cell_to_add_epsilon = (r, c)

        if best_cell_to_add_epsilon:
            r_deg, c_deg = best_cell_to_add_epsilon
            allocation[r_deg][c_deg] = EPSILON
            # Do not add EPSILON * costs[r_deg][c_deg] to total_cost for degeneracy handling
            num_allocations += 1
        else:
            # No suitable empty cell found, break to avoid infinite loop
            break

    return {
        "allocation": allocation,
        "cout_total": total_cost
    }
