import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getTaskById, deleteTask, optimizeTaskWithSteppingStone } from '@utils/transportService' // Added optimizeTaskWithSteppingStone
import Navbar from '@components/Navbar'
import '@styles/TaskDetail.css';

const TaskDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [task, setTask] = useState(null) // Will hold the full task object
  const [loading, setLoading] = useState(true)
  const [isOptimizing, setIsOptimizing] = useState(false) // For loading state during optimization
  // viewingOptimizedSolution will be true if task.is_optimized is true after fetching or optimization
  // and can be toggled by the user if is_optimized is true.
  const [viewingOptimizedSolution, setViewingOptimizedSolution] = useState(true)
  const [error, setError] = useState(null) // For displaying errors

  useEffect(() => {
    const fetchTask = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await getTaskById(id)
        setTask(data)
        // If the fetched task is optimized, by default view the optimized solution.
        // Otherwise, this flag doesn't really matter until after an optimization is run.
        if (data && data.is_optimized) {
          setViewingOptimizedSolution(true)
        } else {
          setViewingOptimizedSolution(false) // Or true, doesn't matter much if not optimized.
        }
      } catch (err) {
        console.error('Erreur lors du chargement de la tâche:', err)
        setError('Impossible de charger les détails de la tâche.')
      } finally {
        setLoading(false)
      }
    }

    fetchTask()
  }, [id])

  const handleDelete = async () => {
    if (window.confirm('Voulez-vous vraiment supprimer cette tâche ?')) {
      try {
        await deleteTask(id)
        navigate('/')
      } catch (err) {
        console.error('Erreur lors de la suppression :', err)
      }
    }
  }

