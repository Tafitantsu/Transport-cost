import axios from 'axios'

const SOLVE_API = 'http://127.0.0.1:8000/solve/'
const TASKS_API = 'http://127.0.0.1:8000/tasks/'

// 🔹 Créer une tâche (calcul immédiat)
export const createTask = async (payload) => {
  const res = await axios.post(SOLVE_API, payload)
  return res.data
}

// 🔹 Obtenir les détails d'une tâche complète
export const getTaskById = async (id) => {
  const res = await axios.get(`${SOLVE_API}${id}`)
  return res.data
}

// 🔹 Mettre à jour une tâche
export const updateTask = async (id, payload) => {
  const res = await axios.put(`${SOLVE_API}${id}`, payload)
  return res.data
}

// 🔹 Supprimer une tâche
export const deleteTask = async (id) => {
  await axios.delete(`${SOLVE_API}${id}`)
}

// 🔹 Liste de toutes les tâches (résumées)
export const getAllTasks = async () => {
  const res = await axios.get(TASKS_API)
  return res.data
}

// 🔹 Optimiser une tâche avec Stepping Stone
export const optimizeTaskWithSteppingStone = async (taskId) => {
  const res = await axios.post(`${SOLVE_API}${taskId}/optimize/stepping-stone`)
  return res.data
}

// 🔹 Liste des 5 dernières tâches
export const getRecentTasks = async () => {
  const res = await axios.get(`${TASKS_API}recent`)
  return res.data
}

// 🔹 Résumé d'une tâche spécifique
export const getTaskSummary = async (id) => {
  const res = await axios.get(`${TASKS_API}${id}`)
  return res.data
}
