try:
    from opik.evaluation import models
    from opik.evaluation.metrics import GEval
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    # Stub classes when opik is not available
    class models:
        pass
    class GEval:
        pass

from src.config import settings
from src.utils.logger_util import setup_logging

logger = setup_logging()

# -----------------------
# Evaluation helper
# -----------------------


async def evaluate_metrics(output: str, context: str) -> dict:
    """Evaluate multiple metrics for a given LLM output.
    Metrics included: faithfulness, coherence, completeness.

    Args:
        output (str): The LLM-generated output to evaluate.
        context (str): The context used to generate the output.

    Returns:
        dict: A dictionary with metric names as keys and their evaluation results as values.

    """
    # OpenAI settings removed - evaluation metrics disabled
    logger.info("Evaluation metrics disabled - OpenAI settings removed")
    return {
        "faithfulness": {"score": None, "reason": "Skipped – OpenAI removed", "failed": True},
        "coherence": {"score": None, "reason": "Skipped – OpenAI removed", "failed": True},
        "completeness": {"score": None, "reason": "Skipped – OpenAI removed", "failed": True},
    }
