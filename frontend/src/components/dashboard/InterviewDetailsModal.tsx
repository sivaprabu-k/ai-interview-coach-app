import { X, CalendarDays, BriefcaseBusiness, User, Award } from 'lucide-react'

interface Interview {
  id: number
  candidate: string
  role: string
  date: string
  status: string
  score: number | null
}

interface InterviewDetailsModalProps {
  interview: Interview | null
  onClose: () => void
}

function InterviewDetailsModal({
  interview,
  onClose,
}: InterviewDetailsModalProps) {
  if (!interview) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="interview-modal-title"
        className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2
              id="interview-modal-title"
              className="text-xl font-bold text-gray-800"
            >
              Interview Details
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              Candidate interview information
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close modal"
            className="rounded-lg p-2 text-gray-500 transition hover:bg-gray-100"
          >
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4">
          <div className="flex items-center gap-3 rounded-xl bg-purple-50 p-4">
            <User className="text-purple-600" size={22} />
            <div>
              <p className="text-xs text-gray-500">Candidate</p>
              <p className="font-semibold text-gray-800">
                {interview.candidate}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-xl border border-gray-100 p-4">
              <BriefcaseBusiness className="mb-2 text-purple-600" size={20} />
              <p className="text-xs text-gray-500">Role</p>
              <p className="mt-1 font-medium text-gray-800">{interview.role}</p>
            </div>

            <div className="rounded-xl border border-gray-100 p-4">
              <CalendarDays className="mb-2 text-purple-600" size={20} />
              <p className="text-xs text-gray-500">Interview Date</p>
              <p className="mt-1 font-medium text-gray-800">{interview.date}</p>
            </div>
          </div>

          <div className="rounded-xl border border-gray-100 p-4">
            <p className="mb-2 text-xs text-gray-500">Status</p>
            <span
              className={`rounded-full px-3 py-1 text-xs font-medium ${
                interview.status === 'Completed'
                  ? 'bg-green-100 text-green-700'
                  : 'bg-blue-100 text-blue-700'
              }`}
            >
              {interview.status}
            </span>
          </div>

          <div className="rounded-xl border border-gray-100 p-4">
            <div className="mb-2 flex items-center gap-2">
              <Award size={20} className="text-purple-600" />
              <p className="text-sm font-semibold text-gray-700">
                Interview Score
              </p>
            </div>

            {interview.score !== null ? (
              <p className="text-3xl font-bold text-purple-600">
                {interview.score}%
              </p>
            ) : (
              <p className="text-sm text-gray-500">
                Evaluation will be available after interview completion.
              </p>
            )}
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="mt-6 w-full rounded-lg bg-purple-600 py-3 font-medium text-white transition hover:bg-purple-700 cursor-pointer"
        >
          Close
        </button>
      </div>
    </div>
  )
}

export default InterviewDetailsModal