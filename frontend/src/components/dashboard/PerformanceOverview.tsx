import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'

const performanceData = [
  { skill: 'Communication', score: 85 },
  { skill: 'Technical', score: 90 },
  { skill: 'Problem Solving', score: 75 },
  { skill: 'Confidence', score: 80 },
  { skill: 'Adaptability', score: 70 },
  { skill: 'Time Management', score: 88 },
]

function PerformanceOverview() {
  return (
    <section className="mb-8 grid grid-cols-1 gap-6 xl:grid-cols-3">

      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm xl:col-span-2">
        <div className="mb-6">
          <h2 className="text-lg font-bold text-gray-800">
            Performance Overview
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Your interview skills analysis
          </p>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={performanceData}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis
                dataKey="skill"
                tick={{ fill: '#6b7280', fontSize: 11 }}
              />
              <PolarRadiusAxis
                angle={30}
                domain={[0, 100]}
                tick={false}
                axisLine={false}
              />
              <Radar
                name="Performance"
                dataKey="score"
                stroke="#9333ea"
                fill="#9333ea"
                fillOpacity={0.3}
              />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-bold text-gray-800">
          Overall Performance
        </h2>

        <p className="mt-1 text-sm text-gray-500">
          Based on your recent interviews
        </p>

        <div className="my-8 flex flex-col items-center">
          <div className="flex h-36 w-36 items-center justify-center rounded-full border-[10px] border-purple-100">
            <span className="text-4xl font-bold text-purple-700">
              85%
            </span>
          </div>

          <p className="mt-4 font-semibold text-gray-800">
            Excellent Performance
          </p>

          <p className="mt-1 text-sm text-gray-500">
            Keep up the good work!
          </p>
        </div>

        <div className="space-y-4">
          {performanceData.slice(0, 3).map((item) => (
            <div key={item.skill}>
              <div className="mb-2 flex justify-between text-sm">
                <span className="text-gray-600">{item.skill}</span>
                <span className="font-semibold text-gray-800">
                  {item.score}%
                </span>
              </div>

              <div className="h-2 rounded-full bg-gray-100">
                <div
                  className="h-2 rounded-full bg-purple-600"
                  style={{ width: `${item.score}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default PerformanceOverview