/* (removed duplicate import and component definition) */

  const handleEdit = () => {
    navigate(`/edit/${id}`)
  }

  const handleOptimize = async () => {
    if (!task || !id) return;
    setIsOptimizing(true);
    setError(null);
    try {
      const updatedTaskData = await optimizeTaskWithSteppingStone(id);
      setTask(updatedTaskData);
      setViewingOptimizedSolution(true); // Default to viewing the new optimized solution
    } catch (err) {
      console.error('Erreur lors de l\'optimisation:', err);
      setError(err.response?.data?.detail || 'Une erreur est survenue lors de l\'optimisation.');
    } finally {
      setIsOptimizing(false);
    }
  };

  const toggleViewSolution = () => {
    setViewingOptimizedSolution(!viewingOptimizedSolution);
  };

  if (loading) return <p>Chargement...</p>
  if (error && !task) return <p className="error-message">{error}</p> // Show error if task couldn't load
  if (!task) return <p>Tâche introuvable</p>


  // Determine what to display based on optimization state and view toggle
  const currentDisplayResult = task.is_optimized && viewingOptimizedSolution && task.optimized_result
    ? task.optimized_result
    : task.initial_result || task.resultat; // Fallback to initial_result, then to general resultat

  const allocationMatrixToDisplay = currentDisplayResult?.allocation;
  const costToDisplay = currentDisplayResult?.cout_total;

  return (
    <>
    <Navbar />
    <div className="task-detail-container">
      {error && <p className="error-message" style={{color: 'red', textAlign: 'center', marginBottom: '1rem'}}>{error}</p>}
      <h1 className="task-detail-header">Détails du projet : {task.nom}</h1>

      <p className="info-paragraph"><strong className="info-label">Algorithme utilisé :</strong> {task.algo_utilise === 'cno' ? 'Coin Nord-Ouest' : 'Hammer'}</p>
      <p className="info-paragraph"><strong className="info-label">Date de création :</strong> {new Date(task.date_creation).toLocaleString()}</p>
      <p className="info-paragraph">
        <strong className="info-label">Statut :</strong>
        {task.is_optimized ? 'Optimisé (Stepping Stone)' : 'Solution Initiale'}
      </p>


      {/* Section for Optimization Actions */}
      <div className="optimization-actions action-buttons-container" style={{ marginBottom: '1.5rem', justifyContent: 'center' }}>
        {!task.is_optimized && (
          <button onClick={handleOptimize} disabled={isOptimizing} className="action-button optimize-button">
            {isOptimizing ? 'Optimisation en cours...' : '🔄 Optimiser avec Stepping Stone'}
          </button>
        )}
        {task.is_optimized && task.initial_result && task.optimized_result && (
          <button onClick={toggleViewSolution} className="action-button view-toggle-button">
            {viewingOptimizedSolution ? 'Voir Solution Initiale' : 'Voir Solution Optimisée'}
          </button>
        )}
      </div>


      <div className="detail-section">
        <h2 className="section-title">Offres</h2>
        <div className="values-display-container">
          {task.offres.map((val, i) => (
            <span key={i} className="value-item">{val}</span>
          ))}
        </div>
      </div>

      <div className="detail-section">
        <h2 className="section-title">Demandes</h2>
        <div className="values-display-container">
          {task.demandes.map((val, j) => (
            <span key={j} className="value-item">{val}</span>
          ))}
        </div>
      </div>

      <div className="detail-section">
        <h2 className="section-title">Coûts</h2>
        <div className="detail-table-container">
          <table className="detail-table">
            <tbody>
              {task.couts.map((row, i) => (
                <tr key={i}>
                  {row.map((val, j) => (
                    <td key={j} className='allocation-cell-allocated'>{val}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Display Allocation Table */}
      {allocationMatrixToDisplay && Array.isArray(allocationMatrixToDisplay) && (
        <div className="detail-section">
          <h2 className="section-title">
            Allocation ({task.is_optimized ? (viewingOptimizedSolution ? 'Optimisée' : 'Initiale') : 'Initiale'})
          </h2>
          <div className="detail-table-container">
            <table className="detail-table">
              <tbody>
                {allocationMatrixToDisplay.map((row, i) => (
                  <tr key={`alloc-row-${i}`}>
                    {row.map((allocatedValue, j) => {
                      // Ensure task.couts[i] and task.couts[i][j] are valid before accessing
                      const unitCost = task.couts && task.couts[i] && task.couts[i][j] !== undefined
                                       ? task.couts[i][j]
                                       : 'N/A';
                        const isEffectivelyZero = allocatedValue === null || allocatedValue === 0;
                        // Define EPSILON based on the backend value
                        const EPSILON_VAL = 1e-6;
                        const IS_EPSILON_PRECISION = 1e-9; // Precision for comparing float

                        // Check if the allocated value is our epsilon
                        const isEpsilonAllocation =
                          allocatedValue !== null &&
                          Math.abs(allocatedValue - EPSILON_VAL) < IS_EPSILON_PRECISION;

                        let displayValue;
                        let cellClass = 'allocation-cell-not-allocated';

                        if (isEpsilonAllocation) {
                          displayValue = `ε (coût: ${unitCost})`;
                          cellClass = 'allocation-cell-epsilon'; // New class for epsilon styling
                        } else if (!isEffectivelyZero && allocatedValue > 0) {
                          // Format to a reasonable number of decimal places if it's a float
                          const formattedAllocatedValue = Number.isInteger(allocatedValue)
                            ? allocatedValue
                            : parseFloat(allocatedValue).toFixed(2);
                          displayValue = `${formattedAllocatedValue} (coût: ${unitCost})`;
                          cellClass = 'allocation-cell-allocated';
                        } else {
                          displayValue = `0 (coût: ${unitCost})`;
                        }

                        return (
                          <td key={j} className={cellClass}>
                            {displayValue}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
        </div>
      )}

      {/* Display Total Cost */}
      {costToDisplay !== undefined && (
        <div className="detail-section total-cost-paragraph">
          <p>
            <strong className="info-label">
              Coût Total ({task.is_optimized ? (viewingOptimizedSolution ? 'Optimisé' : 'Initial') : 'Initial'}) :
            </strong>
            {typeof costToDisplay === 'number' ? costToDisplay.toFixed(2) : 'N/A'}
          </p>
          {task.is_optimized && task.initial_result?.cout_total !== undefined && task.optimized_result?.cout_total !== undefined && (
            <p style={{marginTop: '0.5rem'}}>
              <em className="info-label">(Coût Initial : {task.initial_result.cout_total.toFixed(2)},
              Coût Optimisé : {task.optimized_result.cout_total.toFixed(2)})</em>
            </p>
          )}
        </div>
      )}

      <div className="action-buttons-container">
        <button onClick={handleEdit} className="action-button edit-button">
          ✏️ Modifier
        </button>
        <button onClick={handleDelete} className="action-button delete-button">
          🗑️ Supprimer
        </button>
      </div>
    </div>
    </>
  )
}

export default TaskDetail
