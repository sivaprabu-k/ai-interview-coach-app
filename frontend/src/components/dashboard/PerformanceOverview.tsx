import {
  BarChart,
  Bar,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { DashboardSummary } from '../../types/dashboard'

interface PerformanceOverviewProps {
  summary: DashboardSummary
}

function PerformanceOverview({ summary }: PerformanceOverviewProps) {
  const averageScore = summary.stats.average_score

  const evaluatedSessions = summary.recent_sessions.filter(
    (session) => session.average_score !== null
  )

  const chartData = [...evaluatedSessions]
    .slice(0, 6)
    .reverse()
    .map((session) => ({
      role: session.role,
      score: session.average_score,
    }))

  const recentScores = evaluatedSessions.slice(0, 3)

  const performanceLabel =
    averageScore === null
      ? 'No performance data yet'
      : averageScore >= 80
        ? 'Excellent Performance'
        : averageScore >= 60
          ? 'Good Performance'
          : 'Keep Practicing'

  return (
    <section className="mb-8 grid grid-cols-1 gap-6 xl:grid-cols-3">
      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm xl:col-span-2">
        <div className="mb-6">
          <h2 className="text-lg font-bold text-gray-800">
            Performance Overview
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Your recent interview scores
          </p>
        </div>

        {chartData.length > 0 ? (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="role"
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                />
                <Tooltip />
                <Bar
                  dataKey="score"
                  name="Average Score"
                  fill="#9333ea"
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="flex h-72 items-center justify-center text-sm text-gray-400">
            Complete an interview evaluation to see your performance chart.
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-bold text-gray-800">
          Overall Performance
        </h2>

        <p className="mt-1 text-sm text-gray-500">
          Based on your successful evaluations
        </p>

        <div className="my-8 flex flex-col items-center">
          <div className="flex h-36 w-36 items-center justify-center rounded-full border-[10px] border-purple-100">
            <span className="text-4xl font-bold text-purple-700">
              {averageScore !== null ? `${averageScore}%` : 'N/A'}
            </span>
          </div>

          <p className="mt-4 text-center font-semibold text-gray-800">
            {performanceLabel}
          </p>

          <p className="mt-1 text-center text-sm text-gray-500">
            {averageScore !== null
              ? 'Keep improving your interview skills!'
              : 'Your score will appear after an evaluation.'}
          </p>
        </div>

        <div className="space-y-4">
          {recentScores.length > 0 ? (
            recentScores.map((session) => (
              <div key={session.session_id}>
                <div className="mb-2 flex justify-between gap-2 text-sm">
                  <span className="truncate text-gray-600">
                    {session.role}
                  </span>
                  <span className="font-semibold text-gray-800">
                    {session.average_score}%
                  </span>
                </div>

                <div className="h-2 rounded-full bg-gray-100">
                  <div
                    className="h-2 rounded-full bg-purple-600"
                    style={{
                      width: `${session.average_score}%`,
                    }}
                  />
                </div>
              </div>
            ))
          ) : (
            <p className="text-center text-sm text-gray-400">
              No evaluated interviews yet.
            </p>
          )}
        </div>
      </div>
    </section>
  )
}

export default PerformanceOverview
