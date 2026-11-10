import { Eye, CalendarDays } from 'lucide-react'
import { useState } from 'react'
import InterviewDetailsModal from './InterviewDetailsModal'

const interviews = [
  {
    id: 1,
    candidate: 'Siva',
    role: 'Python Developer',
    date: 'Nov 10, 2026',
    status: 'Completed',
    score: 92,
  },
  {
    id: 2,
    candidate: 'Ganesh',
    role: 'Full Stack Developer',
    date: 'Nov 09, 2026',
    status: 'Completed',
    score: 85,
  },
  {
    id: 3,
    candidate: 'Deepatharun',
    role: 'Backend Developer',
    date: 'Nov 12, 2026',
    status: 'Scheduled',
    score: null,
  },
  {
    id: 4,
    candidate: 'Vignesh',
    role: 'AI Engineer',
    date: 'Nov 13, 2026',
    status: 'Scheduled',
    score: null,
  },
]

function RecentInterviews() {
    const [selectedInterview, setSelectedInterview] = useState<
        (typeof interviews)[number] | null
    >(null)

  return (
    <section className="mb-8 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
      <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h2 className="text-lg font-bold text-gray-800">
            Recent Interviews
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Track your recent interview activities
          </p>
        </div>

        <button className="text-sm font-semibold text-purple-600 hover:text-purple-700 cursor-pointer">
          View All
        </button>
      </div>

      <div className="max-h-80 overflow-auto rounded-lg">
        <table className="w-full min-w-[650px] text-left">
          <thead>
            <tr className="border-b border-gray-100 text-xs uppercase tracking-wider text-gray-400">
              <th className="sticky top-0 z-10 bg-white pb-4 font-semibold">Candidate</th>
              <th className="sticky top-0 z-10 bg-white pb-4 font-semibold">Interview Date</th>
              <th className="sticky top-0 z-10 bg-white pb-4 font-semibold">Status</th>
              <th className="sticky top-0 z-10 bg-white pb-4 font-semibold">Score</th>
              <th className="sticky top-0 z-10 bg-white pb-4 text-center font-semibold">Action</th>
            </tr>
          </thead>

          <tbody>
            {interviews.map((interview) => (
              <tr
                key={interview.id}
                className="border-b border-gray-50 last:border-0"
              >
                <td className="py-4">
                  <p className="font-semibold text-gray-800">
                    {interview.candidate}
                  </p>
                  <p className="mt-1 text-xs text-gray-400">
                    {interview.role}
                  </p>
                </td>

                <td className="py-4 text-sm text-gray-600">
                  <span className="flex items-center gap-2">
                    <CalendarDays size={15} className="text-gray-400" />
                    {interview.date}
                  </span>
                </td>

                <td className="py-4">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      interview.status === 'Completed'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-blue-100 text-blue-700'
                    }`}
                  >
                    {interview.status}
                  </span>
                </td>

                <td className="py-4 text-sm font-semibold text-gray-800">
                  {interview.score !== null
                    ? `${interview.score}%`
                    : '--'}
                </td>

                <td className="py-4 text-center">
                    <button
                        type="button"
                        onClick={() => setSelectedInterview(interview)}
                        aria-label={`View ${interview.candidate} interview`}
                        title="View Interview"
                         className="inline-flex items-center justify-center rounded-lg border border-purple-100 p-2 text-purple-600 transition hover:border-purple-600 hover:bg-purple-600 hover:text-white cursor-pointer"
                    >
                        <Eye size={17} />
                    </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <InterviewDetailsModal
        interview={selectedInterview}
        onClose={() => setSelectedInterview(null)}
        />
    </section>
  )
}

export default RecentInterviews
