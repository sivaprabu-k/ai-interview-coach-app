import {
  Award,
  Brain,
  MessageSquare,
  Lightbulb,
  TrendingUp,
} from 'lucide-react'

const evaluation = {
  candidate: 'Siva',
  role: 'Python Developer',
  overallScore: 92,
  skills: [
    { name: 'Technical Knowledge', score: 95, icon: Brain },
    { name: 'Communication', score: 88, icon: MessageSquare },
    { name: 'Problem Solving', score: 90, icon: Lightbulb },
    { name: 'Confidence', score: 85, icon: TrendingUp },
  ],
  strengths: [
    'Strong Python fundamentals and backend knowledge',
    'Good understanding of REST API development',
    'Clear communication and problem-solving approach',
  ],
  improvements: [
    'Explore advanced database optimization techniques',
    'Improve knowledge of system design concepts',
  ],
}

function InterviewResults() {
  return (
    <section className="mb-8 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
      <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h2 className="text-lg font-bold text-gray-800">
            Interview Results & Evaluation
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            AI-powered candidate performance evaluation
          </p>
        </div>

        <span className="w-fit rounded-full bg-purple-100 px-3 py-1 text-xs font-semibold text-purple-700">
          AI Evaluation
        </span>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Overall Score */}
        <div className="flex flex-col items-center justify-center rounded-xl bg-purple-50 p-6">
          <Award size={32} className="mb-3 text-purple-600" />

          <p className="text-sm font-medium text-gray-500">
            Overall Score
          </p>

          <h3 className="mt-2 text-5xl font-bold text-purple-600">
            {evaluation.overallScore}%
          </h3>

          <span className="mt-3 rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">
            Excellent Performance
          </span>

          <p className="mt-4 text-center text-sm text-gray-500">
            {evaluation.candidate} · {evaluation.role}
          </p>
        </div>

        {/* Skill Scores */}
        <div className="lg:col-span-2">
          <h3 className="mb-5 font-semibold text-gray-800">
            Skill Assessment
          </h3>

          <div className="space-y-5">
            {evaluation.skills.map((skill) => {
              const Icon = skill.icon

              return (
                <div key={skill.name}>
                  <div className="mb-2 flex items-center justify-between">
                    <span className="flex items-center gap-2 text-sm font-medium text-gray-600">
                      <Icon size={17} className="text-purple-600" />
                      {skill.name}
                    </span>

                    <span className="text-sm font-bold text-gray-800">
                      {skill.score}%
                    </span>
                  </div>

                  <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                    <div
                      className="h-full rounded-full bg-purple-600 transition-all"
                      style={{ width: `${skill.score}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Strengths and Improvements */}
      <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="rounded-xl border border-green-100 p-5">
          <h3 className="mb-4 font-semibold text-green-700">
            Key Strengths
          </h3>

          <ul className="space-y-3">
            {evaluation.strengths.map((item) => (
              <li key={item} className="flex gap-2 text-sm text-gray-600">
                <span className="font-bold text-green-600">✓</span>
                {item}
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-xl border border-orange-100 p-5">
          <h3 className="mb-4 font-semibold text-orange-700">
            Areas for Improvement
          </h3>

          <ul className="space-y-3">
            {evaluation.improvements.map((item) => (
              <li key={item} className="flex gap-2 text-sm text-gray-600">
                <span className="font-bold text-orange-500">•</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}

export default InterviewResults