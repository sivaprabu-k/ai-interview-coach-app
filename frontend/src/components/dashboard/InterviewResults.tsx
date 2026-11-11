import {
  Award,
  Brain,
  MessageSquare,
  Lightbulb,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import { useState } from 'react'
import type { InterviewEvaluation } from '../../types/evaluation'

interface InterviewResultsProps {
  evaluation?: InterviewEvaluation
}

const defaultEvaluation: InterviewEvaluation = {
  candidate: 'Siva',
  role: 'Python Developer',
  overallScore: 92,
  skills: [
    { name: 'Technical Knowledge', score: 95 },
    { name: 'Communication', score: 88 },
    { name: 'Problem Solving', score: 90 },
    { name: 'Confidence', score: 85 },
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
  questionDetails: [],
}

const skillIcons = [
  Brain,
  MessageSquare,
  Lightbulb,
  TrendingUp,
]

function InterviewResults({
  evaluation = defaultEvaluation,
}: InterviewResultsProps) {
  const [expandedQuestions, setExpandedQuestions] = useState<number[]>([])

  const toggleQuestion = (index: number) => {
    setExpandedQuestions((previous) =>
      previous.includes(index)
        ? previous.filter((item) => item !== index)
        : [...previous, index],
    )
  }

  const getInterviewSummary = () => {
    if (evaluation.overallScore >= 85) {
      return 'Excellent performance! You demonstrated strong technical knowledge and good problem-solving skills. Continue practising advanced concepts to improve further.'
    }

    if (evaluation.overallScore >= 70) {
      return 'Good performance! You have a solid foundation. Focus on the improvement areas identified below to strengthen your interview readiness.'
    }

    return 'There is room for improvement. Review the suggested answers, strengthen your fundamentals, and practise similar questions regularly.'
  }
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
            {evaluation.overallScore >= 85
              ? 'Excellent Performance'
              : evaluation.overallScore >= 70
                ? 'Good Performance'
                : 'Needs Improvement'}
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
            {evaluation.skills.map((skill, index) => {
              const Icon = skillIcons[index % skillIcons.length]

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

      {/* Interview Summary */}
      <div className="mt-8 rounded-xl border border-purple-100 bg-purple-50 p-6">
        <div className="mb-3 flex items-center gap-2">
          <Award size={22} className="text-purple-600" />
          <h3 className="font-bold text-purple-800">
            Interview Summary
          </h3>
        </div>

        <p className="text-sm leading-7 text-gray-700">
          {getInterviewSummary()}
        </p>

        <p className="mt-4 text-sm font-semibold text-purple-700">
          Keep practising and track your progress!
        </p>
      </div>

      {/* Question-by-Question Evaluation */}
      {evaluation.questionDetails.length > 0 && (
        <div className="mt-8">
          <h3 className="mb-5 text-lg font-bold text-gray-800">
            Detailed Question Feedback
          </h3>

          <div className="space-y-4">
            {evaluation.questionDetails.map((item, index) => {
              const isExpanded = expandedQuestions.includes(index)

              return (
                <div
                  key={index}
                  className="overflow-hidden rounded-xl border border-gray-200"
                >
                  <button
                    type="button"
                    onClick={() => toggleQuestion(index)}
                    className="flex w-full items-center justify-between gap-4 p-5 text-left hover:bg-gray-50"
                  >
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-purple-600">
                        QUESTION {index + 1}
                      </p>

                      <p className="mt-2 font-medium text-gray-800">
                        {item.question}
                      </p>
                    </div>

                    <div className="flex shrink-0 items-center gap-3">
                      <span className="rounded-full bg-purple-100 px-3 py-1 text-sm font-bold text-purple-700">
                        {item.score}%
                      </span>

                      {isExpanded ? (
                        <ChevronUp size={20} />
                      ) : (
                        <ChevronDown size={20} />
                      )}
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="space-y-5 border-t border-gray-200 p-5">
                      <div>
                        <h4 className="mb-2 text-sm font-semibold text-gray-700">
                          Your Answer
                        </h4>
                        <p className="whitespace-pre-wrap rounded-lg bg-gray-50 p-4 text-sm text-gray-600">
                          {item.user_answer}
                        </p>
                      </div>

                      <div>
                        <h4 className="mb-2 text-sm font-semibold text-gray-700">
                          AI Feedback
                        </h4>
                        <p className="text-sm leading-6 text-gray-600">
                          {item.feedback}
                        </p>
                      </div>

                      <div>
                        <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-green-700">
                          <CheckCircle size={17} />
                          Strengths
                        </h4>
                        <ul className="space-y-2">
                          {item.strengths.map((strength, strengthIndex) => (
                            <li
                              key={strengthIndex}
                              className="text-sm text-gray-600"
                            >
                              ✓ {strength}
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-orange-700">
                          <AlertCircle size={17} />
                          Areas to Improve
                        </h4>
                        <ul className="space-y-2">
                          {item.areas_to_improve.map((area, areaIndex) => (
                            <li
                              key={areaIndex}
                              className="text-sm text-gray-600"
                            >
                              • {area}
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <h4 className="mb-2 flex items-center gap-2 text-sm font-semibold text-purple-700">
                          <Lightbulb size={17} />
                          Suggested Answer
                        </h4>
                        <p className="whitespace-pre-wrap rounded-lg bg-purple-50 p-4 text-sm leading-6 text-gray-700">
                          {item.suggested_answer}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </section>
  )
}

export default InterviewResults
