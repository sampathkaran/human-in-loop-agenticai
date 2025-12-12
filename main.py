from typing import TypedDict, Annotated, List
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import add_messages, StateGraph, END
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
from dotenv import load_dotenv
import uuid

load_dotenv()

class AgentState(TypedDict):
    linkedin_topic: str
    generated_post : Annotated[List[str], add_messages]
    human_feedback: Annotated[List[str], add_messages]


# define a model node

def model_node(state:AgentState):
    """Here we will use llm to generate a linkedin post with human in loop"""
    print("[mmodel] Generating Content")
    linkedin_topic = state['linkedin_topic']
    human_feedback = state["human_feedback"] if "human_feedback" in state else ["No feedback yet"]

    # define the prompt for the llm

    prompt = f"""
    
       LinkedIn Topic: {linkedin_topic}
       Human Feeback : {human_feedback[-1] if human_feedback else "No feedback yet" }
       
       Generate a refined Linkein post based on the topic and also consider the human feedback when generating responses        
       """
    
    llm= ChatOpenAI(model = "gpt-5-nano")
    response = llm.invoke([
        SystemMessage(content="You are an expert Linkedin cotent writer"),
        HumanMessage(content=prompt)
    ])

    generated_post = response.content

    print(f"[model_node] Generated Post: \n {generated_post}")

    return {
        "generated_post" : [AIMessage(content=generated_post)],
        "human_feedback" : human_feedback
    }


#define the human node where we will show the model node message and ask feedback if it is goodf

def human_node(state:AgentState):
    """ humasn Intervention Node-  loops back to the model node unless the useer input done"""
    generated_post = state['generated_post']
    print("Waiting for the human feedback")

    #Interrupt function to ask for feedback

    user_input = interrupt(
        {
            "generated_post" : generated_post,
            "message": "Provide feedback for type 'done' to complete the review: "
            
        }
    )
    print(f"[human_node] Received Human Feedback : {user_input}")

    #if user types done end the graph and print the final output

    if user_input.lower() == 'done':
        return Command(update={"human_feedback" : state["human_feedback"]}, goto="end_node")
    
    #otherwise update the feeback to the model node to refine the response
    return Command(update={"human_feedback" : state["human_feedback"]+[user_input]}, goto="model_node")

def end_node(state:AgentState):
    """Final End Node"""
    print("\n[End Node] Process Finished")
    print("\nFinal Generate post", state["generated_post"][-1].content)
    print("\n Human Feedback", state["human_feedback"])  
    return Command(goto=END)
    
graph = StateGraph(AgentState)

graph.add_node("model_node",model_node )
graph.add_node("human_node",human_node)
graph.add_node("end_node", end_node)

graph.set_entry_point("model_node")
graph.add_edge("model_node", "human_node")


checkpointer = MemorySaver()

app = graph.compile(checkpointer=checkpointer)

config = {"configurable":{
    "thread_id" : uuid.uuid4()
}}

#set the initial state
linkedin_topic = input("Enter the linkedin topic: ")
initial_state = {
    "linkedin_topic" : linkedin_topic,
    "generated_post": [],
    "human_feedback": []
}

#stream it to see the entire node messafes

events = app.stream(initial_state, config=config,)

for event in events:
    for node_id, value in event.items():
        if(node_id == "__interrupt__"):
            while True: 
                user_feedback = input("Provide feedback (or type 'done' when finished): ")

                # Resume the graph execution with the user's feedback
                app.invoke(Command(resume=user_feedback), config=config)

                # Exit loop if user says done
                if user_feedback.lower() == "done":
                    break
