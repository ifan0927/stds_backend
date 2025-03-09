import os
import json
import time
import argparse
from openai import OpenAI

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate QA dataset in SQuAD format using GPT-4o')
    parser.add_argument('--input_file', type=str, required=True, help='Path to the input text file')
    parser.add_argument('--output_file', type=str, default='qa_dataset.json', help='Path to the output JSON file')
    parser.add_argument('--api_key', type=str, help='OpenAI API key')
    parser.add_argument('--batch_size', type=int, default=5, help='Number of QA pairs to generate per API call')
    parser.add_argument('--total_pairs', type=int, default=125, help='Total number of QA pairs to generate')
    parser.add_argument('--title', type=str, default='Document QA Dataset', help='Title for the dataset')
    return parser.parse_args()

def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def create_context_chunks(text, max_tokens=4000):
    # Split text into smaller chunks to avoid exceeding context length
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for paragraph in paragraphs:
        # Rough estimation of tokens (for Chinese text, characters ≈ tokens)
        para_length = len(paragraph)
        
        if current_length + para_length > max_tokens and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_length = para_length
        else:
            current_chunk.append(paragraph)
            current_length += para_length
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def generate_qa_pairs(client, text, batch_size, context_id=0):
    """Generate QA pairs for a given text chunk"""
    
    prompt = f"""你是一個專業的問答資料集生成助手。請根據以下文本創建{batch_size}個高質量的問答對。

文本內容:
```
{text}
```

要求:
1. 生成{batch_size}個獨特且多樣化的問題，涵蓋文本中的重要信息和細節
2. 問題應該多樣化，包含事實性問題、數字型問題和理解型問題
3. 答案必須是文本中的原文片段，不能自行創作或總結
4. 每個問題都應該有明確的一個答案
5. 將問題設計得像是真實用戶可能會問的問題
6. 確保問題難度多樣化，有簡單直接的，也有需要理解文本的

請按以下格式返回JSON (請保證JSON格式完全正確，可以直接解析):

{{
  "qa_pairs": [
    {{
      "question": "問題1?",
      "answer": {{
        "text": "答案1",
        "answer_start": 123
      }}
    }},
    {{
      "question": "問題2?",
      "answer": {{
        "text": "答案2",
        "answer_start": 456
      }}
    }},
    ...
  ]
}}

請注意，每個答案必須包含在原文中的實際起始字符位置(answer_start)。這是訓練BERT模型所必需的。
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一個專業的問答資料集生成助手，精通創建用於機器學習的SQuAD格式數據集。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    try:
        content = response.choices[0].message.content
        # Try to extract JSON from the response
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = content[json_start:json_end]
            qa_data = json.loads(json_str)
            return qa_data["qa_pairs"]
        else:
            print(f"Failed to extract JSON from response for context {context_id}")
            print(f"Response: {content}")
            return []
    except Exception as e:
        print(f"Error parsing response for context {context_id}: {e}")
        print(f"Response: {response.choices[0].message.content}")
        return []

def create_squad_format(title, context, qa_pairs):
    """Convert QA pairs to SQuAD format for a single context"""
    qas = []
    for i, qa in enumerate(qa_pairs):
        qas.append({
            "id": f"q{i+1}",
            "question": qa["question"],
            "answers": [qa["answer"]]
        })
    
    return {
        "context": context,
        "qas": qas
    }

def generate_dataset(api_key, input_file, output_file, batch_size, total_pairs, dataset_title):
    client = OpenAI(api_key=api_key)
    full_text = read_text_file(input_file)
    
    # Create context chunks
    context_chunks = create_context_chunks(full_text)
    print(f"Split text into {len(context_chunks)} chunks")
    
    # Calculate needed QA pairs per chunk
    pairs_per_chunk = total_pairs // len(context_chunks)
    remaining_pairs = total_pairs % len(context_chunks)
    
    # Prepare SQuAD format
    squad_data = {
        "version": "v2.0",
        "data": [
            {
                "title": dataset_title,
                "paragraphs": []
            }
        ]
    }
    
    total_generated = 0
    total_api_calls = 0
    
    # Generate QA pairs for each chunk
    for i, chunk in enumerate(context_chunks):
        print(f"Processing chunk {i+1}/{len(context_chunks)}")
        
        # Calculate how many pairs to generate for this chunk
        chunk_pairs = pairs_per_chunk + (1 if i < remaining_pairs else 0)
        chunk_batches = (chunk_pairs + batch_size - 1) // batch_size
        
        chunk_qa_pairs = []
        for j in range(chunk_batches):
            curr_batch_size = min(batch_size, chunk_pairs - j * batch_size)
            if curr_batch_size <= 0:
                break
                
            print(f"  Generating batch {j+1}/{chunk_batches} ({curr_batch_size} QA pairs)")
            batch_pairs = generate_qa_pairs(client, chunk, curr_batch_size, i)
            chunk_qa_pairs.extend(batch_pairs)
            
            total_api_calls += 1
            total_generated += len(batch_pairs)
            
            # Add small delay to avoid rate limiting
            time.sleep(1)
            
        # Add to SQuAD format
        if chunk_qa_pairs:
            squad_paragraph = create_squad_format(chunk, chunk_qa_pairs)
            squad_data["data"][0]["paragraphs"].append(squad_paragraph)
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(squad_data, f, ensure_ascii=False, indent=2)
    
    print(f"Dataset generation complete:")
    print(f"- Generated {total_generated} QA pairs")
    print(f"- Made {total_api_calls} API calls")
    print(f"- Saved to {output_file}")
    
    # Calculate approximate cost
    input_tokens = total_api_calls * (4000 + 500)  # Rough estimate: text + instructions
    output_tokens = total_generated * 100  # Rough estimate per QA pair
    input_cost = (input_tokens / 1000000) * 2.50
    output_cost = (output_tokens / 1000000) * 10.00
    total_cost = input_cost + output_cost
    
    print(f"Estimated cost: ${total_cost:.2f}")
    print(f"- Input cost (est. {input_tokens} tokens): ${input_cost:.2f}")
    print(f"- Output cost (est. {output_tokens} tokens): ${output_cost:.2f}")

def main():
    args = parse_arguments()
    
    # Get API key from args or environment variable
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key must be provided via --api_key argument or OPENAI_API_KEY environment variable")
    
    generate_dataset(
        api_key=api_key,
        input_file=args.input_file,
        output_file=args.output_file,
        batch_size=args.batch_size,
        total_pairs=args.total_pairs,
        dataset_title=args.title
    )

if __name__ == "__main__":
    main()