import { useState, useRef, useEffect, useCallback } from 'react';
import { CameraPreview } from './CameraPreview';
import { faceApi } from '../../services/faceApi';
import type { FaceRecognitionResponse } from '../../types/face';

interface RecognitionDisplayProps {
  mode?: 'single' | 'multi';
}

export function RecognitionDisplay({ mode = 'single' }: RecognitionDisplayProps) {
  const [isRecognizing, setIsRecognizing] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [result, setResult] = useState<FaceRecognitionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [imageDimensions, setImageDimensions] = useState<{ width: number; height: number } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const mountedRef = useRef(true);

  // Cleanup image URL on unmount and when image changes
  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, []);

  // Cleanup previous image URL when it changes
  useEffect(() => {
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [imageUrl]);

  const cleanupImageUrl = useCallback(() => {
    if (imageUrl) {
      URL.revokeObjectURL(imageUrl);
      setImageUrl(null);
    }
  }, [imageUrl]);

  const handleRecognize = useCallback(async (imageBlob: Blob) => {
    // Prevent multiple simultaneous recognitions
    if (isRecognizing) {
      return;
    }

    setIsRecognizing(true);
    setError(null);
    setResult(null);

    // Cleanup previous image URL
    cleanupImageUrl();

    // Create new preview URL
    const url = URL.createObjectURL(imageBlob);
    
    if (!mountedRef.current) {
      URL.revokeObjectURL(url);
      return;
    }

    setImageUrl(url);

    try {
      const imageFile =
        imageBlob instanceof File
          ? imageBlob
          : new File([imageBlob], 'recognition.jpg', { type: 'image/jpeg' });

      const response =
        mode === 'multi'
          ? await faceApi.recognizeMultipleFaces(imageFile)
          : await faceApi.recognizeFace(imageFile);

      if (mountedRef.current) {
        setResult(response);
      }
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || 'Recognition failed';
      
      if (mountedRef.current) {
        setError(errorMessage);
        // Clean up preview URL on error
        URL.revokeObjectURL(url);
        setImageUrl(null);
      }
    } finally {
      if (mountedRef.current) {
        setIsRecognizing(false);
      }
    }
  }, [isRecognizing, mode, cleanupImageUrl]);

  const handleCapture = useCallback((blob: Blob) => {
    handleRecognize(blob);
    setIsCapturing(false);
  }, [handleRecognize]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleRecognize(file);
    }
  }, [handleRecognize]);

  const handleReset = useCallback(() => {
    setResult(null);
    setError(null);
    cleanupImageUrl();
    setImageDimensions(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [cleanupImageUrl]);

  const handleImageLoad = useCallback((e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setImageDimensions({
      width: img.naturalWidth || img.width,
      height: img.naturalHeight || img.height,
    });
  }, []);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 sm:p-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-2 mb-4">
        <h3 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-gray-100">
          Face Recognition {mode === 'multi' && '(Multi-Face)'}
        </h3>
        <div className="flex flex-col sm:flex-row gap-2">
          <button
            onClick={() => setIsCapturing(!isCapturing)}
            className={`btn ${isCapturing ? 'btn-secondary' : 'btn-outline'} flex-1 sm:flex-none`}
            disabled={isRecognizing}
            aria-label={isCapturing ? 'Stop camera' : 'Use camera'}
          >
            {isCapturing ? 'Stop Camera' : 'Use Camera'}
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn btn-outline flex-1 sm:flex-none"
            disabled={isRecognizing}
            aria-label="Upload image"
          >
            Upload Image
          </button>
          {(result || imageUrl || error) && (
            <button
              onClick={handleReset}
              className="btn btn-secondary flex-1 sm:flex-none"
              disabled={isRecognizing}
              aria-label="Reset"
            >
              Reset
            </button>
          )}
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/jpg"
          onChange={handleFileSelect}
          className="hidden"
          aria-label="File input"
        />
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded">
          {error}
        </div>
      )}

      {isRecognizing && (
        <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-400 rounded flex items-center">
          <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-blue-700 dark:border-blue-400 mr-2" />
          Recognizing faces...
        </div>
      )}

      {/* Camera Preview */}
      {isCapturing && (
        <div className="mb-4">
          <CameraPreview
            onCapture={handleCapture}
            isActive={isCapturing}
            width={640}
            height={480}
          />
        </div>
      )}

      {/* Recognition Results */}
      {result && imageUrl && (
        <div className="space-y-4">
          {/* Image with face boxes */}
          <div className="relative bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
            <img
              ref={imageRef}
              src={imageUrl}
              alt="Recognition result"
              className="w-full h-auto"
              onLoad={handleImageLoad}
            />
            {/* Face boxes overlay */}
            {result.faces.length > 0 && imageDimensions && (
              <div className="absolute inset-0 pointer-events-none">
                {result.faces.map((face, index) => {
                  const { bbox } = face;
                  const img = imageRef.current;

                  if (!img) return null;

                  // Calculate scale factors
                  const naturalWidth = imageDimensions.width;
                  const naturalHeight = imageDimensions.height;
                  const displayedWidth = img.clientWidth || img.offsetWidth || naturalWidth;
                  const displayedHeight = img.clientHeight || img.offsetHeight || naturalHeight;

                  const scaleX = displayedWidth / naturalWidth;
                  const scaleY = displayedHeight / naturalHeight;

                  // Scale bbox coordinates
                  const scaledLeft = bbox.left * scaleX;
                  const scaledTop = bbox.top * scaleY;
                  const scaledWidth = (bbox.right - bbox.left) * scaleX;
                  const scaledHeight = (bbox.bottom - bbox.top) * scaleY;

                  return (
                    <div
                      key={index}
                      className={`absolute border-2 ${
                        face.is_known
                          ? 'border-green-500 bg-green-500/20'
                          : 'border-yellow-500 bg-yellow-500/20'
                      }`}
                      style={{
                        left: `${scaledLeft}px`,
                        top: `${scaledTop}px`,
                        width: `${scaledWidth}px`,
                        height: `${scaledHeight}px`,
                      }}
                    >
                      <div
                        className={`absolute -top-8 left-0 px-2 py-1 rounded text-xs font-medium whitespace-nowrap ${
                          face.is_known
                            ? 'bg-green-500 text-white'
                            : 'bg-yellow-500 text-white'
                        }`}
                      >
                        {face.is_known
                          ? `${face.username || 'Known'} (${(face.confidence * 100).toFixed(1)}%)`
                          : `Unknown (${(face.confidence * 100).toFixed(1)}%)`}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Statistics */}
          <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Faces Detected</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {result.num_faces_detected}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Recognized</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {result.recognized ? 'Yes' : 'No'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Detection Time</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {result.detection_time_ms.toFixed(0)}ms
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Primary User</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {result.primary_username || 'N/A'}
                </p>
              </div>
            </div>
            <p className="text-sm text-gray-700 dark:text-gray-300">{result.message}</p>
          </div>

          {/* Face Details */}
          {result.faces.length > 0 && (
            <div className="space-y-2">
              <h4 className="font-medium text-gray-900 dark:text-gray-100">Detected Faces:</h4>
              {result.faces.map((face, index) => (
                <div
                  key={index}
                  className={`p-3 rounded ${
                    face.is_known
                      ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                      : 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-gray-100">
                        {face.is_known ? `Known: ${face.username || 'User'}` : 'Unknown Face'}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Confidence: {(face.confidence * 100).toFixed(1)}% | Quality:{' '}
                        {face.quality_score != null ? (face.quality_score * 100).toFixed(1) : 'N/A'}%
                      </p>
                    </div>
                    {face.face_id && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        Face ID: {face.face_id}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {!isCapturing && !result && !imageUrl && !error && (
        <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-8 text-center">
          <p className="text-gray-500 dark:text-gray-400">
            Use camera or upload an image to recognize faces
          </p>
        </div>
      )}
    </div>
  );
}