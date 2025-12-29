import { useState, useRef } from 'react';
import { CameraPreview } from './CameraPreview';
import { faceApi } from '../../services/faceApi';
import type { FaceEnrollResponse } from '../../types/face';

interface FaceEnrollmentProps {
  onEnrolled?: (response: FaceEnrollResponse) => void;
  onCancel?: () => void;
}

export function FaceEnrollment({ onEnrolled, onCancel }: FaceEnrollmentProps) {
  const [label, setLabel] = useState('');
  const [isCapturing, setIsCapturing] = useState(false);
  const [isEnrolling, setIsEnrolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [capturedImage, setCapturedImage] = useState<Blob | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleCapture = (blob: Blob) => {
    setCapturedImage(blob);
    setIsCapturing(false);
    setError(null);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setCapturedImage(file);
      setError(null);
    }
  };

  const handleEnroll = async () => {
    if (!label.trim()) {
      setError('Please enter a label for this face');
      return;
    }

    if (!capturedImage) {
      setError('Please capture or upload an image first');
      return;
    }

    setIsEnrolling(true);
    setError(null);
    setSuccess(null);

    try {
      // Convert blob to File if needed
      const imageFile =
        capturedImage instanceof File
          ? capturedImage
          : new File([capturedImage], 'face.jpg', { type: 'image/jpeg' });

      const response = await faceApi.enrollFace(label.trim(), imageFile);

      const qualityText = response.quality_score != null 
        ? `${(response.quality_score * 100).toFixed(1)}%`
        : 'N/A';
      setSuccess(
        `Face enrolled successfully! Quality: ${qualityText}`
      );

      // Reset form
      setLabel('');
      setCapturedImage(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      onEnrolled?.(response);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || 'Failed to enroll face';
      setError(errorMessage);
    } finally {
      setIsEnrolling(false);
    }
  };

  const handleReset = () => {
    setLabel('');
    setCapturedImage(null);
    setError(null);
    setSuccess(null);
    setIsCapturing(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
      <h3 className="text-lg sm:text-xl font-semibold mb-4">Enroll New Face</h3>

      {success && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded">
          {success}
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {/* Label Input */}
        <div>
          <label htmlFor="face-label" className="block text-sm font-medium text-gray-700 mb-1">
            Face Label
          </label>
          <input
            id="face-label"
            type="text"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder="e.g., primary, with_glasses, profile"
            className="input w-full"
            disabled={isEnrolling}
          />
          <p className="mt-1 text-xs text-gray-500">
            Give this face a descriptive label
          </p>
        </div>

        {/* Image Source Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Image Source
          </label>
          <div className="flex flex-col sm:flex-row gap-2 mb-3">
            <button
              onClick={() => setIsCapturing(!isCapturing)}
              className={`btn ${isCapturing ? 'btn-secondary' : 'btn-outline'} flex-1 sm:flex-none`}
              disabled={isEnrolling}
            >
              {isCapturing ? 'Stop Camera' : 'Use Camera'}
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="btn btn-outline flex-1 sm:flex-none"
              disabled={isEnrolling}
            >
              Upload Image
            </button>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/jpg"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {/* Camera Preview or Image Preview */}
        {isCapturing ? (
          <CameraPreview
            onCapture={handleCapture}
            isActive={isCapturing}
            width={640}
            height={480}
          />
        ) : capturedImage ? (
          <div className="relative bg-gray-100 rounded-lg overflow-hidden aspect-video">
            <img
              src={URL.createObjectURL(capturedImage)}
              alt="Captured face"
              className="w-full h-full object-cover"
            />
            <button
              onClick={() => setCapturedImage(null)}
              className="absolute top-2 right-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
            >
              Remove
            </button>
          </div>
        ) : (
          <div className="bg-gray-100 rounded-lg aspect-video flex items-center justify-center">
            <p className="text-gray-500">No image selected</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-2">
          <button
            onClick={handleEnroll}
            disabled={!label.trim() || !capturedImage || isEnrolling}
            className="btn btn-primary flex-1"
          >
            {isEnrolling ? 'Enrolling...' : 'Enroll Face'}
          </button>
          {capturedImage && (
            <button
              onClick={handleReset}
              disabled={isEnrolling}
              className="btn btn-outline"
            >
              Reset
            </button>
          )}
          {onCancel && (
            <button
              onClick={onCancel}
              disabled={isEnrolling}
              className="btn btn-outline"
            >
              Cancel
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

