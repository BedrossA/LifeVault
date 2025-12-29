import { useRef, useEffect, useState } from 'react';

interface CameraPreviewProps {
  onCapture: (blob: Blob) => void;
  isActive: boolean;
  width?: number;
  height?: number;
  facingMode?: 'user' | 'environment';
}

export function CameraPreview({
  onCapture,
  isActive,
  width = 640,
  height = 480,
  facingMode = 'user',
}: CameraPreviewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isActive) {
      stopCamera();
      return;
    }

    startCamera();

    return () => {
      stopCamera();
    };
  }, [isActive, facingMode]);

  const startCamera = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Check if we're in a secure context (HTTPS or localhost)
      const isSecureContext = window.isSecureContext || 
        location.protocol === 'https:' || 
        location.hostname === 'localhost' || 
        location.hostname === '127.0.0.1';

      if (!isSecureContext) {
        throw new Error(
          'Camera access requires a secure connection (HTTPS). Please use HTTPS or upload images instead.'
        );
      }

      // Check if getUserMedia is available
      let getUserMediaFn: ((constraints: MediaStreamConstraints) => Promise<MediaStream>) | null = null;

      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // Modern API
        getUserMediaFn = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
      } else {
        // Fallback for older browsers
        const legacyGetUserMedia =
          navigator.getUserMedia ||
          (navigator as any).webkitGetUserMedia ||
          (navigator as any).mozGetUserMedia ||
          (navigator as any).msGetUserMedia;

        if (!legacyGetUserMedia) {
          throw new Error(
            'Camera access is not supported in this browser. Please use a modern browser or upload images instead.'
          );
        }

        // Wrap legacy API in Promise
        getUserMediaFn = (constraints: MediaStreamConstraints) => {
          return new Promise((resolve, reject) => {
            legacyGetUserMedia.call(
              navigator,
              constraints,
              (stream: MediaStream) => resolve(stream),
              (err: any) => reject(err)
            );
          });
        };
      }

      if (!getUserMediaFn) {
        throw new Error('Camera access is not available.');
      }

      const constraints: MediaStreamConstraints = {
        video: {
          width: { ideal: width },
          height: { ideal: height },
          facingMode: facingMode,
        },
        audio: false,
      };

      const stream = await getUserMediaFn(constraints);
      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
    } catch (err: any) {
      let errorMessage = 'Failed to access camera.';
      
      if (err instanceof Error) {
        const errName = err.name || '';
        const errMsg = err.message || '';

        // Handle specific error types
        if (errName === 'NotAllowedError' || errMsg.includes('permission') || errMsg.includes('denied')) {
          errorMessage = 'Camera permission denied. Please allow camera access in your browser settings and try again.';
        } else if (errName === 'NotFoundError' || errMsg.includes('not found')) {
          errorMessage = 'No camera found. Please connect a camera or upload images instead.';
        } else if (errName === 'NotReadableError' || errMsg.includes('not readable')) {
          errorMessage = 'Camera is already in use by another application. Please close other apps using the camera.';
        } else if (errName === 'OverconstrainedError' || errMsg.includes('constraint')) {
          errorMessage = 'Camera does not support the requested settings. Trying with default settings...';
          // Retry with simpler constraints
          try {
            const simpleStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            streamRef.current = simpleStream;
            if (videoRef.current) {
              videoRef.current.srcObject = simpleStream;
              await videoRef.current.play();
            }
            setIsLoading(false);
            return;
          } catch (retryErr) {
            errorMessage = err.message || 'Failed to access camera.';
          }
        } else {
          errorMessage = err.message || errorMessage;
        }
      }

      setError(errorMessage);
      console.error('Camera error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (!context) return;

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    context.drawImage(video, 0, 0);

    // Convert canvas to blob
    canvas.toBlob(
      (blob) => {
        if (blob) {
          onCapture(blob);
        }
      },
      'image/jpeg',
      0.95
    );
  };

  if (!isActive) {
    return (
      <div className="bg-gray-100 rounded-lg flex items-center justify-center aspect-video">
        <p className="text-gray-500">Camera inactive</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 aspect-video flex items-center justify-center">
        <div className="text-center px-2">
          <p className="text-red-700 font-medium text-sm sm:text-base">Camera Error</p>
          <p className="text-red-600 text-xs sm:text-sm mt-1 break-words">{error}</p>
          <button
            onClick={startCamera}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-xs sm:text-sm"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
          <div className="text-white">Loading camera...</div>
        </div>
      )}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-full object-cover"
      />
      <canvas ref={canvasRef} className="hidden" />
      <div className="absolute bottom-4 left-0 right-0 flex justify-center">
        <button
          onClick={capturePhoto}
          disabled={isLoading}
          className="px-6 py-3 bg-primary-600 text-white rounded-full hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
        >
          📷 Capture
        </button>
      </div>
    </div>
  );
}

