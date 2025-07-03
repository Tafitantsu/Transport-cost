from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import Path
from database import get_db
from typing import Optional
from models import TransportTask
from schemas import TransportTaskCreate, TransportTaskOut, TransportTaskUpdate, TransportTaskResult
from solvers.cno import solve_coin_nord_ouest
from solvers.hammer import solve_hammer
from solvers.stepping_stone import solve_stepping_stone # Import the new solver

router = APIRouter(prefix="/solve", tags=["Solver"]) # Existing router for HTTP
ws_router = APIRouter(prefix="/ws/transport", tags=["WebSocket"]) # New router for WebSockets


@router.post("/", response_model=TransportTaskOut)
def create_solve_task(task_data: TransportTaskCreate, db: Session = Depends(get_db)):
    if sum(task_data.offres) != sum(task_data.demandes):
        raise HTTPException(
            status_code=400,
            detail="La somme des offres doit être égale à la somme des demandes."
        )

    initial_calc_result: Optional[dict] = None
    if task_data.algo_utilise == "cno":
        initial_calc_result = solve_coin_nord_ouest(task_data.offres.copy(), task_data.demandes.copy(), task_data.couts)
    elif task_data.algo_utilise == "hammer":
        initial_calc_result = solve_hammer(task_data.offres.copy(), task_data.demandes.copy(), task_data.couts)
    else:
        raise HTTPException(status_code=400, detail="Algorithme non reconnu")

    if initial_calc_result is None:
         raise HTTPException(status_code=500, detail="Erreur interne du serveur lors du calcul initial.")

    db_task = TransportTask(
        nom=task_data.nom,
        offres=task_data.offres,
        demandes=task_data.demandes,
        couts=task_data.couts,
        algo_utilise=task_data.algo_utilise,
        initial_result=initial_calc_result, # Store initial result
        resultat=initial_calc_result,       # Active result is initially the initial_result
        cout_total=initial_calc_result["cout_total"], # Also set the root cout_total for now
        is_optimized=False
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

@router.get("/{task_id}", response_model=TransportTaskOut)
def get_task(task_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    task = db.query(TransportTask).filter(TransportTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    return task

@router.put("/{task_id}", response_model=TransportTaskOut)
def update_task(
    task_id: int,
    updates: TransportTaskUpdate,
    db: Session = Depends(get_db)
):
    task = db.query(TransportTask).filter(TransportTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")

    if updates.offres is not None:
        task.offres = updates.offres
    if updates.demandes is not None:
        task.demandes = updates.demandes
    if updates.couts is not None:
        task.couts = updates.couts
    if updates.algo_utilise is not None:
        task.algo_utilise = updates.algo_utilise
    if updates.nom is not None: # Added nom to TransportTaskUpdate schema
        task.nom = updates.nom

    # Check if any core parameters that define the problem have changed
    problem_defining_change = any([
        updates.offres is not None,
        updates.demandes is not None,
        updates.couts is not None,
        updates.algo_utilise is not None
    ])

    if problem_defining_change:
        # recalcul automatique après modification
        if sum(task.offres) != sum(task.demandes): # Use task.offres as they are updated by now
            raise HTTPException(
                status_code=400,
                detail="La somme des offres doit être égale à la somme des demandes."
            )

        new_initial_result: Optional[dict] = None
        if task.algo_utilise == "cno":
            new_initial_result = solve_coin_nord_ouest(task.offres, task.demandes, task.couts)
        elif task.algo_utilise == "hammer":
            new_initial_result = solve_hammer(task.offres, task.demandes, task.couts)
        else:
            raise HTTPException(status_code=400, detail="Algorithme inconnu")

        if new_initial_result is None:
            raise HTTPException(status_code=500, detail="Erreur recalculating initial solution during update.")

        task.initial_result = new_initial_result
        task.resultat = new_initial_result # Active result is the new initial
        task.cout_total = new_initial_result["cout_total"]
        task.optimized_result = None # Reset optimization
        task.is_optimized = False

    task.date_derniere_maj = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task




@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TransportTask).filter(TransportTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    
    db.delete(task)
    db.commit()
    return

# New endpoint for Stepping Stone Optimization
@router.post("/{task_id}/optimize/stepping-stone", response_model=TransportTaskOut)
def optimize_task_with_stepping_stone(task_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    task = db.query(TransportTask).filter(TransportTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")

    if not task.resultat: # Should have a result from initial calculation
        raise HTTPException(status_code=400, detail="La tâche n'a pas de solution initiale à optimiser.")

    # Use the current 'resultat' as the input for optimization.
    # This allows re-optimizing if parameters changed, or optimizing an already optimized solution further (if applicable)
    # However, typical SS starts from an initial feasible solution (like CNO/Hammer).
    # For simplicity now, let's assume we always optimize the `initial_result` if available and not yet optimized.
    # Or, if already optimized, perhaps we don't allow re-optimizing via this simple endpoint
    # A more robust approach would be to decide based on `is_optimized` or allow choice.

    source_solution_for_optimization = task.initial_result
    if not source_solution_for_optimization:
        # Fallback if initial_result wasn't populated, use current resultat
        source_solution_for_optimization = task.resultat
        if not source_solution_for_optimization:
             raise HTTPException(status_code=400, detail="Aucune solution de base disponible pour l'optimisation.")


    # Ensure 'allocation' is a list of lists of floats/None, as expected by stepping_stone
    # The Pydantic model TransportTaskResult already defines allocation: List[List[Optional[float]]]
    # So, if source_solution_for_optimization is correctly parsed into/from this, it should be fine.

    # The initial_solution for stepping_stone needs 'allocation' and 'cout_total'
    # Our TransportTaskResult schema matches this.

    try:
        # The solve_stepping_stone function expects 'initial_solution' dict and 'couts' list.
        optimized_ss_result_dict = solve_stepping_stone(
            initial_solution=source_solution_for_optimization, # This is a dict from JSON
            couts=task.couts
        )
    except Exception as e:
        # Catch potential errors from stepping stone, especially if path finding is not robust yet
        print(f"Error during Stepping Stone optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'optimisation Stepping Stone: {e}")


    # Update task with optimized results
    task.optimized_result = optimized_ss_result_dict
    task.resultat = optimized_ss_result_dict # Update active result
    task.cout_total = optimized_ss_result_dict["cout_total"] # Update root cout_total
    task.is_optimized = True
    task.date_derniere_maj = datetime.utcnow()

    db.commit()
    db.refresh(task)
    return task

# The ws_router is defined but not used yet. It will be for WebSocket endpoints.
# Need to ensure the main FastAPI app includes this router if it's separate.
# For now, all are on 'router'.
