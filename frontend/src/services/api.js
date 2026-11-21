
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1",
  timeout: 15000,
});

// ==============================
// DASHBOARD APIs
// ==============================

export const getDashboardStats = async () => {
  const response = await api.get("/dashboard/stats");
  return response.data;
};

export const getRevenue = async () => {
  const response = await api.get("/dashboard/revenue");
  return response.data;
};

export const getSegments = async () => {
  const response = await api.get("/dashboard/segments");
  return response.data;
};

export const getHealth = async () => {
  const response = await api.get("/health");
  return response.data;
};

// ==============================
// CUSTOMER APIs
// ==============================

export const getCustomers = async (
  search = "",
  page = 1,
  pageSize = 10
) => {
  const response = await api.get("/customers", {
    params: {
      search,
      page,
      page_size: pageSize,
    },
  });

  return response.data;
};

export const getCustomer = async (customerId) => {
  const response = await api.get(
    `/customers/${encodeURIComponent(customerId)}`
  );

  return response.data;
};

// ==============================
// CUSTOMER SEGMENTATION APIs
// ==============================

export const getSegmentationSummary = async () => {
  const response = await api.get("/segmentation/summary");
  return response.data;
};

export const getSegmentationDistribution = async () => {
  const response = await api.get("/segmentation/distribution");
  return response.data;
};

export const getSegmentCustomers = async (
  segment = "",
  search = "",
  page = 1,
  pageSize = 10
) => {
  const response = await api.get("/segmentation/customers", {
    params: {
      segment,
      search,
      page,
      page_size: pageSize,
    },
  });

  return response.data;
};

// ==============================
// DATASET MANAGEMENT APIs
// ==============================

export const getDatasets = async () => {
  const response = await api.get("/datasets");
  return response.data;
};

export const uploadDataset = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/datasets/upload", formData);
  return response.data;
};

export const previewDataset = async (
  datasetId,
  limit = 10
) => {
  const response = await api.get(
    `/datasets/${encodeURIComponent(datasetId)}/preview`,
    {
      params: { limit },
    }
  );

  return response.data;
};

export const deleteDataset = async (datasetId) => {
  const response = await api.delete(
    `/datasets/${encodeURIComponent(datasetId)}`
  );

  return response.data;
};

// ==============================
// DATA QUALITY APIs
// ==============================

export const getDatasetQualityOverview = async () => {
  const response = await api.get("/datasets/quality/overview");
  return response.data;
};

export const validateDataset = async (datasetId) => {
  const response = await api.get(
    `/datasets/${encodeURIComponent(datasetId)}/validation`
  );

  return response.data;
};

// ==============================
// PRODUCT RECOMMENDATION APIs
// ==============================

export const getRecommendationSummary = async () => {
  const response = await api.get("/recommendations/summary");
  return response.data;
};

export const getPopularProducts = async (limit = 10) => {
  const response = await api.get("/recommendations/popular", {
    params: { limit },
  });

  return response.data;
};

export const getCustomerRecommendations = async (
  customerId,
  limit = 10
) => {
  const response = await api.get(
    `/recommendations/customer/${encodeURIComponent(customerId)}`,
    {
      params: { limit },
    }
  );

  return response.data;
};

export const getFrequentlyBoughtTogether = async (limit = 10) => {
  const response = await api.get(
    "/recommendations/frequently-bought-together",
    {
      params: { limit },
    }
  );

  return response.data;
};

// ==============================
// CHURN PREDICTION APIs
// ==============================

export const getChurnHealth = async () => {
  const response = await api.get("/churn/health");
  return response.data;
};

export const getChurnModelInfo = async () => {
  const response = await api.get("/churn/model-info");
  return response.data;
};

export const getChurnSummary = async () => {
  const response = await api.get("/churn/summary");
  return response.data;
};

export const getChurnCustomers = async (
  riskLevel = "",
  limit = 5000
) => {
  const response = await api.get("/churn/customers", {
    params: {
      risk_level: riskLevel,
      limit,
    },
  });

  return response.data;
};

export const getCustomerChurnPrediction = async (customerId) => {
  const response = await api.get(
    `/churn/customers/${encodeURIComponent(customerId)}`
  );

  return response.data;
};

// ==============================
// SENTIMENT ANALYSIS APIs
// ==============================

export const getSentimentHealth = async () => {
  const response = await api.get("/sentiment/health");
  return response.data;
};

export const getSentimentSummary = async () => {
  const response = await api.get("/sentiment/summary");
  return response.data;
};

export const getSentimentDistribution = async () => {
  const response = await api.get("/sentiment/distribution");
  return response.data;
};

export const getSentimentTrends = async () => {
  const response = await api.get("/sentiment/trends");
  return response.data;
};

export const getSentimentReviews = async (
  search = "",
  sentiment = "",
  limit = 10,
  offset = 0
) => {
  const response = await api.get("/sentiment/reviews", {
    params: {
      search,
      sentiment,
      limit,
      offset,
    },
  });

  return response.data;
};

// ==============================
// DEFAULT EXPORT
// ==============================

export default api;
