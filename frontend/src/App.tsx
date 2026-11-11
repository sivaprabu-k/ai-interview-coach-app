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

function Dashboard() {
  return (
    <>
      <DashboardHeader />
      <StatsCards />
      <PerformanceOverview />
      <RecentInterviews />
      <InterviewResults />
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
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App