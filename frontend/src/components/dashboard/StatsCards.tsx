import {
  Video,
  CheckCircle2,
  TrendingUp,
  Clock,
} from 'lucide-react'
import type { DashboardSummary } from '../../types/dashboard'

interface StatsCardsProps {
  summary: DashboardSummary
}

function StatsCards({ summary }: StatsCardsProps) {
  const stats = [
    {
      title: 'Total Interviews',
      value: summary.stats.total_interviews.toString(),
      description: 'Total created interviews',
      icon: Video,
      color: 'bg-purple-100 text-purple-600',
    },
    {
      title: 'Completed Interviews',
      value: summary.stats.completed_interviews.toString(),
      description: 'Completed sessions',
      icon: CheckCircle2,
      color: 'bg-green-100 text-green-600',
    },
    {
      title: 'Average Score',
      value:
        summary.stats.average_score !== null
          ? `${summary.stats.average_score}%`
          : 'N/A',
      description: `${summary.stats.total_evaluations} successful evaluations`,
      icon: TrendingUp,
      color: 'bg-blue-100 text-blue-600',
    },
    {
      title: 'In Progress Interviews',
      value: summary.stats.in_progress_interviews.toString(),
      description: 'Currently active sessions',
      icon: Clock,
      color: 'bg-orange-100 text-orange-600',
    },
  ]

  return (
    <div className="mb-8 grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat) => {
        const Icon = stat.icon

        return (
          <div
            key={stat.title}
            className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">
                  {stat.title}
                </p>
                <h2 className="mt-3 text-3xl font-bold text-gray-800">
                  {stat.value}
                </h2>
              </div>

              <div className={`rounded-xl p-3 ${stat.color}`}>
                <Icon size={23} />
              </div>
            </div>

            <div className="mt-4 text-xs text-gray-400">
              {stat.description}
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default StatsCards
