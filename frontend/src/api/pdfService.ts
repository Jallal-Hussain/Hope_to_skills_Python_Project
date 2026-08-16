import api from "./axios";
import { BASE_URL } from "./var";

const getAuthHeaders = () => ({
  "Content-Type": "application/json",
});

export const fetchPdfsAPI = async () => {
  const response = await api.get(`${BASE_URL}/list_uuids`, {
    withCredentials: true,
  });
  return response.data.pdfs;
};

export const uploadPdfAPI = async (uuid: string, file: File, onUploadProgress: (progress: number) => void) => {
  const formData = new FormData();
  formData.append("file", file);

  return api.post(`${BASE_URL}/upload/${uuid}`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onUploadProgress(progress);
      }
    },
  });
};

export const downloadPdfAPI = async (uuid: string) => {
  const response = await api.get(`${BASE_URL}/download/${uuid}`, {
    withCredentials: true,
    responseType: "blob",
  });

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `${uuid}.pdf`); // You might want to get the real filename here
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url); // Clean up the object URL
};

export const deletePdfAPI = async (uuid: string) => {
  return api.delete(`${BASE_URL}/delete/${uuid}`, {
    withCredentials: true,
  });
};

export const queryLlmAPI = async (uuid: string, query: string) => {
  const response = await api.get(`${BASE_URL}/query/${uuid}`, {
    withCredentials: true,
    params: { query },
  });
  return response.data.llm_response;
};

// ===== NEW CHAT FUNCTIONS =====

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Conversation {
  uuid: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface ConversationListItem {
  uuid: string;
  title: string;
  document_filename: string;
  document_uuid: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export const startConversationAPI = async (documentUuid: string, message: string): Promise<Conversation> => {
  const response = await api.post(`${BASE_URL}/chat/start/${documentUuid}`, 
    { message },
    { withCredentials: true }
  );
  return response.data;
};

export const continueConversationAPI = async (conversationUuid: string, message: string): Promise<ChatMessage> => {
  const response = await api.post(`${BASE_URL}/chat/continue/${conversationUuid}`, 
    { message },
    { withCredentials: true }
  );
  return response.data;
};

export const getConversationsAPI = async (): Promise<ConversationListItem[]> => {
  const response = await api.get(`${BASE_URL}/chat/conversations`, {
    withCredentials: true,
  });
  return response.data;
};

export const getConversationAPI = async (conversationUuid: string): Promise<Conversation> => {
  const response = await api.get(`${BASE_URL}/chat/conversation/${conversationUuid}`, {
    withCredentials: true,
  });
  return response.data;
};

export const deleteConversationAPI = async (conversationUuid: string) => {
  return api.delete(`${BASE_URL}/chat/conversation/${conversationUuid}`, {
    headers: getAuthHeaders(),
  });
};

// ===== SUMMARIZATION FUNCTIONS =====

export interface DocumentSummary {
  uuid: string;
  filename: string;
  summary: string;
  summary_generated_at: string | null;
}

export const generateSummaryAPI = async (documentUuid: string): Promise<DocumentSummary> => {
  const response = await api.post(`${BASE_URL}/summarize/${documentUuid}`, {}, {
    headers: getAuthHeaders(),
  });
  return response.data;
};

export const getSummaryAPI = async (documentUuid: string): Promise<DocumentSummary> => {
  const response = await api.get(`${BASE_URL}/summary/${documentUuid}`, {
    headers: getAuthHeaders(),
  });
  return response.data;
};