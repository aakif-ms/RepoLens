"use client";

import { useState } from "react";

import { cloneRepo, askQuestion } from "@/lib/api";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRepoCloned, setIsRepoCloned] = useState(false);

  async function handleCloneRepo() {
    setLoading(true);
    try {
      await cloneRepo(repoUrl);
      setIsRepoCloned(true);
    } catch (error) {
      console.error("Error cloning repo:", error);
    }
    setLoading(false);
  }

  async function handleAsk() {
    setLoading(true);
    try {
      const res = await askQuestion(question);
      setAnswer(res.data.answer);
    } catch (error) {
      console.error("Error asking question:", error);
    }
    setLoading(false);
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-muted p-6">
      <Card className="w-full max-w-2xl p-6 space-y-4">
        <h1 className="text-2xl font-bold">RepoLens</h1>

        {!isRepoCloned ? (
          <>
            <Input 
              placeholder="Github Repository URL" 
              value={repoUrl} 
              onChange={(e) => setRepoUrl(e.target.value)} 
            />
            <Button 
              onClick={handleCloneRepo} 
              disabled={loading || !repoUrl.trim()}
            >
              {loading ? "Cloning Repository..." : "Clone Repository"}
            </Button>
          </>
        ) : (
          <>
            <div className="text-sm text-muted-foreground mb-2">
              Repository cloned: {repoUrl}
            </div>
            <Textarea 
              placeholder="Ask about the codebase..." 
              value={question} 
              onChange={(e) => setQuestion(e.target.value)} 
            />
            <Button 
              onClick={handleAsk} 
              disabled={loading || !question.trim()}
            >
              {loading ? "Analyzing..." : "Ask"}
            </Button>
            <Button 
              variant="outline" 
              onClick={() => {
                setIsRepoCloned(false);
                setRepoUrl("");
                setQuestion("");
                setAnswer("");
              }}
            >
              Clone Different Repository
            </Button>
          </>
        )}

        {answer && (
          <pre className="bg-black text-green-400 p-4 rounded text-sm overflow-x-auto">{answer}</pre>
        )}
      </Card>
    </main>
  )
}