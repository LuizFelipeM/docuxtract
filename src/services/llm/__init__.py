import json
import logging
import os
from time import time
from pydantic import BaseModel
from llama_index.llms.ollama import Ollama
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.output_parsers import PydanticOutputParser

from ...logger import logger


def interpret_text(
    text: str,
    model: str,
    output_cls: type[BaseModel],
    metadata: str,
    *,
    query: str = None,
    prompt_json_schema=False,
    language: str = "en",
) -> BaseModel:
    start_time = time()

    prog = LLMTextCompletionProgram.from_defaults(
        output_parser=PydanticOutputParser(output_cls=output_cls),
        prompt_template_str=(
            """Você é responsável por extrair desse arquivo XML as informações solicitadas e retornar os resultados em JSON {json_schema}\
        Informações necessárias: {query}\
        Arquivo XML:\
        {xml}"""
            if language == "pt"
            else """You are responsible for extracting the required query from an XML file and output the results as a JSON {json_schema}\
        Required information: {query}
        XML file:
        {xml}"""
        ),
        llm=Ollama(
            model=model,
            base_url=os.getenv("OLLAMA_HOST"),
            temperature=0,
            request_timeout=360.0,
            json_mode=True,
        ),
        verbose=True,
    )

    json_schema = ""
    if prompt_json_schema:
        json_schema = (
            f"""de acordo com o modelo:\
        {json.dumps(output_cls.model_json_schema(), indent=2)}
        """
            if language == "pt"
            else f"""based on the following JSON schema:\
        {json.dumps(output_cls.model_json_schema(), indent=2)}
        """
        )

    result = prog(xml=text, query=query if query else metadata, json_schema=json_schema)

    end_time = time()
    logger.log(
        logging.INFO, f"Elapsed time of {model} = {end_time - start_time} seconds"
    )

    return result
