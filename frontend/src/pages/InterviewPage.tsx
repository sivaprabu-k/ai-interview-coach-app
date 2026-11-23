import { useEffect, useState } from 'react'
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
// import { evaluateAnswer } from '../services/answerEvaluationService'
import {
  getDocuments,
  generateDocumentInterview,
} from '../services/documentService'
import type { Document } from '../types/document'
import type {
  InterviewEvaluation,
  InterviewQuestion,
} from '../types/evaluation'

import { getUserProfile } from '../services/profileService'
import type { UserProfile } from '../types/profile'
import { generateAIQuestions } from '../services/aiQuestionService'
import { createInterview, createInterviewSession, submitSessionAnswer} from '../services/interviewSessionService'


function InterviewPage() {
  const [showSetup, setShowSetup] = useState(false)
  const [role, setRole] = useState('Python Developer')
  const [difficulty, setDifficulty] = useState('Intermediate')
  const [duration, setDuration] = useState('30')
  const [showSession, setShowSession] = useState(false)
  const [interviewMode, setInterviewMode] = useState('text')
  const [showResults, setShowResults] = useState(false)

  const [interviewType, setInterviewType] = useState<'general' | 'document'>(
    'general',
  )
  const [documents, setDocuments] = useState<Document[]>([])
  const [selectedDocumentId, setSelectedDocumentId] = useState('')
  const [questionCount, setQuestionCount] = useState('5')
  const [generatedQuestions, setGeneratedQuestions] =
    useState<InterviewQuestion[] | null>(null)

  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [documentError, setDocumentError] = useState<string | null>(null)

  const [isEvaluating, setIsEvaluating] = useState(false)
  const [evaluationError, setEvaluationError] = useState<string | null>(null)
  const [evaluation, setEvaluation] =
    useState<InterviewEvaluation | null>(null)

  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [sessionId, setSessionId] = useState<number | null>(null)

  useEffect(() => {
    const loadUserProfile = async () => {
      try {
        const profile = await getUserProfile()

        if (profile) {
          setUserProfile(profile)
          setRole(profile.target_roles[0] || 'Python Developer')
          setDifficulty(profile.preferred_difficulty)
          setQuestionCount(String(profile.preferred_question_count))
        }
      } catch (error) {
        console.error('Failed to load career profile:', error)
      }
    }

    void loadUserProfile()
  }, [])

  useEffect(() => {
    if (!showSetup || interviewType !== 'document') return

    let isActive = true

    const loadDocuments = async () => {
      setIsLoadingDocuments(true)
      setDocumentError(null)

      try {
        const result = await getDocuments()

        if (isActive) {
          const processedDocuments = result.filter(
            (document) => document.status === 'processed',
          )

          setDocuments(processedDocuments)

          setSelectedDocumentId((current) => {
            if (
              current &&
              processedDocuments.some(
                (document) => String(document.document_id) === current,
              )
            ) {
              return current
            }

            return processedDocuments.length > 0
              ? String(processedDocuments[0].document_id)
              : ''
          })
        }
      } catch (error) {
        if (isActive) {
          setDocumentError(
            error instanceof Error
              ? error.message
              : 'Failed to load documents.',
          )
        }
      } finally {
        if (isActive) {
          setIsLoadingDocuments(false)
        }
      }
    }

    loadDocuments()

    return () => {
      isActive = false
    }
  }, [showSetup, interviewType])


  const handleGenerateGeneralInterview = async () => {
    setIsGenerating(true)
    setDocumentError(null)

    try {
      const difficultyMapping: Record<string, 'easy' | 'medium' | 'hard'> = {
        Beginner: 'easy',
        Intermediate: 'medium',
        Advanced: 'hard',
      }

      const mappedDifficulty = difficultyMapping[difficulty] ?? 'medium'

      // Step 1: Create interview
      const interview = await createInterview({
        role,
        difficulty: mappedDifficulty,
      })

      // Step 2: Generate questions linked to the interview
      await generateAIQuestions({
        role,
        experience_years: userProfile?.years_of_experience ?? undefined,
        skills: userProfile?.technical_skills?.length
          ? userProfile.technical_skills
          : undefined,
        difficulty: mappedDifficulty,
        interview_id: interview.id,
        number_of_questions: Number(questionCount),
      })

      // Create the interview session using the generated questions.
      const session = await createInterviewSession(interview.id)

      setSessionId(session.id)
      setGeneratedQuestions(session.questions)
      setShowSetup(false)
      setShowSession(true)
    } catch (error) {
      setDocumentError(
        error instanceof Error
          ? error.message
          : 'Failed to generate interview questions.',
      )
    } finally {
      setIsGenerating(false)
    }
  }

  const handleGenerateDocumentInterview = async () => {
    if (!selectedDocumentId) {
      setDocumentError('Please select a processed document.')
      return
    }

    const selectedDocument = documents.find(
      (document) =>
        String(document.document_id) === selectedDocumentId,
    )

    if (!selectedDocument) {
      setDocumentError('Selected document was not found.')
      return
    }

    setIsGenerating(true)
    setDocumentError(null)

    try {
      const response = await generateDocumentInterview({
        document_id: Number(selectedDocumentId),
        difficulty,
        question_count: Number(questionCount),
      })

      setGeneratedQuestions(response.questions)
      setRole(selectedDocument.filename)
      setShowSetup(false)
      setShowSession(true)
    } catch (error) {
      setDocumentError(
        error instanceof Error
          ? error.message
          : 'Failed to generate interview questions.',
      )
    } finally {
      setIsGenerating(false)
    }
  }

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
      if (sessionId === null) {
        throw new Error('Interview session not found. Please start again.')
      }

      const answeredQuestions = questions
        .map((item, index) => ({
          ...item,
          user_answer: answers[index]?.trim() ?? '',
          index,
        }))

      if (
        answeredQuestions.length === 0 ||
        answeredQuestions.some((item) => !item.user_answer)
      ) {
        throw new Error('Please answer all questions before completing the interview.')
      }

      const results = []

      for (const item of answeredQuestions) {
        if (typeof item.id !== 'number') {
          throw new Error('A valid database question ID is missing.')
        }

        const response = await submitSessionAnswer(sessionId, {
          generated_question_id: item.id,
          user_answer: item.user_answer,
        })

        if (!response.evaluation) {
          throw new Error('Answer evaluation failed.')
        }

        results.push(response.evaluation)
      }

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

  const handleStartNewInterview = () => {
    setShowResults(false)
    setShowSession(false)
    setEvaluation(null)
    setEvaluationError(null)
    setIsEvaluating(false)

    setRole(userProfile?.target_roles[0] || 'Python Developer')
    setDifficulty(userProfile?.preferred_difficulty || 'Intermediate')
    setDuration('30')
    setInterviewMode('text')

    setInterviewType('general')
    setSelectedDocumentId('')
    setQuestionCount(String(userProfile?.preferred_question_count ?? 10))
    setGeneratedQuestions(null)
    setDocumentError(null)

    setShowSetup(true)
  }

  const handleBackToSetup = () => {
    setShowResults(false)
    setShowSession(false)
    setShowSetup(true)
  }

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

        {evaluation && <InterviewResults evaluation={evaluation} />}
      </div>
    )
  }

  // Interview session screen.
  if (showSession) {
    return (
      <InterviewSession
        role={role}
        difficulty={difficulty}
        duration={duration}
        mode={interviewMode}
        questions={generatedQuestions ?? undefined}
        onExit={() => setShowSession(false)}
        onComplete={handleInterviewComplete}
      />
    )
  }

  // Interview landing page.
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
                  setInterviewType('general')
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
        <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/50 p-4">
          <div className="my-auto w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-800">
                Setup Your Interview
              </h2>
              <p className="mt-1 text-sm text-gray-500">
                Customize your AI interview session.
              </p>
            </div>

            <div className="space-y-5">
              {/* Interview Type */}
              <div>
                <label className="mb-3 block text-sm font-medium text-gray-700">
                  Interview Type
                </label>

                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setInterviewType('general')
                      setDocumentError(null)
                    }}
                    className={`rounded-xl border p-3 text-sm font-semibold transition ${
                      interviewType === 'general'
                        ? 'border-purple-600 bg-purple-50 text-purple-700'
                        : 'border-gray-200 text-gray-600 hover:border-purple-300'
                    }`}
                  >
                    General Interview
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setInterviewType('document')
                      setDocumentError(null)
                    }}
                    className={`rounded-xl border p-3 text-sm font-semibold transition ${
                      interviewType === 'document'
                        ? 'border-purple-600 bg-purple-50 text-purple-700'
                        : 'border-gray-200 text-gray-600 hover:border-purple-300'
                    }`}
                  >
                    Document Interview
                  </button>
                </div>
              </div>

              {/* General Interview Mode */}
              {interviewType === 'general' && (
                <>
                  {userProfile && (
                    <div className="rounded-lg border border-purple-100 bg-purple-50 p-3 text-sm text-purple-700">
                      Using your saved Career Profile defaults. You can change them before starting.
                    </div>
                  )}
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
                </>
              )}

              {/* Document Selection */}
              {interviewType === 'document' && (
                <>
                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                      Select Processed Document
                    </label>

                    {isLoadingDocuments ? (
                      <p className="text-sm text-gray-500">
                        Loading your documents...
                      </p>
                    ) : (
                      <select
                        value={selectedDocumentId}
                        onChange={(e) =>
                          setSelectedDocumentId(e.target.value)
                        }
                        disabled={documents.length === 0}
                        className="w-full rounded-lg border border-gray-200 p-3 text-sm outline-none focus:border-purple-500 disabled:bg-gray-100"
                      >
                        <option value="">Select a document</option>
                        {documents.map((document) => (
                          <option
                            key={document.document_id}
                            value={String(document.document_id)}
                          >
                            {document.filename}
                          </option>
                        ))}
                      </select>
                    )}

                    {!isLoadingDocuments && documents.length === 0 && (
                      <p className="mt-2 text-xs text-gray-500">
                        No processed documents available. Upload and process
                        a document first.
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                      Number of Questions
                    </label>

                    <select
                      value={questionCount}
                      onChange={(e) => setQuestionCount(e.target.value)}
                      className="w-full rounded-lg border border-gray-200 p-3 text-sm outline-none focus:border-purple-500"
                    >
                      <option value="5">5 Questions</option>
                      <option value="10">10 Questions</option>
                      <option value="15">15 Questions</option>
                      <option value="20">20 Questions</option>
                    </select>
                  </div>
                </>
              )}

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

              {/* Number of Questions */}
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Number of Questions
                </label>

                <select
                  value={questionCount}
                  onChange={(e) => setQuestionCount(e.target.value)}
                  className="w-full rounded-lg border border-gray-200 p-3 text-sm outline-none focus:border-purple-500"
                >
                  {[5, 10, 15, 20].map((count) => (
                    <option key={count} value={count}>
                      {count} Questions
                    </option>
                  ))}
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

              {documentError && (
                <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
                  {documentError}
                </div>
              )}
            </div>

            {/* Modal Actions */}
            <div className="mt-8 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowSetup(false)}
                disabled={isGenerating}
                className="cursor-pointer rounded-lg border border-gray-200 px-5 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>

              <button
                type="button"
                disabled={
                  isGenerating ||
                  (interviewType === 'document' &&
                    (isLoadingDocuments || documents.length === 0))
                }
                onClick={() => {
                  if (interviewType === 'document') {
                    void handleGenerateDocumentInterview()
                  } else {
                    void handleGenerateGeneralInterview()
                  }
                }}
                className="cursor-pointer rounded-lg bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isGenerating
                  ? 'Generating Questions...'
                  : interviewType === 'document'
                    ? 'Generate Interview'
                    : 'Generate Questions'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default InterviewPage
