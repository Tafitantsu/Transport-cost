import React, { useState } from 'react'
import TaskForm from '@components/TaskForm'
import { createTask } from '@utils/transportService'
import { useNavigate } from 'react-router-dom'
import Navbar from '@components/Navbar'

const CreateTask = () => {
  const navigate = useNavigate()
  const [errorMessage, setErrorMessage] = useState(null)

  const handleCreate = async (payload) => {
    try {
      setErrorMessage(null) // réinitialiser l’erreur avant un nouvel essai
      const createdTask = await createTask(payload)
      navigate(`/task/${createdTask.id}`)
    } catch (error) {
      console.error('Erreur lors de la création :', error)

      // Essayer de récupérer le message précis de l'API
      if (error.response && error.response.data && error.response.data.detail) {
        setErrorMessage(error.response.data.detail)
      } else {
        setErrorMessage("Une erreur est survenue lors de la création.")
      }
    }
  }

  return (
    <>
    <Navbar />
    <div className="container mx-auto p-4">
      {errorMessage && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {errorMessage}
        </div>
      )}
      <TaskForm onSubmit={handleCreate} isEditing={false} />
    </div>
    </>
  )
}

export default CreateTask
