import QueueDepth from '../components/QueueDepth'
import TaskStream from '../components/TaskStream'

export default function Home() {
  return (
    <main className="p-4">
      <h1 className="text-2xl mb-4">NovaOS Control Panel</h1>
      <QueueDepth />
      <TaskStream />
    </main>
  )
}