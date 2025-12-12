# human-in-loop-agenticai
This repo is to demo a blogpost agent get feedback from human and create a post
# LinkedIn Post Generator with Human-in-the-Loop

This project is an interactive LinkedIn post generator that combines **LLM-based content generation** with **human feedback** using a state machine workflow. It leverages LangGraph and LangChain to create a loop where an AI generates content and a human can iteratively refine it.

---

## Features

- Generates LinkedIn posts based on a topic provided by the user.  
- Human-in-the-loop feedback loop: humans can review and refine AI-generated content.  
- State machine-based workflow using `StateGraph` to manage nodes and transitions.  
- Tracks history of generated posts and feedback.  
- Graceful termination after human indicates the process is complete.  

---
