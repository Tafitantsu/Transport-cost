import Home from '@pages/Home'
import CreateTask from '@pages/CreateTask'
import TaskDetail from '@pages/TaskDetail'
import EditTask from '@pages/EditTask'
import TaskList from '@pages/TaskList'
//import '@styles/global.css'
import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"


function App() {
  return (
    <Router>
      <Routes>

        <Route path="/" element={ <Navigate to="/Home"/>} />
        <Route path="/home" element={<Home />} />
        <Route path="/list" element={<TaskList/>} />
        <Route path="/create" element={<CreateTask />} />
        <Route path="/task/:id" element={<TaskDetail />} />
        <Route path="/edit/:id" element={<EditTask />} />
      </Routes>
    </Router>
  )
}

export default App;