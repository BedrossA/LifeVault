import { useState } from 'react';
import { FaceEnrollment } from '../components/face/FaceEnrollment';
import { RecognitionDisplay } from '../components/face/RecognitionDisplay';
import { FaceManagement } from '../components/face/FaceManagement';

type TabType = 'enroll' | 'recognize' | 'manage';

export function FaceRecognitionPage() {
  const [activeTab, setActiveTab] = useState<TabType>('enroll');
  const [recognitionMode, setRecognitionMode] = useState<'single' | 'multi'>('single');

  const handleEnrolled = () => {
    // Optionally switch to manage tab after enrollment
    // setActiveTab('manage');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-4 sm:py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-4 sm:mb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-gray-100">Face Recognition</h1>
          <p className="mt-2 text-sm sm:text-base text-gray-600 dark:text-gray-400">
            Enroll, recognize, and manage your facial recognition data
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-4 sm:mb-6 border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
          <nav className="-mb-px flex space-x-4 sm:space-x-8 min-w-max sm:min-w-0">
            <button
              onClick={() => setActiveTab('enroll')}
              className={`${
                activeTab === 'enroll'
                  ? 'border-primary-500 dark:border-primary-400 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
              } whitespace-nowrap py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm`}
            >
              Enroll Face
            </button>
            <button
              onClick={() => setActiveTab('recognize')}
              className={`${
                activeTab === 'recognize'
                  ? 'border-primary-500 dark:border-primary-400 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
              } whitespace-nowrap py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm`}
            >
              Recognize
            </button>
            <button
              onClick={() => setActiveTab('manage')}
              className={`${
                activeTab === 'manage'
                  ? 'border-primary-500 dark:border-primary-400 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
              } whitespace-nowrap py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm`}
            >
              Manage Faces
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'enroll' && (
            <FaceEnrollment onEnrolled={handleEnrolled} />
          )}

          {activeTab === 'recognize' && (
            <div className="space-y-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
                <label className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Recognition Mode:
                  </span>
                  <select
                    value={recognitionMode}
                    onChange={(e) =>
                      setRecognitionMode(e.target.value as 'single' | 'multi')
                    }
                    className="input text-sm"
                  >
                    <option value="single">Single Face</option>
                    <option value="multi">Multiple Faces</option>
                  </select>
                </label>
              </div>
              <RecognitionDisplay mode={recognitionMode} />
            </div>
          )}

          {activeTab === 'manage' && <FaceManagement />}
        </div>
      </div>
    </div>
  );
}

