import axios from "axios";

const fetchData = async (url, options = {}) => {
  const token = localStorage.getItem("token");
  const baseUrl = process.env.REACT_APP_SERVER_DOMAIN || "http://localhost:8000";
  const method = options.method || "GET";

  if (!token) {
    console.error("No authentication token found");
    throw new Error("Authentication required");
  }

  try {
    const response = await axios({
      method,
      url: `${baseUrl}${url}`,
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        ...options.headers,
      },
      data: options.data,
      ...options,
    });

    return response.data;
  } catch (error) {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error("Error response:", {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers,
      });
    } else if (error.request) {
      // The request was made but no response was received
      console.error("Error request:", error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error("Error message:", error.message);
    }
    throw error;
  }
};

export default fetchData;
