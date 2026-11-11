
import { useState } from 'react'
import {
  Video,
  Clock,
  BriefcaseBusiness,
  BarChart3,
  ArrowRight,
  MessageSquare,
  Mic,
} from 'lucide-react'

import InterviewSession from '../components/interview/InterviewSession'
import InterviewResults from '../components/dashboard/InterviewResults'
import { evaluateAnswer } from '../services/answerEvaluationService'
import type {
  InterviewEvaluation,
  InterviewQuestion,
} from '../types/evaluation'

function InterviewPage() {
  const [showSetup, setShowSetup] = useState(false)
  const [role, setRole] = useState('Python Developer')
  const [difficulty, setDifficulty] = useState('Intermediate')
  const [duration, setDuration] = useState('30')
  const [showSession, setShowSession] = useState(false)
  const [interviewMode, setInterviewMode] = useState('text')
  const [showResults, setShowResults] = useState(false)

  const [isEvaluating, setIsEvaluating] = useState(false)
  const [evaluationError, setEvaluationError] = useState<string | null>(null)
  const [evaluation, setEvaluation] =
    useState<InterviewEvaluation | null>(null)

  // Evaluate interview answers
  const handleInterviewComplete = async (
    answers: Record<number, string>,
    questions: InterviewQuestion[],
  ) => {
    setShowSession(false)
    setShowResults(true)
    setIsEvaluating(true)
    setEvaluationError(null)
    setEvaluation(null)

    try {
      const answeredQuestions = questions
        .map((item, index) => ({
          ...item,
          user_answer: answers[index]?.trim() ?? '',
          index,
        }))
        .filter((item) => item.user_answer.length > 0)

      if (answeredQuestions.length === 0) {
        throw new Error('Please answer at least one question.')
      }

      const results = await Promise.all(
        answeredQuestions.map((item) =>
          evaluateAnswer({
            question: item.question,
            expected_answer_points: item.expected_answer_points,
            user_answer: item.user_answer,
          }),
        ),
      )

      const overallScore = Math.round(
        results.reduce((total, item) => total + item.score, 0) /
          results.length,
      )

      setEvaluation({
        candidate: 'Candidate',
        role,
        overallScore,

        skills: results.map((item, index) => ({
          name: `Question ${answeredQuestions[index].index + 1}`,
          score: item.score,
        })),

        strengths: [
          ...new Set(results.flatMap((item) => item.strengths)),
        ],

        improvements: [
          ...new Set(results.flatMap((item) => item.areas_to_improve)),
        ],

        questionDetails: results.map((item, index) => ({
          question: answeredQuestions[index].question,
          user_answer: answeredQuestions[index].user_answer,
          score: item.score,
          strengths: item.strengths,
          areas_to_improve: item.areas_to_improve,
          suggested_answer: item.suggested_answer,
          feedback: item.feedback,
        })),
      })
    } catch (error) {
      setEvaluationError(
        error instanceof Error
          ? error.message
          : 'Failed to evaluate interview answers.',
      )
    } finally {
      setIsEvaluating(false)
    }
  }

  // Start a completely new interview
  const handleStartNewInterview = () => {
    setShowResults(false)
    setShowSession(false)
    setEvaluation(null)
    setEvaluationError(null)
    setIsEvaluating(false)

    setRole('Python Developer')
    setDifficulty('Intermediate')
    setDuration('30')
    setInterviewMode('text')

    setShowSetup(true)
  }

  // Return to setup while retaining configuration
  const handleBackToSetup = () => {
    setShowResults(false)
    setShowSession(false)
    setShowSetup(true)
  }

  // Results screen
  if (showResults) {
    return (
      <div className="space-y-6">
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handleStartNewInterview}
            className="rounded-lg bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-purple-700"
          >
            Start New Interview
          </button>

          <button
            type="button"
            onClick={handleBackToSetup}
            className="rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-semibold text-gray-700 transition hover:bg-gray-50"
          >
            Back to Setup
          </button>
        </div>

        {isEvaluating && (
          <div className="rounded-xl bg-blue-50 p-6 text-center text-blue-700">
            Evaluating your interview answers...
          </div>
        )}

        {evaluationError && (
          <div className="rounded-xl bg-red-50 p-6 text-center text-red-700">
            {evaluationError}
          </div>
        )}

        {evaluation && (
          <InterviewResults evaluation={evaluation} />
        )}
      </div>
    )
  }

  // Interview session screen
  if (showSession) {
    return (
      <InterviewSession
        role={role}
        difficulty={difficulty}
        duration={duration}
        mode={interviewMode}
        onExit={() => setShowSession(false)}
        onComplete={handleInterviewComplete}
      />
    )
  }

  // Interview landing page
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">
          Interview Session
        </h1>

        <p className="mt-2 text-sm text-gray-500">
          Prepare, practice, and improve your interview performance with AI.
        </p>
      </div>

      {/* Hero Section */}
      <div className="rounded-2xl bg-gradient-to-r from-purple-700 to-indigo-600 p-8 text-white shadow-lg">
        <div className="max-w-2xl">
          <span className="rounded-full bg-white/20 px-3 py-1 text-xs font-medium">
            AI Interview Coach
          </span>

          <h2 className="mt-5 text-3xl font-bold">
            Ready for your next interview?
          </h2>

          <p className="mt-3 text-sm leading-6 text-purple-100">
            Practice real-world interview questions, receive AI-powered
            feedback, and improve your technical and communication skills.
          </p>

          <button
            type="button"
            onClick={() => setShowSetup(true)}
            className="mt-6 inline-flex cursor-pointer items-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-semibold text-purple-700 transition hover:bg-purple-50"
          >
            Start New Interview
            <ArrowRight size={18} />
          </button>
        </div>
      </div>

      {/* Interview Overview */}
      <div>
        <h2 className="mb-5 text-lg font-bold text-gray-800">
          Interview Overview
        </h2>

        <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
          <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
            <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-purple-100 text-purple-600">
              <Video size={22} />
            </div>

            <h3 className="font-semibold text-gray-800">
              Technical Interview
            </h3>

            <p className="mt-2 text-sm text-gray-500">
              Practice Python, React, SQL, APIs, and backend development.
            </p>
          </div>

          <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
            <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-blue-100 text-blue-600">
              <Clock size={22} />
            </div>

            <h3 className="font-semibold text-gray-800">
              Timed Practice
            </h3>

            <p className="mt-2 text-sm text-gray-500">
              Improve your confidence with structured interview sessions.
            </p>
          </div>

          <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
            <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-green-100 text-green-600">
              <BarChart3 size={22} />
            </div>

            <h3 className="font-semibold text-gray-800">
              AI Evaluation
            </h3>

            <p className="mt-2 text-sm text-gray-500">
              Understand your strengths and areas for improvement.
            </p>
          </div>
        </div>
      </div>

      {/* Recommended Interview Roles */}
      <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-bold text-gray-800">
          Recommended Interview Roles
        </h2>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {['Python Developer', 'Full Stack Developer'].map(
            (recommendedRole) => (
              <button
                key={recommendedRole}
                type="button"
                onClick={() => {
                  setRole(recommendedRole)
                  setShowSetup(true)
                }}
                className="flex cursor-pointer items-center justify-between rounded-lg border border-gray-100 p-4 text-left transition hover:border-purple-300 hover:bg-purple-50"
              >
                <div className="flex items-center gap-3">
                  <BriefcaseBusiness
                    className="text-purple-600"
                    size={20}
                  />

                  <span className="text-sm font-semibold text-gray-700">
                    {recommendedRole}
                  </span>
                </div>

                <ArrowRight size={18} className="text-gray-400" />
              </button>
            ),
          )}
        </div>
      </div>

      {/* Interview Setup Modal */}
      {showSetup && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-800">
                Setup Your Interview
              </h2>

              <p className="mt-1 text-sm text-gray-500">
                Customize your AI interview session.
              </p>
            </div>

            <div className="space-y-5">
              {/* Interview Mode */}
              <div>
                <label className="mb-3 block text-sm font-medium text-gray-700">
                  Interview Mode
                </label>

                <div className="grid grid-cols-3 gap-3">
                  {[
                    { id: 'text', label: 'Text', icon: MessageSquare },
                    { id: 'audio', label: 'Audio', icon: Mic },
                    { id: 'video', label: 'Video', icon: Video },
                  ].map((mode) => {
                    const Icon = mode.icon

                    return (
                      <button
                        key={mode.id}
                        type="button"
                        onClick={() => setInterviewMode(mode.id)}
                        className={`rounded-xl border p-4 text-center transition ${
                          interviewMode === mode.id
                            ? 'border-purple-600 bg-purple-50 text-purple-700'
                            : 'border-gray-200 text-gray-600 hover:border-purple-300'
                        }`}
                      >
                        <Icon className="mx-auto h-6 w-6" />

                        <div className="mt-2 text-sm font-semibold">
                          {mode.label}
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Interview Role */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Interview Role
                </label>

                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full rounded-lg border border-gray-200 p-3 text-sm outline-none focus:border-purple-500"
                >
                  <option>Python Developer</option>
                  <option>Full Stack Developer</option>
                  <option>Backend Developer</option>
                  <option>AI Engineer</option>
                  <option>Frontend Developer</option>
                </select>
              </div>

              {/* Difficulty */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Difficulty Level
                </label>

                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="w-full rounded-lg border border-gray-200 p-3 text-sm outline-none focus:border-purple-500"
                >
                  <option>Beginner</option>
                  <option>Intermediate</option>
                  <option>Advanced</option>
                </select>
              </div>

              {/* Duration */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Interview Duration
                </label>

                <select
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  className="w-full rounded-lg border border-gray-200 p-3 text-sm outline-none focus:border-purple-500"
                >
                  <option value="15">15 Minutes</option>
                  <option value="30">30 Minutes</option>
                  <option value="45">45 Minutes</option>
                  <option value="60">60 Minutes</option>
                </select>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="mt-8 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowSetup(false)}
                className="cursor-pointer rounded-lg border border-gray-200 px-5 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={() => {
                  setShowSetup(false)
                  setShowSession(true)
                }}
                className="cursor-pointer rounded-lg bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-purple-700"
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default InterviewPage
