import axios, { AxiosError } from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Add auth header to requests
apiClient.interceptors.request.use((config) => {
  const auth = localStorage.getItem('auth');
  if (auth) {
    config.headers.Authorization = `Basic ${auth}`;
  }
  return config;
});

// Types
export interface EquipmentItem {
  id: number;
  equipment_name: string;
  equipment_type: string;
  flowrate: number | null;
  pressure: number | null;
  temperature: number | null;
}

export interface Dataset {
  id: number;
  name: string;
  uploaded_at: string;
  summary_data: SummaryData;
  item_count: number;
  items?: EquipmentItem[];
}

export interface SummaryData {
  total_count: number;
  avg_flowrate: number | null;
  avg_pressure: number | null;
  avg_temperature: number | null;
  min_flowrate: number | null;
  max_flowrate: number | null;
  min_pressure: number | null;
  max_pressure: number | null;
  min_temperature: number | null;
  max_temperature: number | null;
  type_distribution: Record<string, number>;
}

export interface ChartData {
  type_distribution: Record<string, number>;
  avg_flowrate_by_type: Record<string, number>;
  avg_pressure_by_type: Record<string, number>;
  avg_temperature_by_type: Record<string, number>;
  labels: string[];
  type_counts: number[];
}

export interface UploadResponse {
  message: string;
  dataset_id: number;
  summary: SummaryData;
}

// API functions
export const api = {
  // Login
  login: async (username: string, password: string): Promise<boolean> => {
    try {
      const auth = btoa(`${username}:${password}`);
      const response = await axios.get(`${API_BASE_URL}/datasets/`, {
        headers: {
          Authorization: `Basic ${auth}`,
        },
      });
      return response.status === 200;
    } catch (error) {
      return false;
    }
  },

  // Get all datasets
  getDatasets: async (): Promise<Dataset[]> => {
    const response = await apiClient.get('/datasets/');
    return response.data;
  },

  // Get dataset summary
  getSummary: async (datasetId: number): Promise<SummaryData> => {
    const response = await apiClient.get(`/datasets/${datasetId}/summary/`);
    return response.data;
  },

  // Get dataset items
  getItems: async (datasetId: number): Promise<EquipmentItem[]> => {
    const response = await apiClient.get(`/datasets/${datasetId}/data/`);
    return response.data;
  },

  // Get chart data
  getChartData: async (datasetId: number): Promise<ChartData> => {
    const response = await apiClient.get(`/datasets/${datasetId}/chart_data/`);
    return response.data;
  },

  // Upload CSV file
  uploadCSV: async (file: File, name: string): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);

    const response = await apiClient.post('/datasets/upload_csv/', formData);
    return response.data;
  },

  // Download PDF report
  downloadPDF: async (datasetId: number, datasetName: string): Promise<void> => {
    const response = await apiClient.get(`/datasets/${datasetId}/generate_pdf/`, {
      responseType: 'blob',
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `equipment_report_${datasetName}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  // Delete dataset
  deleteDataset: async (datasetId: number): Promise<void> => {
    await apiClient.delete(`/datasets/${datasetId}/`);
  },
};

// Error handler
export const handleApiError = (error: AxiosError): string => {
  if (error.response) {
    const data = error.response.data as { error?: string; detail?: string };
    return data.error || data.detail || 'An error occurred';
  }
  return error.message || 'Network error';
};
