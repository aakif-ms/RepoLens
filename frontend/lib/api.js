import axios from "axios";

export async function cloneRepo(repoUrl) {
    const res = await axios.post("http://127.0.0.1:8000/repos/clone", {
        repo_url: repoUrl
    })
    return res;
}

export async function askQuestion(q) {
    const res = await axios.post("http://127.0.0.1:8000/ask", {
        q: q
    })
    return res;
}