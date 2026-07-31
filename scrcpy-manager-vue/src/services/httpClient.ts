import axios from "axios";

export function createApiClient(baseURL: string) {
  const client = axios.create({
    baseURL,
    timeout: 10000,
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (import.meta.env.DEV) {
    client.interceptors.request.use(
      (config) => {
        console.log(
          `API Request: ${config.method?.toUpperCase()} ${config.url}`,
        );
        return config;
      },
      (error) => {
        console.error("API Request Error:", error);
        return Promise.reject(error);
      },
    );

    client.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error("API Error:", error);
        return Promise.reject(error);
      },
    );
  }

  return client;
}
