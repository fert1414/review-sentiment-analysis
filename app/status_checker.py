from collections import Counter

import torch
from datasets import Dataset as DatasetForTransformers
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    set_seed
)

set_seed = 42

def count_original_status(reviews: list) -> int | int:
    total_negative = 0
    total_positive = 0

    for item in reviews:
        if not item.rating:
            continue

        if item.rating <= 4:
            total_negative += 1
        elif item.rating >= 7:
            total_positive += 1
        else:
            continue

    return total_positive, total_negative

def count_model_status(reviews: list) -> int | int:
    model_path = './best_model'
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)

    review_texts = []
    for item in reviews:
        review_texts.append(item.content)

    inputs = tokenizer(
        review_texts,
        truncation=True,
        padding=True,
        max_length = tokenizer.model_max_length,
        return_tensors='pt'
    )

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    predictions = torch.argmax(logits, dim=1)

    counts = Counter(predictions.tolist())
    total_negative = counts.get(0)
    total_positive = counts.get(1)
    print(counts)
    return total_positive, total_negative