import axios from "axios";

export async function cloneRepo(repoUrl) {
    const res = await axios.post("http://127.0.0.1:8000/repos/clone", {
        repo_url: repoUrl
    });
    return res.data; 
}

export async function askQuestionStream(sessionId, q, onToken) {
    console.log("askQuestionStream called with:", { sessionId, q });
    
    const res = await fetch("http://127.0.0.1:8000/repos/ask/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            session_id: sessionId,
            q
        })
    });

    console.log("Response status:", res.status);
    
    if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let buffer = "";

    while (true) {
        const { value, done } = await reader.read();
        if (done) {
            console.log("Stream done");
            break;
        }

        const chunk = decoder.decode(value, { stream: true });
        console.log("Received chunk:", chunk);
        buffer += chunk;

        // Try to parse complete JSON objects from the buffer
        let startIndex = 0;
        for (let i = 0; i < buffer.length; i++) {
            if (buffer[i] === '}') {
                // Found potential end of JSON object
                const jsonStr = buffer.slice(startIndex, i + 1);
                try {
                    const parsed = JSON.parse(jsonStr);
                    console.log("Parsed JSON:", parsed);
                    if (parsed.content) {
                        onToken(parsed.content);
                    } else if (parsed.error) {
                        console.error("Stream error:", parsed.error);
                    }
                    startIndex = i + 1;
                } catch (err) {
                    // Not a complete JSON object yet, continue
                }
            }
        }
        
        // Keep remaining buffer for next iteration
        buffer = buffer.slice(startIndex);
    }
}


export async function askQuestion(sessionId, q) {
    const res = await axios.post("http://127.0.0.1:8000/repos/ask", {
        session_id: sessionId,
        q: q
    });
    return res.data;
}
