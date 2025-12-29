import { apiClient } from './api';
import type {
  FaceEnrollResponse,
  FaceRecognitionResponse,
  FaceListResponse,
  FaceDeleteResponse,
  FaceStatsResponse,
  FaceAddEncodingResponse,
  FaceConfig,
  FaceDetails,
} from '../types/face';

class FaceApiClient {
  /**
   * Enroll a new face
   * @param label - Label for this face (e.g., "primary", "with_glasses")
   * @param imageFile - Image file containing a single face
   */
  async enrollFace(label: string, imageFile: File): Promise<FaceEnrollResponse> {
    const formData = new FormData();
    formData.append('label', label);
    formData.append('image', imageFile);

    const response = await apiClient.client.post<FaceEnrollResponse>(
      '/face/enroll',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  /**
   * Add another encoding to an existing face
   * @param faceId - ID of the face to add encoding to
   * @param imageFile - Another image of the same person
   */
  async addEncoding(
    faceId: number,
    imageFile: File
  ): Promise<FaceAddEncodingResponse> {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await apiClient.client.post<FaceAddEncodingResponse>(
      `/face/${faceId}/add-encoding`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  /**
   * Recognize a face in the uploaded image (single face mode)
   * @param imageFile - Image file containing a face to recognize
   */
  async recognizeFace(imageFile: File): Promise<FaceRecognitionResponse> {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await apiClient.client.post<FaceRecognitionResponse>(
      '/face/recognize',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  /**
   * Recognize multiple faces in one image
   * @param imageFile - Image file that may contain multiple faces
   */
  async recognizeMultipleFaces(
    imageFile: File
  ): Promise<FaceRecognitionResponse> {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await apiClient.client.post<FaceRecognitionResponse>(
      '/face/recognize-multi',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  /**
   * Get list of all enrolled faces for current user
   */
  async getMyFaces(): Promise<FaceListResponse[]> {
    const response = await apiClient.client.get<FaceListResponse[]>(
      '/face/my-faces'
    );
    return response.data;
  }

  /**
   * Delete an enrolled face
   * @param faceId - ID of the face to delete
   */
  async deleteFace(faceId: number): Promise<FaceDeleteResponse> {
    const response = await apiClient.client.delete<FaceDeleteResponse>(
      `/face/${faceId}`
    );
    return response.data;
  }

  /**
   * Get face recognition statistics for current user
   */
  async getStats(): Promise<FaceStatsResponse> {
    const response = await apiClient.client.get<FaceStatsResponse>(
      '/face/stats'
    );
    return response.data;
  }

  /**
   * Get current face recognition configuration
   */
  async getConfig(): Promise<FaceConfig> {
    const response = await apiClient.client.get<FaceConfig>('/face/config');
    return response.data;
  }

  /**
   * Get detailed information about a specific face
   * @param faceId - ID of the face
   */
  async getFaceDetails(faceId: number): Promise<FaceDetails> {
    const response = await apiClient.client.get<FaceDetails>(
      `/face/${faceId}/details`
    );
    return response.data;
  }
}

export const faceApi = new FaceApiClient();

