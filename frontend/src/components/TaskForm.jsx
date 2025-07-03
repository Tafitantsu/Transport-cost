import React, { useState, useEffect } from 'react'
import '@styles/TaskForm.css';

const TaskForm = ({ initialData = null, onSubmit, isEditing }) => {
  const [nom, setNom] = useState('')
  const [algo, setAlgo] = useState('cno')
  const [rows, setRows] = useState(3)
  const [cols, setCols] = useState(3)
  const [offre, setOffre] = useState(Array(3).fill(0))
  const [demande, setDemande] = useState(Array(3).fill(0))
  const [couts, setCouts] = useState(Array(3).fill().map(() => Array(3).fill(0)))
  const [sumOffre, setSumOffre] = useState(0)
  const [sumDemande, setSumDemande] = useState(0)

  useEffect(() => {
    if (initialData) {
      setNom(initialData.nom || '')
      setAlgo(initialData.algo_utilise || 'cno')
      const offreInit = initialData.offres || []
      const demandeInit = initialData.demandes || []
      const coutsInit = initialData.couts || [[]]
      setOffre(offreInit)
      setDemande(demandeInit)
      setCouts(coutsInit)
      setRows(offreInit.length)
      setCols(demandeInit.length)
    }
  }, [initialData])

  useEffect(() => {
    setSumOffre(offre.reduce((acc, val) => acc + val, 0))
  }, [offre])

  useEffect(() => {
    setSumDemande(demande.reduce((acc, val) => acc + val, 0))
  }, [demande])

  const handleCostChange = (i, j, value) => {
    const newCouts = [...couts]
    newCouts[i][j] = parseInt(value) || 0
    setCouts(newCouts)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const payload = {
      ...(isEditing ? {} : { nom }),
      offres: offre,
      demandes: demande,
      couts,
      algo_utilise: algo,
    }
    onSubmit(payload)
  }

  return (
    <div className="task-form-container">
      <h1 className="task-form-header">
        {isEditing ? 'Modifier le tâche' : '➕ Créer un nouveau tâche'}
      </h1>

      <form onSubmit={handleSubmit} className="task-form">
        {!isEditing && (
          <div className="form-section">
            <label htmlFor="nom">Nom de la tâche :</label>
            <input
              type="text"
              id="nom"
              value={nom}
              onChange={(e) => setNom(e.target.value)}
              className="input-nom"
              required
            />
          </div>
        )}

        <div className="form-section">
          <label htmlFor="algo">Algorithme :</label>
          <select id="algo" className="input-algo" value={algo} onChange={(e) => setAlgo(e.target.value)}>
            <option value="cno">Coin Nord-Ouest</option>
            <option value="hammer">Hammer</option>
          </select>
        </div>

        <div className="form-section">
          <label>Dimensions :</label>
          <div className="dimensions-container">
            <input
              type="number"
              min={1}
            value={rows}
            onChange={(e) => {
              const val = parseInt(e.target.value)
              setRows(val)

              setOffre((prev) => {
                const newArr = [...prev]
                while (newArr.length < val) newArr.push(0)
                return newArr.slice(0, val)
              })

              setCouts((prev) => {
                const newCouts = [...prev]
                while (newCouts.length < val) newCouts.push(Array(cols).fill(0))
                return newCouts.slice(0, val)
              })
            }}
            className="input-dimension"
            aria-label="Nombre de lignes"
          />
          <span>lignes ×</span>
          <input
            type="number"
            min={1}
            value={cols}
            onChange={(e) => {
              const val = parseInt(e.target.value)
              setCols(val)

              setDemande((prev) => {
                const newArr = [...prev]
                while (newArr.length < val) newArr.push(0)
                return newArr.slice(0, val)
              })

              setCouts((prev) =>
                prev.map((row) => {
                  const newRow = [...row]
                  while (newRow.length < val) newRow.push(0)
                  return newRow.slice(0, val)
                })
              )
            }}
            className="input-dimension"
            aria-label="Nombre de colonnes"
          />
          <span>colonnes</span>
          </div>
        </div>

        <div className="form-section">
          <h2 className="section-title">Offre</h2>
          <div className="input-list-container">
            {offre.map((val, i) => (
              <input
                key={i}
                type="number"
                value={val}
                onChange={(e) => {
                  const newOffre = [...offre]
                  newOffre[i] = parseInt(e.target.value) || 0
                  setOffre(newOffre)
                }}
                className="input-offre-demande"
                aria-label={`Offre ${i + 1}`}
              />
            ))}
          </div>
          <p className="sum-display">Somme des offres : {sumOffre}</p>
        </div>

        <div className="form-section">
          <h2 className="section-title">Demande</h2>
          <div className="input-list-container">
            {demande.map((val, j) => (
              <input
                key={j}
                type="number"
                value={val}
                onChange={(e) => {
                  const newDemande = [...demande]
                  newDemande[j] = parseInt(e.target.value) || 0
                  setDemande(newDemande)
                }}
                className="input-offre-demande"
                aria-label={`Demande ${j + 1}`}
              />
            ))}
          </div>
          <p className="sum-display">Somme des demandes : {sumDemande}</p>
          {offre.length > 0 && demande.length > 0 && sumOffre !== sumDemande && (
            <p className="validation-message-error">
              Attention : La somme des offres ({sumOffre}) doit être égale à la somme des demandes ({sumDemande}).
            </p>
          )}
        </div>

        <div className="form-section">
          <h2 className="section-title">Coûts</h2>
          <div className="costs-table-container">
            <table className="costs-table">
              <tbody>
                {couts.map((row, i) => (
                  <tr key={i}>
                    {row.map((val, j) => (
                      <td key={j}>
                        <input
                          type="number"
                          value={val}
                          onChange={(e) => handleCostChange(i, j, e.target.value)}
                          aria-label={`Coût pour Offre ${i+1} Demande ${j+1}`}
                          className='input-cost'
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <button
          type="submit"
          className={`submit-button ${isEditing ? 'edit' : 'create'}`}
        >
          {isEditing ? '♻️ Mettre à jour' : '🧮 Calculer'}
        </button>
      </form>
    </div>
  )
}

export default TaskForm
