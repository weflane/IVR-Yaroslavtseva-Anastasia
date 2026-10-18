import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import useAuthStore from './store/authStore'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Quiz from './pages/Quiz'
import QuizResult from './pages/QuizResult'
import BookDetail from './pages/BookDetail'
import Catalog from './pages/Catalog'
import Profile from './pages/Profile'
import Recommendations from './pages/Recommendations'

function PrivateRoute({ children }) {
  const { user, loading } = useAuthStore()
  if (loading) return <div className="loading">Loading...</div>
  return user ? children : <Navigate to="/login" />
}

export default function App() {
  const fetchUser = useAuthStore((s) => s.fetchUser)

  useEffect(() => {
    fetchUser()
  }, [])

  return (
    <BrowserRouter>
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/catalog" element={<Catalog />} />
          <Route path="/books/:id" element={<BookDetail />} />
          <Route path="/quiz" element={<PrivateRoute><Quiz /></PrivateRoute>} />
          <Route path="/quiz/result" element={<PrivateRoute><QuizResult /></PrivateRoute>} />
          <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
          <Route path="/recommendations" element={<PrivateRoute><Recommendations /></PrivateRoute>} />
        </Routes>
      </main>
      <footer className="footer">
        <div className="footer-dots"><span /><span /><span /></div>
        <div>BookMatch</div>
      </footer>
    </BrowserRouter>
  )
}