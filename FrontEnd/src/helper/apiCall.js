import axios from "axios";

const fetchData = async (url, options = {}) => {
  const token = localStorage.getItem("token");

  try {
    const response = await axios.get(`http://localhost:8000${url}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    return response.data;
  } catch (error) {
    console.error("Failed to fetch data:", error);
    throw error;
  }
};

export default fetchData;
