/**
 * Face Recognition Login Component
 */
import { useState, useRef } from 'react';
import { CameraPreview } from './face/CameraPreview';
import { faceApi } from '../services/faceApi';
import type { FaceRecognitionResponse } from '../types/face';

interface FaceLoginProps {
  onSuccess: (username: string) => void;
  onError: (error: string) => void;
}

export function FaceLogin({ onSuccess, onError }: FaceLoginProps) {
  const [isCapturing, setIsCapturing] = useState(false);
  const [isRecognizing, setIsRecognizing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleRecognize = async (imageBlob: Blob) => {
    setIsRecognizing(true);
    setError(null);
    setIsCapturing(false);

    try {
      const imageFile = imageBlob instanceof File
        ? imageBlob
        : new File([imageBlob], 'login.jpg', { type: 'image/jpeg' });

      const response: FaceRecognitionResponse = await faceApi.recognizeFace(imageFile);

      if (response.recognized && response.primary_username) {
        // Use the username from the recognition response
        onSuccess(response.primary_username);
      } else {
        const errorMsg = 'Face not recognized. Please try again or use username/password login.';
        setError(errorMsg);
        onError(errorMsg);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Face recognition failed';
      setError(errorMessage);
      onError(errorMessage);
    } finally {
      setIsRecognizing(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleRecognize(file);
    }
  };

  return (
    <div className="space-y-4">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Face Recognition Login
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Use your face to sign in quickly
        </p>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-400 text-red-700 dark:text-red-400 px-4 py-3 rounded">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium">{error}</p>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-2">
        <button
          onClick={() => setIsCapturing(!isCapturing)}
          disabled={isRecognizing}
          className={`btn ${isCapturing ? 'btn-secondary' : 'btn-primary'} flex-1`}
        >
          {isCapturing ? 'Stop Camera' : 'Use Camera'}
        </button>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isRecognizing}
          className="btn btn-secondary flex-1"
        >
          Upload Photo
        </button>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/jpg"
        onChange={handleFileSelect}
        className="hidden"
      />

      {isCapturing && (
        <CameraPreview
          onCapture={handleRecognize}
          isActive={isCapturing}
          width={640}
          height={480}
        />
      )}

      {isRecognizing && (
        <div className="text-center py-4">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Recognizing face...</p>
        </div>
      )}
    </div>
  );
}

