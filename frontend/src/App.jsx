import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home.jsx'
import Research from './pages/Research.jsx'
import User from './pages/User.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/research" element={<Research />} />
        <Route path="/user/:username" element={<User />} />
      </Routes>
    </BrowserRouter>
  )
}