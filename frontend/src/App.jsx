import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'

import Home from './pages/Home.jsx'
import Auth from './pages/Auth.jsx'
import Research from './pages/Research.jsx'
import Search from './pages/Search.jsx'
import User from './pages/User.jsx'


function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/auth" element={<Auth />} />
      <Route path="/search" element={<Search />} />
      <Route path="/research" element={<Research />} />
      <Route path="/user/:username" element={<User />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  )
}
