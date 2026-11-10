import {
  Video,
  CheckCircle2,
  TrendingUp,
  CalendarClock,
} from 'lucide-react'

const stats = [
  {
    title: 'Total Interviews',
    value: '24',
    change: '+12%',
    description: 'from last month',
    icon: Video,
    color: 'bg-purple-100 text-purple-600',
  },
  {
    title: 'Completed Interviews',
    value: '18',
    change: '+8%',
    description: 'from last month',
    icon: CheckCircle2,
    color: 'bg-green-100 text-green-600',
  },
  {
    title: 'Average Score',
    value: '85%',
    change: '+5%',
    description: 'from last month',
    icon: TrendingUp,
    color: 'bg-blue-100 text-blue-600',
  },
  {
    title: 'Upcoming Interviews',
    value: '06',
    change: 'Next 7 days',
    description: 'scheduled interviews',
    icon: CalendarClock,
    color: 'bg-orange-100 text-orange-600',
  },
]

function StatsCards() {
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

            <div className="mt-4 flex items-center gap-2 text-xs">
              <span className="font-semibold text-green-600">
                {stat.change}
              </span>
              <span className="text-gray-400">
                {stat.description}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default StatsCards
