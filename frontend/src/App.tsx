import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom'
import Sidebar from './components/layout/Sidebar'
import DashboardHeader from './components/dashboard/DashboardHeader'
import StatsCards from './components/dashboard/StatsCards'
import PerformanceOverview from './components/dashboard/PerformanceOverview'
import RecentInterviews from './components/dashboard/RecentInterviews'
import InterviewResults from './components/dashboard/InterviewResults'
import InterviewPage from './pages/InterviewPage'
import LoginPage from './pages/LoginPage'
import ProtectedRoute from './components/auth/ProtectedRoute'
import InterviewHistoryPage from './pages/InterviewHistoryPage'
import InsightsPage from './pages/InsightsPage'
import DocumentsPage from './pages/DocumentsPage'
import CareerProfilePage from './pages/CareerProfilePage'
import FAQPage from './pages/FAQPage'
import SettingsPage from './pages/SettingsPage'
import { useEffect, useState } from 'react'
import { getDashboardSummary } from './services/dashboardService'
import type { DashboardSummary } from './types/dashboard'

function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const data = await getDashboardSummary()
        setSummary(data)
      } catch {
        setError('Unable to load dashboard data. Please try again.')
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [])

  return (
    <>
      <DashboardHeader />

      {loading && (
        <p className="py-8 text-center text-gray-500">
          Loading dashboard...
        </p>
      )}

      {!loading && error && (
        <p className="py-8 text-center text-red-500">
          {error}
        </p>
      )}

      {!loading && !error && summary && (
        <>
          <StatsCards summary={summary} />
          <PerformanceOverview summary={summary} />
          <RecentInterviews summary={summary} />
          <InterviewResults evaluation={summary.latest_evaluation} />
        </>
      )}
    </>
  )
}

function DashboardLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />

      <main className="h-screen min-w-0 flex-1 overflow-y-auto p-8">
        <Outlet />
      </main>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<DashboardLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="interview" element={<InterviewPage />} />
            <Route path="interview-history" element={<InterviewHistoryPage />} />
            <Route path="insights" element={<InsightsPage />} />
            <Route path="documents" element={<DocumentsPage />} />
            <Route path="career-profile" element={<CareerProfilePage />} />
            <Route path="faq" element={<FAQPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App