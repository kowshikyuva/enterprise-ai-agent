import axios from "axios";

const api = axios.create({
    baseURL: "https://enterprise-ai-agent-vyj5.onrender.com",
});

export default api;