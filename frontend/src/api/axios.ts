// src/api/axios.ts
import axios from "axios";
import { BASE_URL } from "./var";

const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      localStorage.removeItem("isAuthenticated");
      window.location.href = "/auth/login?expired=1";
    }
    return Promise.reject(error);
  }
);

export default api;
