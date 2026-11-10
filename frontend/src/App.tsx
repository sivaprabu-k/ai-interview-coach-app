import Sidebar from './components/layout/Sidebar'
import DashboardHeader from './components/dashboard/DashboardHeader'
import StatsCards from './components/dashboard/StatsCards'
import PerformanceOverview from './components/dashboard/PerformanceOverview'

function App() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <main className="min-w-0 flex-1 p-8">
        <DashboardHeader />
        <StatsCards />
        <PerformanceOverview />
      </main>
    </div>
  )
}

export default App