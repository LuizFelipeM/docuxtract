import json
import logging
from time import time
from pydantic import BaseModel
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.output_parsers import PydanticOutputParser

from ...logger import logger


def interpret_text(
    text: str,
    query: str,
    model: str,
    output_cls: type[BaseModel],
    *,
    prompt_json_schema=False,
) -> BaseModel:
    start_time = time()

    Settings.llm = Ollama(
        model=model, temperature=0.2, request_timeout=360.0, json_mode=True
    )

    prog = LLMTextCompletionProgram.from_defaults(
        output_parser=PydanticOutputParser(output_cls=output_cls),
        prompt_template_str="""
        You are responsible for extracting the required query from an XML file and output the results as a JSON {json_schema}\
        XML: {xml}\
        query: {query}
        """,
        verbose=True,
    )

    json_schema = ""
    if prompt_json_schema:
        json_schema = f"""
        based on the following JSON schema:\
        {json.dumps(output_cls.model_json_schema(), indent=2)}
        """

    result = prog(xml=text, query=query, json_schema=json_schema)

    end_time = time()
    logger.log(
        logging.INFO, f"Elapsed time of {model} = {end_time - start_time} seconds"
    )

    return result
