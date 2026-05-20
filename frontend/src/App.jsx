import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
import Landing from './pages/Landing.jsx'
import Home from './pages/Home.jsx'
import Research from './pages/Research.jsx'
import Search from './pages/Search.jsx'
import User from './pages/User.jsx'
import Scoreboard from './pages/Scoreboard.jsx'
import Trade from './pages/Trade.jsx'
import Register from './pages/Register.jsx'
import LogIn from './components/LogIn.jsx'

function ProtectedRoute({ children }) {
  const { user } = useAuth()
  if (user === undefined) return null  // still checking session, render nothing
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<LogIn />} />
          <Route path="/register" element={<Register />} />
          <Route path="/search" element={<Search />} />
          <Route path="/research" element={<Research />} />
          <Route path="/user/:username" element={<User />} />
          <Route path="/scoreboard" element={<Scoreboard />} />
          <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
          <Route path="/trade" element={<ProtectedRoute><Trade /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}