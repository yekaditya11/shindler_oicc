from dotenv import load_dotenv
load_dotenv()
import os
from typing import Annotated
import logging
from datetime import datetime

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate 
from typing import TypedDict, Dict, Any, List, Optional
from .prompts import intent_prompt,greeting_prompt,file_identification_prompt,required_columns_prompt,text_to_sql_prompt,prompt_ddl,summarizer_prompt,clarification_prompt
import json
import psycopg

logger = logging.getLogger(__name__)

class WorkflowState(TypedDict):

    history: Annotated[list, add_messages]
    question: str
    filename: str
    intent: str
    context_info: str
    database_ddl: str
    rephrased_question: str
    sql_query: str
    query_result: str
    categorical_colums_data: str
    final_answer: str
    error_message: str
    needs_clarification: bool
    top_5_unique_values_of_columns:Dict[str, Any]
    required_unique_column_names:List[str]
    required_unique_column_values:List[str]
    visualization_data:Dict[str, Any]


class TextToSQLWorkflow:
    def __init__(self):
        with open("convBI_engine/round_robin.json", "r") as round_robin_json:
            self.round_robin_count = json.load(round_robin_json)["count"]
        self.round_robin_count = self.round_robin_count 
        logger.info(f"Using Azure OpenAI endpoint {self.round_robin_count}")
        self.llm = AzureChatOpenAI(
        azure_endpoint=os.environ[f"AZURE_OPENAI_ENDPOINT_{self.round_robin_count}"],
        azure_deployment=os.environ[f"AZURE_OPENAI_DEPLOYMENT_NAME_{self.round_robin_count}"],
        openai_api_version=os.environ[f"AZURE_OPENAI_API_VERSION_{self.round_robin_count}"],
        api_key=os.environ[f"AZURE_OPENAI_API_KEY_{self.round_robin_count}"]
        )
        with open("convBI_engine/round_robin.json", "w") as round_robin_json:
            json.dump({"count": (self.round_robin_count+1)%3}, round_robin_json)



    def _build_workflow(self)-> StateGraph[WorkflowState]:
        graph_builder = StateGraph(WorkflowState)
        graph_builder.add_node("intent_classification", self._intent_classification_agent)
        graph_builder.add_node("greeting", self._greeting_agent)
        graph_builder.add_node("file_identification", self._file_identification_agent)
        graph_builder.add_node("top_5_unique_values_of_columns_retriever", self._top_5_unique_values_of_columns_retriever_agent)
        graph_builder.add_node("text_to_sql", self._text_to_sql_agent)
        graph_builder.add_node("execute_sql_query", self._execute_sql_query)
        graph_builder.add_node("required_columns_info_retriever", self._required_columns_info_retriever_agent)
        graph_builder.add_node("summarizer", self._summarizer_agent)
        graph_builder.add_node("clarification_agent", self._clarification_agent)
        graph_builder.add_node("visualization",self._visualization_agent)

        graph_builder.add_edge(START, "intent_classification")
        graph_builder.add_conditional_edges(
            "intent_classification",
            lambda state: state["intent"] == "general",
            {True: "greeting", False: "file_identification"}
           
        )
        graph_builder.add_edge("file_identification", "top_5_unique_values_of_columns_retriever")
        graph_builder.add_edge("top_5_unique_values_of_columns_retriever", "text_to_sql")
        graph_builder.add_edge("text_to_sql", "execute_sql_query")
        graph_builder.add_conditional_edges(
            "execute_sql_query", 
            lambda state:state["needs_clarification"]==True,
            {True:"clarification_agent", False: "summarizer"})

        graph_builder.add_edge("greeting", END)
        graph_builder.add_edge("execute_sql_query", "summarizer")
        graph_builder.add_edge("summarizer", "visualization")
        graph_builder.add_edge("visualization", END)
        graph_builder.add_edge("clarification_agent", END)
        return graph_builder
    
    def _intent_classification_agent(self, state: WorkflowState)-> WorkflowState:
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - INTENT CLASSIFICATION STARTED")
        start_time = datetime.now()
        
        prompt=ChatPromptTemplate.from_messages(intent_prompt)
        # Optimize history to reduce state size
        prez_conv = state["history"][-1:] if state["history"] else []

        chain = prompt | self.llm
        result = chain.invoke({
            "question": state["question"],
            "history": prez_conv
        })
        state["intent"] = result.content.strip().lower()
        
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - INTENT CLASSIFICATION COMPLETED: {state['intent']} - TIME: {process_time:.3f}s")

        return state
    
    def _greeting_agent(self, state: WorkflowState)-> WorkflowState:
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - GREETING AGENT STARTED")
        start_time = datetime.now()
        
        prompt=ChatPromptTemplate.from_messages(greeting_prompt)
        chain = prompt | self.llm
        result = chain.invoke({
            "question": state["question"]
        })
        state["final_answer"] = result.content.strip().lower()
        
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - GREETING AGENT COMPLETED - TIME: {process_time:.3f}s")

        return state
    
    def _file_identification_agent(self, state: WorkflowState)-> WorkflowState:
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - FILE IDENTIFICATION STARTED")
        start_time = datetime.now()
        
        prompt=ChatPromptTemplate.from_messages(file_identification_prompt)
        # Optimize history to reduce state size
        prez_conv = state["history"][-1:] if state["history"] else []
        chain = prompt | self.llm
        result = chain.invoke({
            "question": state["question"],
            "history": prez_conv,
            "ddl": state["database_ddl"]
        })
        state["filename"] = result.content.strip().lower()
        
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - FILE IDENTIFICATION COMPLETED: {state['filename']} - TIME: {process_time:.3f}s")

        return state
    
    def _top_5_unique_values_of_columns_retriever_agent(self, state: WorkflowState) -> WorkflowState:
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - TOP 5 COLUMNS RETRIEVER STARTED")
        start_time = datetime.now()
        
        try:
            with open("convBI_engine/column_analysis_top5.json", "r") as top_5_context_info_json:
                top_5_context_info = json.load(top_5_context_info_json)
            if state["filename"]:
               state["top_5_unique_values_of_columns"] = top_5_context_info.get(state["filename"], {})
            
            process_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - TOP 5 COLUMNS RETRIEVER COMPLETED - TIME: {process_time:.3f}s")
        except FileNotFoundError:
            logger.warning(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - column_analysis_top5.json not found")
            state["top_5_unique_values_of_columns"] = {}
        return state


    def _required_columns_info_retriever_agent(self, state: WorkflowState) -> WorkflowState:
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - REQUIRED COLUMNS RETRIEVER STARTED")
        start_time = datetime.now()
        
        prompt = ChatPromptTemplate.from_messages(required_columns_prompt)

        chain = prompt | self.llm
        prez_conv=state["history"]
        if len(state["history"])>2:
            prez_conv=state["history"][-2:]
        result = chain.invoke({
            "question": state["question"],
            "query": state["sql_query"],
            "error_message": state["error_message"],
            "col_info": state["top_5_unique_values_of_columns"],
            "history": prez_conv
        })
        final_result = result.content.strip()
        try:
            state["required_unique_column_names"] = json.loads(final_result)
        except json.JSONDecodeError:
            logger.warning(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - JSON parsing failed for required columns")
            state["required_unique_column_names"] = []
        
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - REQUIRED COLUMNS RETRIEVER COMPLETED - TIME: {process_time:.3f}s")
        return state
    
    def _text_to_sql_agent(self, state: WorkflowState) -> WorkflowState:
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - TEXT TO SQL STARTED")
        start_time = datetime.now()
        
        prompt = ChatPromptTemplate.from_messages(text_to_sql_prompt)
        # Optimize history to reduce state size
        prez_conv = state["history"][-1:] if state["history"] else []
        chain = prompt | self.llm
        result = chain.invoke({
            "ddl": state["database_ddl"],
            "col_info": state["top_5_unique_values_of_columns"],
            "question": state["question"],
            "history": prez_conv
        })
        # Clean the SQL query by removing markdown formatting
        sql_content = result.content.strip()
        if sql_content.startswith("```sql"):
            sql_content = sql_content[6:]  # Remove ```sql
        if sql_content.startswith("```"):
            sql_content = sql_content[3:]   # Remove ```
        if sql_content.endswith("```"):
            sql_content = sql_content[:-3]  # Remove trailing ```
        state["sql_query"] = sql_content.strip()
        
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - TEXT TO SQL COMPLETED: {state['sql_query']} - TIME: {process_time:.3f}s")
        return state
    
    def _get_db_connection(self):
        try:
            DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
            connection = psycopg.connect(DATABASE_URL)
            return connection
        except psycopg.Error as e:
            logger.error(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - DATABASE CONNECTION ERROR: {e}")
            return None
  
    def _execute_sql_query(self, state: WorkflowState) -> WorkflowState:
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - SQL EXECUTION STARTED")
        start_time = datetime.now()
        
        try:
            conn = self._get_db_connection()
            if not conn:
                raise Exception("Could not establish database connection")
            
            cursor = conn.cursor()
            cursor.execute(state["sql_query"])
           
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            formatted_results = []
            for row in results:
                row_dict = dict(zip(columns, row))
                formatted_results.append(row_dict)
            
            state["query_result"] = str(formatted_results)
            # Optimize state by storing only essential query info
            state["history"] = [{"role":"system", "content":f"query_result_count: {len(results)}"}]
            state["needs_clarification"] = False
            
            process_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - SQL EXECUTION SUCCESS - ROWS: {len(results)} - TIME: {process_time:.3f}s")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            state["error_message"] = str(e)
            state["needs_clarification"] = True
            
            process_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - SQL EXECUTION ERROR: {e} - TIME: {process_time:.3f}s")
            
        return state
    
    def _summarizer_agent(self, state: WorkflowState) -> WorkflowState:
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - SUMMARIZER STARTED")
        start_time = datetime.now()
        
        prompt = ChatPromptTemplate.from_messages(summarizer_prompt)
        # Optimize history to reduce state size
        prez_conv = state["history"][-1:] if state["history"] else []
        chain = prompt | self.llm
        result = chain.invoke({
            "question": state["question"],
            "history": prez_conv,
            "query_result": state["query_result"],
            "filename": state["filename"]
        })
        state["final_answer"] = result.content.strip().lower()
        
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - SUMMARIZER COMPLETED - TIME: {process_time:.3f}s")
        
        return state
    
    def _clarification_agent(self, state: WorkflowState) -> WorkflowState:
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - CLARIFICATION AGENT STARTED")
        start_time = datetime.now()
        
        prompt = ChatPromptTemplate.from_messages(clarification_prompt)
        prez_conv=state["history"]
        if len(state["history"])>2:
            prez_conv=state["history"][-2:]
        chain = prompt | self.llm
        result = chain.invoke({
            "question": state["question"],
            "history": prez_conv,
            "error_message": state["error_message"]
        })
        state["final_answer"] = result.content.strip().lower()
        
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - CLARIFICATION AGENT COMPLETED - TIME: {process_time:.3f}s")
        
        return state
    
    def _visualization_agent(self, state: WorkflowState) -> WorkflowState:
        logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - VISUALIZATION AGENT STARTED")
        start_time = datetime.now()
        
        """
        This agent uses GPT to generate a JSON for Apache ECharts based on the summary data.
        It creates a chart configuration in the ECharts JSON format.
        """
        question = state["question"]
        query_result = state["query_result"]
        
        # Assuming the query result is a list of dictionaries, let's pass it along with the question to GPT.
        try:
            # Parse the result (assuming it's a list of dictionaries)
            results = query_result

            # Now prompt GPT to generate the ECharts JSON for visualization
            prompt = ChatPromptTemplate.from_template(
                """
                Based on the following question and the query result data, generate an ECharts JSON  configuration for a chart:
                previous conversation: {history}

                Question: {question}
                Query Result Data (Assuming it's a list of dictionaries with column names and values): {query_result}

                Generate a JSON in the ECharts format suitable for a bar chart, line chart, or pie chart, depending on the question. Include any necessary configuration like xAxis, yAxis, series, tooltip, etc.
                #Instruction
                - Do generate Echarts only if it makes meaningful to generate chart based on the Question and Query Result Data
                - Respon with JSON no extra information/explanation need.
                - Don't add ```json or ``` in the output 
                - if you feel chat makes no meaning for the give Question and Query Result Data just return empty json curly braces
                """
            )

            chain = prompt | self.llm  # Assuming `self.llm` is already initialized as AzureChatOpenAI
            # Optimize history to reduce state size
            prez_conv = state["history"][-1:] if state["history"] else []

            result = chain.invoke({
                "question": question,
                "query_result":results, # Pass the results as JSON string to GPT
                "history": prez_conv
            })
            # Parse the output and save the JSON to state

            state["visualization_data"] = json.loads(result.content.strip())  # Save the generated JSON
            
            process_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - VISUALIZATION AGENT COMPLETED - TIME: {process_time:.3f}s")
            
        except json.JSONDecodeError as e:
            state["error_message"] = f"Error generating visualization data: {e}"
            state["needs_clarification"] = True
            
            process_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"REQUEST_ID: {getattr(self, 'request_id', 'unknown')} - VISUALIZATION AGENT ERROR: {e} - TIME: {process_time:.3f}s")
        
        return state
     


    
    
    
    def run_workflow(self, question: str,  thread_id: str = "1", request_id: str = None) -> Dict[str, Any]:
        # Store request_id for logging
        self.request_id = request_id or "unknown"
        
        logger.info(f"REQUEST_ID: {self.request_id} - WORKFLOW STARTED - QUESTION: {question}")
        workflow_start_time = datetime.now()
        
        state = WorkflowState(
                history=[{"role":"user", "content": question}],
                question=question,
                filename="",
                intent="",
                context_info="",
                database_ddl=prompt_ddl,
                rephrased_question="",
                sql_query="",
                query_result="",
                categorical_colums_data="",
                final_answer="",
                error_message="",
                needs_clarification=False,
                top_5_unique_values_of_columns={},
                required_unique_column_names=[],
                required_unique_column_values=[],
                visualization_data={}
            )
        
        try:
            # Remove PostgreSQL checkpointing for better performance
            workflow = self._build_workflow()
            build_time = (datetime.now() - workflow_start_time).total_seconds()
            logger.info(f"REQUEST_ID: {self.request_id} - WORKFLOW BUILT - TIME: {build_time:.3f}s")
            
            graph = workflow.compile()  # Remove checkpointer parameter
            compile_time = (datetime.now() - workflow_start_time).total_seconds()
            logger.info(f"REQUEST_ID: {self.request_id} - GRAPH COMPILED - TIME: {compile_time:.3f}s")
            
            config = {"configurable": {"thread_id": "1"}}
            final_state = graph.invoke(state, config)
            
            workflow_time = (datetime.now() - workflow_start_time).total_seconds()
            logger.info(f"REQUEST_ID: {self.request_id} - WORKFLOW COMPLETED SUCCESSFULLY - TOTAL TIME: {workflow_time:.3f}s")
            
            return {
            "final_answer": final_state["final_answer"],
            "visualization_data": final_state["visualization_data"],
            }
        except Exception as e:
            workflow_time = (datetime.now() - workflow_start_time).total_seconds()
            logger.error(f"REQUEST_ID: {self.request_id} - WORKFLOW FAILED: {str(e)} - TOTAL TIME: {workflow_time:.3f}s")
            raise


if __name__ == "__main__":
    workflow = TextToSQLWorkflow()
    final_state = workflow.run_workflow("Compare the number of no-go violations in Mumbai 1, Hyderabad 1, Gurgaon and Bangalore 1.")
    # print(final_state["query_result"], final_state["filename"])




    # graph_builder = StateGraph(WorkflowState)

    # graph_builder.add_node("chatbot", chatbot)

