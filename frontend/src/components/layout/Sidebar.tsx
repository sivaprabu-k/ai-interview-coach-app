import { useState } from 'react'
import {
  LayoutDashboard,
  Video,
  BarChart3,
  Users,
  CircleHelp,
  Settings,
  LogOut,
  BrainCircuit,
} from 'lucide-react'

const menuItems = [
  { name: 'Dashboard', icon: LayoutDashboard },
  { name: 'Interview', icon: Video },
  { name: 'Insights', icon: BarChart3 },
  { name: 'Talent', icon: Users },
  { name: 'FAQ', icon: CircleHelp },
  { name: 'Settings', icon: Settings },
]

function Sidebar() {
  const [activeItem, setActiveItem] = useState('Dashboard')

  return (
    <aside className="sticky top-0 flex h-screen w-64 shrink-0 flex-col overflow-y-auto bg-[#171729] px-5 py-6 text-white">
      {/* Logo */}
      <div className="mb-10 flex items-center gap-3 px-2">
        <div className="rounded-xl bg-purple-600 p-2">
          <BrainCircuit size={25} />
        </div>

        <div>
          <h2 className="text-lg font-bold">Interview AI</h2>
          <p className="text-xs text-gray-400">Smart Interview Coach</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="min-h-0 flex-1 space-y-2">
        <p className="mb-4 px-3 text-xs font-semibold uppercase tracking-wider text-gray-500">
          Menu
        </p>

        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = activeItem === item.name

          return (
            <button
              key={item.name}
              onClick={() => setActiveItem(item.name)}
              className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm transition ${
                isActive
                  ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/30'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <Icon size={19} />
              <span>{item.name}</span>
            </button>
          )
        })}
      </nav>

      <button className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-gray-400 transition hover:bg-red-500/10 hover:text-red-400">
        <LogOut size={19} />
        <span>Logout</span>
      </button>
    </aside>
  )
}

export default Sidebar