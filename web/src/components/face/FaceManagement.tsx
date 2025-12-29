import { useState, useEffect } from 'react';
import { faceApi } from '../../services/faceApi';
import type {
  FaceListResponse,
  FaceStatsResponse,
  FaceDetails,
} from '../../types/face';
import { format } from 'date-fns';

export function FaceManagement() {
  const [faces, setFaces] = useState<FaceListResponse[]>([]);
  const [stats, setStats] = useState<FaceStatsResponse | null>(null);
  const [selectedFace, setSelectedFace] = useState<FaceDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [facesData, statsData] = await Promise.all([
        faceApi.getMyFaces(),
        faceApi.getStats(),
      ]);
      setFaces(facesData);
      setStats(statsData);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || 'Failed to load faces';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (faceId: number) => {
    if (!confirm('Are you sure you want to delete this face?')) {
      return;
    }

    setDeletingId(faceId);
    try {
      await faceApi.deleteFace(faceId);
      await loadData();
      if (selectedFace?.id === faceId) {
        setSelectedFace(null);
      }
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || 'Failed to delete face';
      alert(errorMessage);
    } finally {
      setDeletingId(null);
    }
  };

  const handleViewDetails = async (faceId: number) => {
    try {
      const details = await faceApi.getFaceDetails(faceId);
      setSelectedFace(details);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || 'Failed to load details';
      alert(errorMessage);
    }
  };

  const handleAddEncoding = async (faceId: number) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/jpeg,image/png,image/jpg';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;

      try {
        await faceApi.addEncoding(faceId, file);
        alert('Encoding added successfully!');
        await loadData();
        if (selectedFace?.id === faceId) {
          const details = await faceApi.getFaceDetails(faceId);
          setSelectedFace(details);
        }
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.detail || err.message || 'Failed to add encoding';
        alert(errorMessage);
      }
    };
    input.click();
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center py-8">
          <p className="text-gray-500">Loading faces...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded">
          {error}
        </div>
        <button onClick={loadData} className="btn btn-primary mt-4">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Statistics */}
      {stats && (
        <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
          <h3 className="text-lg sm:text-xl font-semibold mb-4">Face Recognition Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Faces</p>
              <p className="text-2xl font-bold">{stats.total_faces}</p>
              <p className="text-xs text-gray-500">Max: {stats.max_faces}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Active Faces</p>
              <p className="text-2xl font-bold">{stats.active_faces}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Encodings</p>
              <p className="text-2xl font-bold">{stats.total_encodings}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Avg Quality</p>
              <p className="text-2xl font-bold">
                {stats.average_quality != null 
                  ? `${(stats.average_quality * 100).toFixed(1)}%`
                  : 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Recognitions</p>
              <p className="text-2xl font-bold">{stats.total_recognitions}</p>
            </div>
            {stats.latest_enrollment && (
              <div>
                <p className="text-sm text-gray-600">Last Enrollment</p>
                <p className="text-sm font-semibold">
                  {format(new Date(stats.latest_enrollment), 'MMM d, yyyy')}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Face List */}
      <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-0 mb-4">
          <h3 className="text-lg sm:text-xl font-semibold">My Enrolled Faces</h3>
          <button onClick={loadData} className="btn btn-outline text-sm self-start sm:self-auto">
            Refresh
          </button>
        </div>

        {faces.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No faces enrolled yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {faces.map((face) => (
              <div
                key={face.id}
                className={`p-4 rounded-lg border ${
                  face.is_active
                    ? 'bg-green-50 border-green-200'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-semibold">{face.label}</h4>
                      {face.is_active ? (
                        <span className="px-2 py-1 bg-green-500 text-white text-xs rounded">
                          Active
                        </span>
                      ) : (
                        <span className="px-2 py-1 bg-gray-400 text-white text-xs rounded">
                          Inactive
                        </span>
                      )}
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                      <div>
                        <span className="text-gray-600">Quality: </span>
                        <span className="font-medium">
                          {face.average_quality != null
                            ? `${(face.average_quality * 100).toFixed(1)}%`
                            : 'N/A'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">Encodings: </span>
                        <span className="font-medium">{face.encoding_count}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Recognitions: </span>
                        <span className="font-medium">{face.recognition_count}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Created: </span>
                        <span className="font-medium">
                          {format(new Date(face.created_at), 'MMM d, yyyy')}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-2 sm:ml-4 mt-2 sm:mt-0">
                    <button
                      onClick={() => handleViewDetails(face.id)}
                      className="btn btn-outline text-sm"
                    >
                      Details
                    </button>
                    {face.encoding_count < 10 && (
                      <button
                        onClick={() => handleAddEncoding(face.id)}
                        className="btn btn-outline text-sm"
                      >
                        Add Encoding
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(face.id)}
                      disabled={deletingId === face.id}
                      className="btn btn-outline text-sm text-red-600 hover:bg-red-50"
                    >
                      {deletingId === face.id ? 'Deleting...' : 'Delete'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Face Details Modal */}
      {selectedFace && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-semibold">{selectedFace.label}</h3>
                <button
                  onClick={() => setSelectedFace(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Face ID</p>
                    <p className="font-medium">{selectedFace.id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Status</p>
                    <p className="font-medium">
                      {selectedFace.is_active ? 'Active' : 'Inactive'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Encoding Count</p>
                    <p className="font-medium">
                      {selectedFace.encoding_count} / 10
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Quality Score</p>
                    <p className="font-medium">
                      {selectedFace.quality_score != null
                        ? `${(selectedFace.quality_score * 100).toFixed(1)}%`
                        : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Average Quality</p>
                    <p className="font-medium">
                      {selectedFace.average_quality != null
                        ? `${(selectedFace.average_quality * 100).toFixed(1)}%`
                        : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Recognition Count</p>
                    <p className="font-medium">{selectedFace.recognition_count}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Created</p>
                    <p className="font-medium">
                      {format(new Date(selectedFace.created_at), 'PPp')}
                    </p>
                  </div>
                  {selectedFace.last_recognized && (
                    <div>
                      <p className="text-sm text-gray-600">Last Recognized</p>
                      <p className="font-medium">
                        {format(
                          new Date(selectedFace.last_recognized),
                          'PPp'
                        )}
                      </p>
                    </div>
                  )}
                </div>

                {selectedFace.custom_threshold && (
                  <div>
                    <p className="text-sm text-gray-600">Custom Threshold</p>
                    <p className="font-medium">{selectedFace.custom_threshold}</p>
                  </div>
                )}

                <div>
                  <p className="text-sm text-gray-600 mb-1">Recommendation</p>
                  <p className="text-sm text-gray-700 bg-blue-50 p-3 rounded">
                    {selectedFace.recommendation}
                  </p>
                </div>

                <div className="flex gap-2 pt-4">
                  {selectedFace.can_add_more_encodings && (
                    <button
                      onClick={() => {
                        handleAddEncoding(selectedFace.id);
                        setSelectedFace(null);
                      }}
                      className="btn btn-primary"
                    >
                      Add More Encodings
                    </button>
                  )}
                  <button
                    onClick={() => {
                      handleDelete(selectedFace.id);
                      setSelectedFace(null);
                    }}
                    className="btn btn-outline text-red-600 hover:bg-red-50"
                  >
                    Delete Face
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

