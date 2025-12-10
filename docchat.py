import os
import requests
from tqdm import tqdm
from typing import Any, List, Mapping

from gpt4all import GPT4All
from langchain.llms.base import LLM


class MyGPT4ALL(LLM):
    """
    A custom LLM class that integrates gpt4all models
    
    Arguments:

    model_folder_path: (str) Folder path where the model lies
    model_name: (str) The name of the model to use (<model name>.bin)
    allow_download: (bool) whether to download the model or not

    backend: (str) The backend of the model (Supported backends: llama/gptj)
    n_threads: (str) The number of threads to use
    n_predict: (str) The maximum numbers of tokens to generate
    temp: (str) Temperature to use for sampling
    top_p: (float) The top-p value to use for sampling
    top_k: (float) The top k values use for sampling
    n_batch: (int) Batch size for prompt processing
    repeat_last_n: (int) Last n number of tokens to penalize
    repeat_penalty: (float) The penalty to apply repeated tokens
    
    """
    # These are required fields for the LLM, passed during initialization
    model_folder_path: str
    model_name: str
    allow_download: bool

    # all the optional arguments with default values
    backend: str | None = 'llama'
    temp: float | None = 0.7
    top_p: float | None = 0.1
    top_k: int | None = 40
    n_batch: int | None = 8
    n_threads: int | None = 4
    n_predict: int | None = 256
    max_tokens: int | None = 200
    repeat_last_n: int | None = 64
    repeat_penalty: float | None = 1.18

    # initialize the model
    gpt4_model_instance: Any = None

    def __init__(self, model_folder_path: str, model_name: str, allow_download: bool, **kwargs: Any):
        # Pass all arguments to the Pydantic BaseModel's __init__
        super().__init__(
            model_folder_path=model_folder_path,
            model_name=model_name,
            allow_download=allow_download,
            **kwargs,
        )

        # trigger auto download
        self.auto_download()

        self.gpt4_model_instance = GPT4All(
            model_name=self.model_name,
            model_path=self.model_folder_path,
        )

    def auto_download(self) -> None:
        """
        This method will download the model to the specified path
        reference: python.langchain.com/docs/modules/model_io/models/llms/integrations/gpt4all
        """

        # see whether the model name has .bin or not
        # FIX: Use self.model_name instead of an undefined local 'model_name'
        current_model_name = self.model_name
        model_name_to_check = (
            f"{current_model_name}.bin"
            if not current_model_name.endswith(".bin")
            else current_model_name
        )

        download_path = os.path.join(self.model_folder_path, model_name_to_check)

        if not os.path.exists(download_path):
            if self.allow_download:
                # send a GET request to the URL to download the file.
                # Stream it while downloading, since the file is large

                try:
                    url = f'http://gpt4all.io/models/{model_name_to_check}'  # Use the corrected model name

                    response = requests.get(url, stream=True)
                    # open the file in binary mode and write the contents of the response
                    # in chunks.

                    with open(download_path, 'wb') as f:
                        for chunk in tqdm(response.iter_content(chunk_size=8912)):
                            if chunk:
                                f.write(chunk)

                except Exception as e:
                    print(f"=> Download Failed. Error: {e}")
                    return

                print(f"=> Model: {self.model_name} downloaded sucessfully 🥳")

            else:
                print(
                    f"Model: {self.model_name} does not exists in {self.model_folder_path}",
                    "Please either download the model by allow_download = True else change the path",
                )

    @property
    def _get_model_default_parameters(self) -> Mapping[str, Any]:
        return {
            "max_tokens": self.max_tokens,
            "n_predict": self.n_predict,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "temp": self.temp,
            "n_batch": self.n_batch,
            "repeat_penalty": self.repeat_penalty,
            "repeat_last_n": self.repeat_last_n,
        }

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """
        Get all the identifying parameters
        """
        return {
            'model_name': self.model_name,
            'model_path': self.model_folder_path,
            'model_parameters': self._get_model_default_parameters,
        }

    @property
    def _llm_type(self) -> str:
        return 'llama'

    def _call(self, prompt: str, stop: List[str] | None = None, **kwargs: Any) -> str:
        """
        Args:
            prompt: The prompt to pass into the model.
            stop: A list of strings to stop generation when encountered

        Returns:
            The string generated by the model        
        """

        params = {
            **self._get_model_default_parameters,
            **kwargs,
        }

        resposne = self.gpt4_model_instance.generate(prompt, **params)
        return resposne
