import os
import json
from together import Together
from decouple import config
from database.services import DBSessionService

os.environ["TOGETHER_API_KEY"] = config('TOGETHER_API_KEY')

class DbChatService:
    def __init__(self,user,session_id):
        self.user_id = user
        self.session_id = session_id

    def get_db_schema(self):
        db_session = DBSessionService(
            user=self.user_id,
            session_id=self.session_id
        )
        return db_session.get_full_db_schema()
    
    def get_recommend_query(self):
        db_schema = str(self.get_db_schema())
        trim_schema = self.trim_schema_by_token_limit(db_schema)
        prompt = f"""
            You are given the following MySQL database schema:

            {trim_schema}

            Your task is to suggest 5 meaningful and relevant **natural language questions** that a user might ask to explore this data.

            **Important instructions:**
            - Only use the tables and columns that are present in the schema above.
            - Do not make up or assume any new columns or tables.
            - Each question should be practical and based on what can be answered using the schema.
            - Avoid overly generic questions; aim for diverse and insightful queries.
            - Return the result strictly as a JSON array with this format, and do not include any extra text:

            [
            {{ "question": "..." }},
            {{ "question": "..." }},
            ...
            ]
        """


        client = Together()
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        output_text =  response.choices[0].message.content
        return json.loads(output_text)
    
    def get_mysql_query(self,user_question):
        db_schema = str(self.get_db_schema())
        trim_schema = self.trim_schema_by_token_limit(db_schema)
        prompt = f"""
            You are a MySQL expert.

            Here is the MySQL database schema:

            {trim_schema}

            Instructions:
            Using only the information explicitly defined in the schema above, write a valid MySQL query that answers the question below.

            Strict rules:
            - Use only table and column names that are present in the schema. Do not assume or invent any extra.
            - Do NOT use real values (e.g. names, IDs, dates). Instead, use placeholder variables in the format: {{variable_name}}.
            Example: WHERE institution_bkey = {{institution_bkey}}
            - The query must be runnable on the schema with these placeholders replaced at runtime.
            - Return ONLY the raw SQL query as a single line, with no explanation or formatting.

            Natural Language Question:
            "{user_question}"
        """
        client = Together()
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    
    def trim_schema_by_token_limit(self,schema_string: str) -> str:
        """
        Trims schema string to stay under token limit by removing unnecessary tables.
        """
        lines = schema_string.strip().splitlines()
        safe_lines = []

        excluded_prefixes = ('django_', 'auth_', 'oauth2_', 'admin_', 'session_', 'cache_', 'social_', 'log_','authtoken_')

        for line in lines:
            # Skip unnecessary tables
            table_name = line.split(' ', 1)[1].split('(', 1)[0].strip() if 'Table:' in line else ''
            if table_name.startswith(excluded_prefixes):
                continue

            safe_lines.append(line)

        return '\n'.join(safe_lines)
    
