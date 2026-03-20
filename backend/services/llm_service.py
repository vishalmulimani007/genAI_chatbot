import requests
from config_loader import ConfigLoader


class LLMService:
    """
    Handles interaction with Ollama LLM.
    """

    def __init__(self):
        config_loader = ConfigLoader()
        llm_config = config_loader.get_section("llm")

        self.model_name = llm_config["model"]
        self.base_url = llm_config.get("base_url", "http://localhost:11434")
        self.temperature = llm_config.get("temperature", 0.2)

    def generate(self, prompt: str) -> str:
        """
        Generate response using Ollama.
        """

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature
                    }
                },
                timeout=120
            )

            if response.status_code != 200:
                raise ValueError(f"Ollama error: {response.text}")

            data = response.json()

            return data.get("response", "").strip()

        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}")