"""
Lightweight training script for seq2seq generators using Hugging Face Transformers Trainer.
Ensure you have a GPU for decent performance.
Usage: python scripts/train_generator.py --train-jsonl data/train.jsonl --model t5-small --output-dir models/generator_ft
"""
import argparse
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)
from datasets import load_dataset


def train(train_jsonl: str, model_name: str, output_dir: str) -> None:
    ds = load_dataset("json", data_files={"train": train_jsonl})
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def preprocess(ex):
        inputs = ex["input_text"]
        outputs = ex["target_text"]
        model_inputs = tokenizer(
            inputs, truncation=True, padding="max_length", max_length=512
        )
        labels = tokenizer(
            outputs, truncation=True, padding="max_length", max_length=256
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized = ds["train"].map(preprocess, batched=False)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=2,
        num_train_epochs=1,
        logging_steps=10,
        save_total_limit=2,
        predict_with_generate=True,
    )
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    trainer = Seq2SeqTrainer(
        model=model,
        args=args,
        train_dataset=tokenized,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    trainer.train()
    trainer.save_model(output_dir)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--train-jsonl", required=True)
    p.add_argument("--model", default="t5-small")
    p.add_argument("--output-dir", default="models/generator_ft")
    args = p.parse_args()
    train(args.train_jsonl, args.model, args.output_dir)

