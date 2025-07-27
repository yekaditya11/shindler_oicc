from dotenv import load_dotenv
load_dotenv()
import os
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate 
from typing import TypedDict, Dict, Any, List, Optional
from convBI_engine.prompts import intent_prompt,greeting_prompt,file_identification_prompt,required_columns_prompt,text_to_sql_prompt,prompt_ddl,summarizer_prompt,clarification_prompt
import json
import psycopg


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
        print(self.round_robin_count)
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
        prompt=ChatPromptTemplate.from_messages(intent_prompt)
        prez_conv=state["history"]
        if len(state["history"])>2:
            prez_conv=state["history"][-2:]

        chain = prompt | self.llm
        result = chain.invoke({
            "question": state["question"],
            "history": prez_conv
        })
        state["intent"] = result.content.strip().lower()

        return state
    
    def _greeting_agent(self, state: WorkflowState)-> WorkflowState:
        prompt=ChatPromptTemplate.from_messages(greeting_prompt)
        chain = prompt | self.llm
        result = chain.invoke({
            "question": state["question"]
        })
        state["final_answer"] = result.content.strip().lower()

        return state
    
    def _file_identification_agent(self, state: WorkflowState)-> WorkflowState:
        prompt=ChatPromptTemplate.from_messages(file_identification_prompt)
        prez_conv=state["history"]
        if len(state["history"])>2:
            prez_conv=state["history"][-2:]
        chain = prompt | self.llm
        result = chain.invoke({
            "question": state["question"],
            "history": prez_conv,
            "ddl": state["database_ddl"]
        })
        state["filename"] = result.content.strip().lower()

        return state
    
    def _top_5_unique_values_of_columns_retriever_agent(self, state: WorkflowState) -> WorkflowState:
        try:
            with open("convBI_engine/column_analysis_top5.json", "r") as top_5_context_info_json:
                top_5_context_info = json.load(top_5_context_info_json)
            if state["filename"]:
               state["top_5_unique_values_of_columns"] = top_5_context_info.get(state["filename"], {})
            #    print(f"Top 5 unique values of columns: {state['top_5_unique_values_of_columns']}")
        except FileNotFoundError:
            print("Warning: column_analysis_top5.json not found")
            state["top_5_unique_values_of_columns"] = {}
        return state


    def _required_columns_info_retriever_agent(self, state: WorkflowState) -> WorkflowState:
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
            # Fallback if JSON parsing fails
            state["required_unique_column_names"] = []
        return state
    
    def _text_to_sql_agent(self, state: WorkflowState) -> WorkflowState:
        # Extract previous SQL queries from PostgreSQL history for context

        prompt = ChatPromptTemplate.from_messages(text_to_sql_prompt)
        prez_conv=state["history"]
        if len(state["history"])>2:
            prez_conv=state["history"][-2:]
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
        # state["history"]=[result]
        print(f"SQL Query generated: {state['sql_query']}")
        return state
    
    def _get_db_connection(self):
        try:
            # Get connection parameters from environment
            host = os.getenv('POSTGRES_HOST', 'localhost')
            port = os.getenv('POSTGRES_PORT', '5432')
            database = os.getenv('POSTGRES_DB', 'defaultdb')
            user = os.getenv('POSTGRES_USER', 'postgres')
            password = os.getenv('POSTGRES_PASSWORD', '')
            
            # Determine SSL mode based on host
            sslmode = 'require' if 'aiven' in host or 'cloud' in host else 'prefer'
            
            # Create connection with proper SSL configuration
            connection = psycopg.connect(
                host=host,
                port=port,
                dbname=database,
                user=user,
                password=password,
                sslmode=sslmode,
                connect_timeout=10,
                application_name='Shindler_ConvBI'
            )
            
            return connection
        except psycopg.Error as e:
            print(f"Database connection error: {e}")
            # Try fallback connection without SSL for local development
            try:
                print("Attempting fallback connection without SSL...")
                connection = psycopg.connect(
                    host=host,
                    port=port,
                    dbname=database,
                    user=user,
                    password=password,
                    sslmode='disable',
                    connect_timeout=10,
                    application_name='Shindler_ConvBI'
                )
                print("Fallback connection successful")
                return connection
            except psycopg.Error as fallback_error:
                print(f"Fallback connection also failed: {fallback_error}")
                return None
  
    def _execute_sql_query(self, state: WorkflowState) -> WorkflowState:
        try:
            conn = self._get_db_connection()
            if not conn:
                state["error_message"] = "Could not establish database connection. Please check your database configuration."
                state["needs_clarification"] = True
                return state
            
            cursor = conn.cursor()
            cursor.execute(state["sql_query"])
           
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            formatted_results = []
            for row in results:
                row_dict = dict(zip(columns, row))
                formatted_results.append(row_dict)
            
            state["query_result"] = str(formatted_results)
            state["history"]=[{"role":"system", "content":f"query_result: {state['query_result']}"}]
            # print(f"SQL Query executed: {state['query_result']}")
            state["needs_clarification"] = False
            cursor.close()
            conn.close()
            
        except psycopg.Error as db_error:
            error_msg = f"Database error: {str(db_error)}"
            state["error_message"] = error_msg
            state["needs_clarification"] = True
            print(f"SQL execution database error: {db_error}")
        except Exception as e:
            error_msg = f"Query execution error: {str(e)}"
            state["error_message"] = error_msg
            state["needs_clarification"] = True
            print(f"SQL execution general error: {e}")
        return state
    
    def _summarizer_agent(self, state: WorkflowState) -> WorkflowState:
        prompt = ChatPromptTemplate.from_messages(summarizer_prompt)
        prez_conv=state["history"]
        if len(state["history"])>2:
            prez_conv=state["history"][-2:]
        chain = prompt | self.llm
        result = chain.invoke({
            "question": state["question"],
            "history": prez_conv,
            "query_result": state["query_result"],
            "filename": state["filename"]
        })
        state["final_answer"] = result.content.strip().lower()
        print(f"Final answer: {state['final_answer']}")
        return state
    
    def _clarification_agent(self, state: WorkflowState) -> WorkflowState:
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
        print(f"Clarification answer: {state['final_answer']}")
        return state
    
    def _visualization_agent(self, state: WorkflowState) -> WorkflowState:
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
            prez_conv=state["history"]
            if len(state["history"])>2:
                prez_conv=state["history"][-2:]

            result = chain.invoke({
                "question": question,
                "query_result":results, # Pass the results as JSON string to GPT
                "history": prez_conv
            })
            # Parse the output and save the JSON to state

            state["visualization_data"] = json.loads(result.content.strip())  # Save the generated JSON
            print(state["visualization_data"])
            
        except json.JSONDecodeError as e:
            state["error_message"] = f"Error generating visualization data: {e}"
            state["needs_clarification"] = True
            print(f"hi Error: {e}")
        
        return state
     


    
    
    
    def run_workflow(self, question: str,  thread_id: str = "1") -> Dict[str, Any]:
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
        # DB_URI = "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable"
        DB_URI = f"postgres://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
            # checkpointer.setup()

            workflow = self._build_workflow()
            graph = workflow.compile(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": "1"}}
            final_state = graph.invoke(state, config)
            return {
            "final_answer": final_state["final_answer"],
            "visualization_data": final_state["visualization_data"],
            }


if __name__ == "__main__":
    workflow = TextToSQLWorkflow()
    final_state = workflow.run_workflow("Compare the number of no-go violations in Mumbai 1, Hyderabad 1, Gurgaon and Bangalore 1.")
    # print(final_state["query_result"], final_state["filename"])




    # graph_builder = StateGraph(WorkflowState)

    # graph_builder.add_node("chatbot", chatbot)

