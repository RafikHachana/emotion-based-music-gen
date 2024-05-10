import axios from "axios";

const API_URL = `${process.env.NEXT_PUBLIC_API_URL}`;
console.log("API_URL: ", API_URL);

const axiosInstance = axios.create({
    baseURL: API_URL,
});

export default axiosInstance;