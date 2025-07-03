import React, { useEffect, useState } from 'react'
import { getAllTasks } from '@utils/transportService'
import { Link } from 'react-router-dom'

import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import Paper from '@mui/material/Paper'
import Button from '@mui/material/Button'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import Navbar from '@components/Navbar'
import '@styles/TaskList.css';

const TaskList = () => {
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const data = await getAllTasks()
        setTasks(data)
        console.log('Tâches récentes récupérées :', data)
      } catch (error) {
        console.error('Erreur lors de la récupération des tâches récentes :', error)
      }
    }

    fetchTasks()
  }, [])

  return (
    <>
    <Navbar />
    <Box className="task-list-container">
      <Typography variant="h4" gutterBottom className="task-list-header">
        📋 Liste de mes projets
      </Typography>

      {tasks.length === 0 ? (
        <Typography className="empty-task-list-message">Aucune tâche.</Typography>
      ) : (
        <TableContainer component={Paper} className="task-list-table-container">
          <Table className="task-list-table" aria-label="table des tâches récentes">
            <TableHead>
              <TableRow>
                <TableCell>Nom</TableCell>
                <TableCell>Algorithme</TableCell>
                <TableCell>Coût total</TableCell>
                <TableCell>Date de création</TableCell>
                <TableCell>Dernière mise à jour</TableCell>
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tasks.map((task) => (
                <TableRow key={task.id}>
                  <TableCell>{task.nom}</TableCell>
                  <TableCell>{task.algo_utilise.toUpperCase()}</TableCell>
                  <TableCell>{task.cout_total}</TableCell>
                  <TableCell>{new Date(task.date_creation).toLocaleString()}</TableCell>
                  <TableCell>
                    {task.date_derniere_maj
                      ? new Date(task.date_derniere_maj).toLocaleString()
                      : '—'}
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="outlined"
                      component={Link}
                      to={`/task/${task.id}`}
                      className="view-task-button"
                    >
                      👁️ Voir
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
    </>
  )
}

export default TaskList
