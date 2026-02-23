import React, { useState } from 'react';
import { Calendar } from 'lucide-react';

const GanttChart = () => {
  const [hoveredTask, setHoveredTask] = useState(null);

  const tasks = [
    { id: 1, name: 'Literature Review & Requirements Analysis', phase: 'Research', start: 1, duration: 2, color: 'bg-blue-500' },
    { id: 2, name: 'System Architecture Design', phase: 'Design', start: 2, duration: 2, color: 'bg-purple-500' },
    { id: 3, name: 'Accelerometer Sensor Specification', phase: 'Design', start: 3, duration: 2, color: 'bg-purple-500' },
    { id: 4, name: 'ASIC Circuit Design (Analog Frontend)', phase: 'Design', start: 4, duration: 3, color: 'bg-purple-500' },
    { id: 5, name: 'Digital Signal Processing Block Design', phase: 'Design', start: 5, duration: 3, color: 'bg-purple-500' },
    { id: 6, name: 'Power Management Circuit Design', phase: 'Design', start: 6, duration: 2, color: 'bg-indigo-500' },
    { id: 7, name: 'Schematic Design & Simulation', phase: 'Implementation', start: 7, duration: 2, color: 'bg-green-500' },
    { id: 8, name: 'Layout Design & DRC/LVS Verification', phase: 'Implementation', start: 9, duration: 2, color: 'bg-green-500' },
    { id: 9, name: 'Post-Layout Simulation', phase: 'Testing', start: 11, duration: 1, color: 'bg-yellow-500' },
    { id: 10, name: 'Algorithm Development (Heart Rate Extraction)', phase: 'Implementation', start: 8, duration: 3, color: 'bg-green-500' },
    { id: 11, name: 'Power Consumption Analysis & Optimization', phase: 'Testing', start: 11, duration: 2, color: 'bg-yellow-500' },
    { id: 12, name: 'Prototype PCB Design', phase: 'Implementation', start: 12, duration: 2, color: 'bg-green-500' },
    { id: 13, name: 'Testing & Validation', phase: 'Testing', start: 13, duration: 2, color: 'bg-yellow-500' },
    { id: 14, name: 'Performance Benchmarking', phase: 'Testing', start: 14, duration: 1, color: 'bg-yellow-500' },
    { id: 15, name: 'Documentation & Report Writing', phase: 'Documentation', start: 13, duration: 3, color: 'bg-red-500' },
    { id: 16, name: 'Final Presentation Preparation', phase: 'Documentation', start: 15, duration: 2, color: 'bg-red-500' },
  ];

  const weeks = Array.from({ length: 16 }, (_, i) => i + 1);
  const phases = ['Research', 'Design', 'Implementation', 'Testing', 'Documentation'];
  const phaseColors = {
    'Research': 'text-blue-600',
    'Design': 'text-purple-600',
    'Implementation': 'text-green-600',
    'Testing': 'text-yellow-600',
    'Documentation': 'text-red-600'
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl shadow-2xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Calendar className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-800">16-Week Project Timeline</h1>
        </div>
        <h2 className="text-xl text-gray-600 ml-11">Energy Efficient ASIC Accelerometer for Fetal & Heart Rate Monitoring</h2>
      </div>

      {/* Phase Legend */}
      <div className="mb-6 p-4 bg-white rounded-lg shadow-md">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Project Phases:</h3>
        <div className="flex flex-wrap gap-4">
          {phases.map(phase => (
            <div key={phase} className="flex items-center gap-2">
              <div className={w-4 h-4 rounded ${tasks.find(t => t.phase === phase)?.color}}></div>
              <span className={text-sm font-medium ${phaseColors[phase]}}>{phase}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Gantt Chart */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <div className="min-w-max">
            {/* Header */}
            <div className="flex border-b-2 border-gray-300 bg-gray-50">
              <div className="w-80 p-4 font-semibold text-gray-700 border-r-2 border-gray-300">
                Task Name
              </div>
              <div className="flex flex-1">
                {weeks.map(week => (
                  <div key={week} className="w-16 p-2 text-center text-sm font-medium text-gray-600 border-r border-gray-200">
                    W{week}
                  </div>
                ))}
              </div>
            </div>

            {/* Tasks */}
            {tasks.map((task, idx) => (
              <div
                key={task.id}
                className={`flex border-b border-gray-200 hover:bg-blue-50 transition-colors ${
                  hoveredTask === task.id ? 'bg-blue-50' : idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                }`}
                onMouseEnter={() => setHoveredTask(task.id)}
                onMouseLeave={() => setHoveredTask(null)}
              >
                <div className="w-80 p-4 border-r border-gray-200">
                  <div className="font-medium text-gray-800 text-sm">{task.name}</div>
                  <div className={text-xs mt-1 ${phaseColors[task.phase]}}>{task.phase}</div>
                </div>
                <div className="flex flex-1 relative">
                  {weeks.map(week => (
                    <div key={week} className="w-16 border-r border-gray-100 relative">
                      {week >= task.start && week < task.start + task.duration && (
                        <div
                          className={absolute inset-y-1 inset-x-1 ${task.color} rounded shadow-md hover:shadow-lg transition-shadow}
                          style={{
                            left: week === task.start ? '4px' : '0',
                            right: week === task.start + task.duration - 1 ? '4px' : '0'
                          }}
                        >
                          {week === task.start && (
                            <div className="text-white text-xs font-semibold px-2 py-1 truncate">
                              {task.duration}w
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Milestones */}
      <div className="mt-6 p-4 bg-white rounded-lg shadow-md">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Key Milestones:</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="flex items-start gap-2">
            <div className="w-2 h-2 rounded-full bg-purple-500 mt-1.5"></div>
            <div>
              <span className="font-medium text-gray-700">Week 7:</span>
              <span className="text-gray-600 text-sm ml-1">Design Phase Complete</span>
            </div>
          </div>
          <div className="flex items-start gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 mt-1.5"></div>
            <div>
              <span className="font-medium text-gray-700">Week 11:</span>
              <span className="text-gray-600 text-sm ml-1">Implementation Complete</span>
            </div>
          </div>
          <div className="flex items-start gap-2">
            <div className="w-2 h-2 rounded-full bg-yellow-500 mt-1.5"></div>
            <div>
              <span className="font-medium text-gray-700">Week 15:</span>
              <span className="text-gray-600 text-sm ml-1">Testing & Validation Complete</span>
            </div>
          </div>
          <div className="flex items-start gap-2">
            <div className="w-2 h-2 rounded-full bg-red-500 mt-1.5"></div>
            <div>
              <span className="font-medium text-gray-700">Week 16:</span>
              <span className="text-gray-600 text-sm ml-1">Final Presentation</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GanttChart;