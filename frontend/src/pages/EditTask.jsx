import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getTaskById, updateTask } from '@utils/transportService'
import TaskForm from '@components/TaskForm'
import Navbar from '@components/Navbar'

const EditTask = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [initialData, setInitialData] = useState(null)
  const [errorMessage, setErrorMessage] = useState(null)

  useEffect(() => {
    const fetchTask = async () => {
      try {
        const data = await getTaskById(id)
        setInitialData(data)
      } catch (error) {
        console.error('Erreur de chargement :', error)
        setErrorMessage("Impossible de charger la tâche.")
      }
    }
    fetchTask()
  }, [id])

  const handleUpdate = async (updatedData) => {
    try {
      setErrorMessage(null)
      await updateTask(id, updatedData)
      navigate(`/task/${id}`)
    } catch (error) {
      console.error('Erreur de mise à jour :', error)
      if (error.response && error.response.data && error.response.data.detail) {
        setErrorMessage(error.response.data.detail)
      } else {
        setErrorMessage("Une erreur est survenue lors de la mise à jour.")
      }
    }
  }

  if (!initialData) return <p>Chargement...</p>

  return (
    <>
    <Navbar />
    <div className="container mx-auto p-4">
      {errorMessage && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {errorMessage}
        </div>
      )}
      <TaskForm isEditing={true} initialData={initialData} onSubmit={handleUpdate} />
    </div>
    </>
  )
}

export default EditTask
