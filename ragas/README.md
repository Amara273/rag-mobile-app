# RAGAS Evaluation Framework for RAG Chatbot

This directory contains the RAGAS (Retrieval-Augmented Generation Assessment) evaluation framework for testing your RAG chatbot's quality and reliability.

## Overview

RAGAS is a framework for evaluating RAG (Retrieval-Augmented Generation) systems. It provides metrics to assess:

- **Faithfulness**: Measures if the generated answer is consistent with the retrieved context (lower hallucination)
- **Answer Relevancy**: Measures if the generated answer directly addresses the question asked
- **Context Relevancy**: Measures if the retrieved context pieces are relevant to the question
- **Hallucination Detection**: Identifies when the model generates information not present in the context

## Files

- `script.py` - Main evaluation script
- `data.json` - Test data containing questions, answers, and their retrieval contexts
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Installation

### 1. Install Dependencies

```bash
# Navigate to the ragas directory
cd ragas

# Install RAGAS and related packages
pip install -r requirements.txt
```

### 2. Set Up OpenAI API Key

The script uses OpenAI's models for evaluation. Set your API key:

```bash
# On Windows PowerShell
$env:OPENAI_API_KEY = "your-openai-api-key"

# On Linux/macOS
export OPENAI_API_KEY="your-openai-api-key"
```

## Usage

### Basic Usage

```bash
# Run evaluation using default data.json
python script.py

# Specify custom data file
python script.py --data-file custom_data.json

# Specify output report file
python script.py --output my_report.json

# Use different LLM model
python script.py --model gpt-4
```

### Creating Sample Data

The `data.json` file already contains sample test cases. To regenerate or update it:

```bash
python script.py --create-sample
```

## Data Format

The `data.json` file should contain a JSON array with test cases. Each test case has:

```json
[
  {
    "question": "What is machine learning?",
    "answer": "Machine learning is a subset of artificial intelligence...",
    "contexts": [
      "Context from retrieval system 1",
      "Context from retrieval system 2"
    ]
  }
]
```

### Fields

- **question** (string): The user's question
- **answer** (string): The RAG system's answer/response
- **contexts** (array of strings): Retrieved context pieces that the answer should be based on

## Understanding the Metrics

### Faithfulness Score (0-1)
- **High score (>0.8)**: Answer is well-grounded in the context
- **Medium score (0.5-0.8)**: Answer is mostly grounded but has minor inconsistencies
- **Low score (<0.5)**: Answer contains significant hallucinations

### Answer Relevancy Score (0-1)
- **High score (>0.8)**: Answer directly addresses the question
- **Medium score (0.5-0.8)**: Answer partially addresses the question
- **Low score (<0.5)**: Answer is not relevant to the question

### Context Relevancy Score (0-1)
- **High score (>0.8)**: Retrieved context is highly relevant
- **Medium score (0.5-0.8)**: Context is somewhat relevant
- **Low score (<0.5)**: Retrieved context is not relevant to the question

## Output

The script generates a `ragas_report.json` file containing:

```json
{
  "timestamp": "2024-01-15T10:30:00.123456",
  "model": "gpt-3.5-turbo",
  "metrics": {
    "faithfulness": {
      "scores": [0.92, 0.88, 0.95, ...],
      "mean": 0.91,
      "min": 0.85,
      "max": 0.98
    },
    "answer_relevancy": {
      "scores": [0.94, 0.91, 0.93, ...],
      "mean": 0.92,
      "min": 0.88,
      "max": 0.97
    },
    "context_relevancy": {
      "scores": [0.89, 0.92, 0.90, ...],
      "mean": 0.90,
      "min": 0.85,
      "max": 0.95
    }
  }
}
```

## Integration with Your RAG System

To evaluate your own RAG system:

1. **Collect Test Cases**: Create question-answer pairs with their retrieved contexts
2. **Format Data**: Add them to `data.json` in the required format
3. **Run Evaluation**: Execute `python script.py`
4. **Review Results**: Check the generated report for improvement areas

Example integration in your backend:

```python
# In your RAG backend
from ragas.script import RAGASEvaluator

evaluator = RAGASEvaluator(
    data_file="test_cases.json",
    model_name="gpt-3.5-turbo"
)

# After collecting test cases
results = evaluator.evaluate()
evaluator.print_summary(results)
evaluator.generate_report(results, "evaluation_results.json")
```

## Sample Test Data

The `data.json` file includes 8 sample questions covering:
1. What is machine learning?
2. How does a neural network work?
3. Main types of machine learning
4. Overfitting explanation
5. Accuracy vs Precision
6. What is deep learning?
7. How backpropagation works
8. Transfer learning

These serve as examples for your own test data.

## Troubleshooting

### ImportError: No module named 'ragas'
```bash
pip install ragas datasets langchain-openai
```

### OpenAI API Key Error
```bash
# Verify your API key is set
echo $OPENAI_API_KEY  # Linux/macOS
echo $env:OPENAI_API_KEY  # PowerShell
```

### JSON Decode Error
- Ensure `data.json` is valid JSON
- Check formatting matches the required structure

## Advanced Usage

### Custom Evaluation Metrics

Modify `script.py` to add more metrics or customize evaluation:

```python
from ragas.metrics import faithfulness, answer_relevancy, context_relevancy

# Add more metrics as needed
metrics = [
    faithfulness,
    answer_relevancy,
    context_relevancy,
    # Add custom metrics here
]
```

### Batch Evaluation

Evaluate multiple datasets:

```python
evaluator = RAGASEvaluator()
for dataset_name in ["test1", "test2", "test3"]:
    results = evaluator.evaluate(f"{dataset_name}.json")
    evaluator.generate_report(results, f"{dataset_name}_report.json")
```

## References

- [RAGAS Documentation](https://docs.ragas.io/)
- [RAG Systems](https://python.langchain.com/docs/use_cases/question_answering/)
- [Evaluation Metrics](https://docs.ragas.io/en/latest/concepts/metrics/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review RAGAS documentation
3. Validate your data format
4. Check API key configuration
