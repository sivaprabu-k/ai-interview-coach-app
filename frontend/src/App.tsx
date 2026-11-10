import Sidebar from './components/layout/Sidebar'

function App() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold text-gray-800">
          Dashboard
        </h1>

        <p className="mt-2 text-gray-500">
          Welcome back! Here's your interview overview.
        </p>
      </main>
    </div>
  )
}

export default App