import { useState } from 'react'
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle,
  Mic,
  Video,
} from 'lucide-react'

interface InterviewQuestion {
  question: string
  expected_answer_points: string[]
}

interface InterviewSessionProps {
  role: string
  difficulty: string
  duration: string
  mode: string
  onExit: () => void
  onComplete: (
    answers: Record<number, string>,
    questions: InterviewQuestion[]
  ) => void
}


const questions = [
  {
    question: 'Explain the difference between a Python list and a tuple.',
    expected_answer_points: [
      'Lists are mutable, while tuples are immutable.',
      'Lists use square brackets, while tuples use parentheses.',
      'Lists support modification, insertion, and deletion.',
      'Tuples are generally suitable for fixed collections of data.',
    ],
  },
  {
    question: 'What are Python decorators?',
    expected_answer_points: [
      'Decorators modify or extend function behavior.',
      'They accept a function as an argument.',
      'They use wrapper functions.',
      'They are commonly applied using the @ syntax.',
    ],
  },
  {
    question: 'Explain list comprehension with an example.',
    expected_answer_points: [
      'List comprehension provides a concise way to create lists.',
      'It supports expressions and iteration.',
      'It can include conditional filtering.',
      'Example: [x * 2 for x in range(5)].',
    ],
  },
  {
    question: 'What is the difference between shallow copy and deep copy?',
    expected_answer_points: [
      'Shallow copy creates a new outer object.',
      'Nested objects remain shared in a shallow copy.',
      'Deep copy recursively copies nested objects.',
      'Python provides copy.copy() and copy.deepcopy().',
    ],
  },
  {
    question: 'Explain Python generators and yield.',
    expected_answer_points: [
      'Generators produce values lazily.',
      'The yield keyword returns a value while preserving execution state.',
      'Generators are memory efficient.',
      'They can be iterated using a for loop.',
    ],
  },
]


function InterviewSession({
  role,
  difficulty,
  duration,
  mode,
  onExit,
  onComplete,
}: InterviewSessionProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = () => {
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <div className="w-full max-w-lg rounded-2xl border border-purple-200 bg-white p-8 text-center shadow-lg">
          <CheckCircle className="mx-auto mb-4 text-green-500" size={52} />

          <h2 className="text-2xl font-bold text-gray-900">
            Interview Submitted!
          </h2>

          <p className="mt-3 text-gray-500">
            Your answers have been submitted successfully.
          </p>

          <button
            onClick={() => onComplete(answers, questions)}
            className="mt-6 rounded-lg bg-purple-600 px-6 py-3 font-semibold text-white hover:bg-purple-700 cursor-pointer"
            >
            View Interview Results
            </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Interview Session
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Answer the questions to complete your interview.
          </p>
        </div>

        <button
          onClick={onExit}
          className="flex items-center gap-2 rounded-lg border px-4 py-2 text-sm text-gray-600 hover:bg-gray-100"
        >
          <ArrowLeft size={16} />
          Exit
        </button>
      </div>

      {/* Interview Details */}
      <div className="grid grid-cols-1 gap-4 rounded-xl bg-purple-50 p-5 sm:grid-cols-4">
        <div>
          <p className="text-xs text-gray-500">Role</p>
          <p className="font-semibold text-gray-900">{role}</p>
        </div>

        <div>
          <p className="text-xs text-gray-500">Difficulty</p>
          <p className="font-semibold text-gray-900">{difficulty}</p>
        </div>

        <div>
          <p className="text-xs text-gray-500">Duration</p>
          <p className="font-semibold text-gray-900">{duration} minutes</p>
        </div>

        <div>
          <p className="text-xs text-gray-500">Interview Mode</p>
          <p className="font-semibold capitalize text-purple-700">
            {mode}
          </p>
        </div>
      </div>

      {/* Question Card */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        {/* Progress */}
        <div className="mb-6 flex items-center justify-between">
          <span className="text-sm font-semibold text-purple-700">
            Question {currentQuestion + 1} of {questions.length}
          </span>

          <span className="text-sm text-gray-500">
            {Math.round(((currentQuestion + 1) / questions.length) * 100)}%
            completed
          </span>
        </div>

        <div className="mb-6 h-2 overflow-hidden rounded-full bg-gray-100">
          <div
            className="h-full rounded-full bg-purple-600 transition-all"
            style={{
              width: `${((currentQuestion + 1) / questions.length) * 100}%`,
            }}
          />
        </div>

        {/* Question */}
        <h2 className="text-lg font-semibold text-gray-900">
          {questions[currentQuestion].question}
        </h2>

        {/* Text Mode */}
        {mode === 'text' && (
          <div className="mt-5">
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Your Answer
            </label>

            <textarea
              value={answers[currentQuestion] || ''}
              onChange={(event) =>
                setAnswers((previous) => ({
                  ...previous,
                  [currentQuestion]: event.target.value,
                }))
              }
              rows={8}
              placeholder="Type your answer here..."
              className="w-full rounded-xl border border-gray-200 p-4 text-sm outline-none transition focus:border-purple-500 focus:ring-2 focus:ring-purple-100"
            />
          </div>
        )}

        {/* Audio Mode */}
        {mode === 'audio' && (
          <div className="mt-5 rounded-xl border border-gray-200 bg-gray-50 p-8 text-center">
            <Mic className="mx-auto h-12 w-12 text-purple-600" />

            <h3 className="mt-4 text-lg font-semibold text-gray-900">
              Audio Interview
            </h3>

            <p className="mt-2 text-sm text-gray-500">
              Answer the question using your microphone.
            </p>

            <button
              type="button"
              disabled
              className="mt-5 inline-flex items-center gap-2 rounded-lg bg-purple-600 px-6 py-3 text-sm font-semibold text-white opacity-60"
            >
              <Mic size={18} />
              Recording Coming Soon
            </button>
          </div>
        )}

        {/* Video Mode */}
        {mode === 'video' && (
          <div className="mt-5 rounded-xl border border-gray-200 bg-gray-50 p-8 text-center">
            <Video className="mx-auto h-12 w-12 text-purple-600" />

            <h3 className="mt-4 text-lg font-semibold text-gray-900">
              Video Interview
            </h3>

            <p className="mt-2 text-sm text-gray-500">
              Answer the question using your camera and microphone.
            </p>

            <div className="mx-auto mt-5 flex h-48 max-w-md items-center justify-center rounded-xl bg-gray-900">
              <Video className="h-12 w-12 text-gray-400" />
            </div>

            <button
              type="button"
              disabled
              className="mt-5 inline-flex items-center gap-2 rounded-lg bg-purple-600 px-6 py-3 text-sm font-semibold text-white opacity-60"
            >
              <Video size={18} />
              Recording Coming Soon
            </button>
          </div>
        )}

        {/* Navigation */}
        <div className="mt-6 flex items-center justify-between">
          <button
            onClick={() => setCurrentQuestion((previous) => previous - 1)}
            disabled={currentQuestion === 0}
            className="flex items-center gap-2 rounded-lg border px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ArrowLeft size={16} />
            Previous
          </button>

          {currentQuestion === questions.length - 1 ? (
            <button
              onClick={handleSubmit}
              className="rounded-lg bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-purple-700"
            >
              Submit Interview
            </button>
          ) : (
            <button
              onClick={() => setCurrentQuestion((previous) => previous + 1)}
              className="flex items-center gap-2 rounded-lg bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-purple-700"
            >
              Next
              <ArrowRight size={16} />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default InterviewSession
