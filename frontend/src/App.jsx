import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext.jsx'

import Home from './pages/Home.jsx'
import Auth from './pages/Auth.jsx'
import Login from './components/auth/Login.jsx'
import Register from './components/auth/Register.jsx'
import ChangePwViaEmailToken from './components/auth/ChangePwViaEmailToken.jsx'
import Research from './pages/Research.jsx'
import Search from './pages/Search.jsx'
import User from './pages/User.jsx'
import VerifyEmailConfirm from './components/auth/VerifyEmailConfirm.jsx'
import Test from './components/home/Test.jsx'


function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/test" element={<Test />} />
      <Route path="/auth" element={<Auth />}>
        <Route index element={<Navigate to="login" replace />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="change" element={<ChangePwViaEmailToken />} />
        <Route path="verify" element={<VerifyEmailConfirm />} />
      </Route>
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