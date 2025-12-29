/**
 * Face recognition type definitions matching backend schemas
 */

export interface FaceEnrollResponse {
  face_id: number;
  encoding_id: string;
  label: string;
  confidence_score: number;
  quality_score: number;
  encoding_count: number;
  custom_threshold?: number | null;
  message: string;
}

export interface FaceAddEncodingResponse {
  face_id: number;
  encoding_id: string;
  encoding_count: number;
  average_quality: number;
  message: string;
}

export interface DetectedFace {
  user_id?: number | null;
  username?: string | null;
  face_id?: number | null;
  confidence: number;
  bbox: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
  quality_score: number;
  is_known: boolean;
}

export interface FaceRecognitionResponse {
  recognized: boolean;
  num_faces_detected: number;
  detection_time_ms: number;
  faces: DetectedFace[];
  primary_user_id?: number | null;
  primary_username?: string | null;
  message: string;
}

export interface FaceListResponse {
  id: number;
  label: string;
  confidence_score: number;
  quality_score: number;
  average_quality: number;
  encoding_count: number;
  recognition_count: number;
  custom_threshold?: number | null;
  is_active: boolean;
  created_at: string;
  last_recognized?: string | null;
}

export interface FaceDeleteResponse {
  message: string;
  deleted_face_id: number;
}

export interface FaceStatsResponse {
  total_faces: number;
  active_faces: number;
  total_encodings: number;
  max_faces: number;
  average_quality: number;
  total_recognitions: number;
  latest_enrollment?: string | null;
}

export interface FaceConfig {
  max_faces_per_user: number;
  max_encodings_per_face: number;
  min_quality_threshold: number;
  adaptive_thresholds_enabled: boolean;
  multi_face_detection_enabled: boolean;
  max_faces_in_frame: number;
  detection_method: string;
  thresholds: {
    high_quality: number;
    default: number;
    low_quality: number;
  };
}

export interface FaceDetails {
  id: number;
  label: string;
  encoding_count: number;
  quality_score: number;
  average_quality: number;
  custom_threshold?: number | null;
  recognition_count: number;
  is_active: boolean;
  created_at: string;
  last_recognized?: string | null;
  can_add_more_encodings: boolean;
  recommendation: string;
}

