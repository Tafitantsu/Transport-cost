from copy import deepcopy

EPSILON = 1e-6 # Define a small epsilon value

def solve_coin_nord_ouest(offres, demandes, couts):
    n = len(offres)
    m = len(demandes)
    allocation = [[None for _ in range(m)] for _ in range(n)]

    offres_copy = offres.copy()
    demandes_copy = demandes.copy()

    i, j = 0, 0
    total_cost = 0
    num_allocations = 0

    # Main allocation loop
    while i < n and j < m:
        qte = min(offres_copy[i], demandes_copy[j])

        if qte > 0: # Only count actual allocations
            allocation[i][j] = qte
            total_cost += qte * couts[i][j]
            num_allocations += 1

        offres_copy[i] -= qte
        demandes_copy[j] -= qte

        if offres_copy[i] == 0 and demandes_copy[j] == 0 and i < n - 1 and j < m - 1:
            # This is a potential point of degeneracy if we simply move i+1, j+1
            # For Northwest corner, the standard approach is to proceed,
            # and then fix degeneracy if it occurs.
            # However, to be more explicit, if both are zero, we move diagonally.
            # If one becomes zero, we move along that row/column.
            # The critical part is counting actual allocations.
            i += 1
            j += 1
        elif offres_copy[i] == 0:
            i += 1
        elif demandes_copy[j] == 0:
            j += 1
        else: # Should not happen if logic is correct, but as a fallback
            i += 1
            j += 1

    # Degeneracy handling
    # Number of basic variables should be n + m - 1
    required_allocations = n + m - 1

    while num_allocations < required_allocations:
        best_cell = None
        min_cost = float('inf')

        for r in range(n):
            for c in range(m):
                if allocation[r][c] is None: # If cell is empty
                    # Simple strategy: pick the unused cell with the lowest cost.
                    # A more advanced strategy would check for loop formation.
                    if couts[r][c] < min_cost:
                        min_cost = couts[r][c]
                        best_cell = (r, c)

        if best_cell:
            r_deg, c_deg = best_cell
            allocation[r_deg][c_deg] = EPSILON
            # Do not add EPSILON * couts[r_deg][c_deg] to total_cost for degeneracy handling
            num_allocations += 1
        else:
            # This case should ideally not be reached if there are enough cells
            # and n+m-1 is a valid number of allocations.
            break

    return {
        "allocation": allocation,
        "cout_total": total_cost
    }
