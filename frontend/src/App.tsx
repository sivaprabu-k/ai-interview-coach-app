import Sidebar from './components/layout/Sidebar'
import DashboardHeader from './components/dashboard/DashboardHeader'
import StatsCards from './components/dashboard/StatsCards'
import PerformanceOverview from './components/dashboard/PerformanceOverview'
import RecentInterviews from './components/dashboard/RecentInterviews'
import InterviewResults from './components/dashboard/InterviewResults'

function App() {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />

      <main className="h-screen min-w-0 flex-1 overflow-y-auto p-8">
        <DashboardHeader />
        <StatsCards />
        <PerformanceOverview />
        <RecentInterviews />
        <InterviewResults />
      </main>
    </div>
  )
}

export default App