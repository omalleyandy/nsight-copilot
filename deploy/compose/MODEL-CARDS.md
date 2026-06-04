# Model Cards

Copies of the upstream model cards for the models bundled in the
Nsight Copilot offline deployment. Each section is the verbatim README
from the model's Hugging Face page; updates are made by re-fetching
from the upstream URL listed under each model's heading.

Bundled models (alphabetical):

- [BAAI/bge-m3](#baaibge-m3)
- [nvidia/CUDA-Autocomplete](#nvidiacuda-autocomplete)
- [nvidia/llama-nemotron-rerank-1b-v2](#nvidiallama-nemotron-rerank-1b-v2)
- [openai/gpt-oss-120b](#openaigpt-oss-120b)

---

## BAAI/bge-m3

For more details please refer to our github repo: https://github.com/FlagOpen/FlagEmbedding

# BGE-M3 ([paper](https://arxiv.org/pdf/2402.03216.pdf), [code](https://github.com/FlagOpen/FlagEmbedding/tree/master/FlagEmbedding/BGE_M3))

In this project, we introduce BGE-M3, which is distinguished for its versatility in Multi-Functionality, Multi-Linguality, and Multi-Granularity. 
- Multi-Functionality: It can simultaneously perform the three common retrieval functionalities of embedding model: dense retrieval, multi-vector retrieval, and sparse retrieval. 
- Multi-Linguality: It can support more than 100 working languages. 
- Multi-Granularity: It is able to process inputs of different granularities, spanning from short sentences to long documents of up to 8192 tokens. 



**Some suggestions for retrieval pipeline in RAG**

We recommend to use the following pipeline: hybrid retrieval + re-ranking. 
- Hybrid retrieval leverages the strengths of various methods, offering higher accuracy and stronger generalization capabilities. 
A classic example: using both embedding retrieval and the BM25 algorithm. 
Now, you can try to use BGE-M3, which supports both embedding and sparse retrieval. 
This allows you to obtain token weights (similar to the BM25) without any additional cost when generate dense embeddings.
To use hybrid retrieval, you can refer to [Vespa](https://github.com/vespa-engine/pyvespa/blob/master/docs/sphinx/source/examples/mother-of-all-embedding-models-cloud.ipynb
) and [Milvus](https://github.com/milvus-io/pymilvus/blob/master/examples/hello_hybrid_sparse_dense.py).

- As cross-encoder models, re-ranker demonstrates higher accuracy than bi-encoder embedding model. 
Utilizing the re-ranking model (e.g., [bge-reranker](https://github.com/FlagOpen/FlagEmbedding/tree/master/FlagEmbedding/reranker), [bge-reranker-v2](https://github.com/FlagOpen/FlagEmbedding/tree/master/FlagEmbedding/llm_reranker)) after retrieval can further filter the selected text.


## News:
- 2024/7/1: **We update the MIRACL evaluation results of BGE-M3**. To reproduce the new results, you can refer to: [bge-m3_miracl_2cr](https://huggingface.co/datasets/hanhainebula/bge-m3_miracl_2cr). We have also updated our [paper](https://arxiv.org/pdf/2402.03216) on arXiv.
  <details>
  <summary> Details </summary>

  The previous test results were lower because we mistakenly removed the passages that have the same id as the query from the search results. After correcting this mistake, the overall performance of BGE-M3 on MIRACL is higher than the previous results, but the experimental conclusion remains unchanged. The other results are not affected by this mistake. To reproduce the previous lower results, you need to add the `--remove-query` parameter when using `pyserini.search.faiss` or `pyserini.search.lucene` to search the passages.

  </details>
- 2024/3/20: **Thanks Milvus team!** Now you can use hybrid retrieval of bge-m3 in Milvus: [pymilvus/examples
/hello_hybrid_sparse_dense.py](https://github.com/milvus-io/pymilvus/blob/master/examples/hello_hybrid_sparse_dense.py).
- 2024/3/8: **Thanks for the [experimental results](https://towardsdatascience.com/openai-vs-open-source-multilingual-embedding-models-e5ccb7c90f05) from @[Yannael](https://huggingface.co/Yannael). In this benchmark, BGE-M3 achieves top performance in both English and other languages, surpassing models such as OpenAI.**
- 2024/3/2: Release unified fine-tuning [example](https://github.com/FlagOpen/FlagEmbedding/tree/master/examples/unified_finetune) and [data](https://huggingface.co/datasets/Shitao/bge-m3-data) 
- 2024/2/6: We release the [MLDR](https://huggingface.co/datasets/Shitao/MLDR) (a long document retrieval dataset covering 13 languages) and [evaluation pipeline](https://github.com/FlagOpen/FlagEmbedding/tree/master/C_MTEB/MLDR). 
- 2024/2/1: **Thanks for the excellent tool from Vespa.** You can easily use multiple modes of BGE-M3 following this [notebook](https://github.com/vespa-engine/pyvespa/blob/master/docs/sphinx/source/examples/mother-of-all-embedding-models-cloud.ipynb)


## Specs

- Model  

| Model Name |  Dimension | Sequence Length | Introduction |
|:----:|:---:|:---:|:---:|
| [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) | 1024 | 8192 | multilingual; unified fine-tuning (dense, sparse, and colbert) from bge-m3-unsupervised|
| [BAAI/bge-m3-unsupervised](https://huggingface.co/BAAI/bge-m3-unsupervised) | 1024 | 8192 | multilingual; contrastive learning from bge-m3-retromae |
| [BAAI/bge-m3-retromae](https://huggingface.co/BAAI/bge-m3-retromae) | -- | 8192 | multilingual; extend the max_length of [xlm-roberta](https://huggingface.co/FacebookAI/xlm-roberta-large) to 8192 and further pretrained via [retromae](https://github.com/staoxiao/RetroMAE)| 
| [BAAI/bge-large-en-v1.5](https://huggingface.co/BAAI/bge-large-en-v1.5) | 1024 | 512 | English model | 
| [BAAI/bge-base-en-v1.5](https://huggingface.co/BAAI/bge-base-en-v1.5) |  768 | 512 | English model | 
| [BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5) |  384 | 512 | English model | 

- Data

|                          Dataset                           |                   Introduction                    |
|:----------------------------------------------------------:|:-------------------------------------------------:|
|    [MLDR](https://huggingface.co/datasets/Shitao/MLDR)     | Docuemtn Retrieval Dataset, covering 13 languages |
| [bge-m3-data](https://huggingface.co/datasets/Shitao/bge-m3-data) |          Fine-tuning data used by bge-m3          |



## FAQ

**1. Introduction for different retrieval methods**

- Dense retrieval: map the text into a single embedding, e.g., [DPR](https://arxiv.org/abs/2004.04906), [BGE-v1.5](https://github.com/FlagOpen/FlagEmbedding)
- Sparse retrieval (lexical matching): a vector of size equal to the vocabulary, with the majority of positions set to zero, calculating a weight only for tokens present in the text. e.g., BM25, [unicoil](https://arxiv.org/pdf/2106.14807.pdf), and [splade](https://arxiv.org/abs/2107.05720)
- Multi-vector retrieval: use multiple vectors to represent a text, e.g., [ColBERT](https://arxiv.org/abs/2004.12832).


**2. How to use BGE-M3 in other projects?**

For embedding retrieval, you can employ the BGE-M3 model using the same approach as BGE. 
The only difference is that the BGE-M3 model no longer requires adding instructions to the queries. 

For hybrid retrieval, you can use [Vespa](https://github.com/vespa-engine/pyvespa/blob/master/docs/sphinx/source/examples/mother-of-all-embedding-models-cloud.ipynb
) and [Milvus](https://github.com/milvus-io/pymilvus/blob/master/examples/hello_hybrid_sparse_dense.py).


**3. How to fine-tune bge-M3 model?**

You can follow the common in this [example](https://github.com/FlagOpen/FlagEmbedding/tree/master/examples/finetune) 
to fine-tune the dense embedding.

If you want to fine-tune all embedding function of m3 (dense, sparse and colbert), you can refer to the [unified_fine-tuning example](https://github.com/FlagOpen/FlagEmbedding/tree/master/examples/unified_finetune)






## Usage

Install: 
```
git clone https://github.com/FlagOpen/FlagEmbedding.git
cd FlagEmbedding
pip install -e .
```
or: 
```
pip install -U FlagEmbedding
```



### Generate Embedding for text

- Dense Embedding
```python
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('BAAI/bge-m3',  
                       use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation

sentences_1 = ["What is BGE M3?", "Defination of BM25"]
sentences_2 = ["BGE M3 is an embedding model supporting dense retrieval, lexical matching and multi-vector interaction.", 
               "BM25 is a bag-of-words retrieval function that ranks a set of documents based on the query terms appearing in each document"]

embeddings_1 = model.encode(sentences_1, 
                            batch_size=12, 
                            max_length=8192, # If you don't need such a long length, you can set a smaller value to speed up the encoding process.
                            )['dense_vecs']
embeddings_2 = model.encode(sentences_2)['dense_vecs']
similarity = embeddings_1 @ embeddings_2.T
print(similarity)
# [[0.6265, 0.3477], [0.3499, 0.678 ]]
```
You also can use sentence-transformers and huggingface transformers to generate dense embeddings.
Refer to [baai_general_embedding](https://github.com/FlagOpen/FlagEmbedding/tree/master/FlagEmbedding/baai_general_embedding#usage) for details.


- Sparse Embedding (Lexical Weight)
```python
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('BAAI/bge-m3',  use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation

sentences_1 = ["What is BGE M3?", "Defination of BM25"]
sentences_2 = ["BGE M3 is an embedding model supporting dense retrieval, lexical matching and multi-vector interaction.", 
               "BM25 is a bag-of-words retrieval function that ranks a set of documents based on the query terms appearing in each document"]

output_1 = model.encode(sentences_1, return_dense=True, return_sparse=True, return_colbert_vecs=False)
output_2 = model.encode(sentences_2, return_dense=True, return_sparse=True, return_colbert_vecs=False)

# you can see the weight for each token:
print(model.convert_id_to_token(output_1['lexical_weights']))
# [{'What': 0.08356, 'is': 0.0814, 'B': 0.1296, 'GE': 0.252, 'M': 0.1702, '3': 0.2695, '?': 0.04092}, 
#  {'De': 0.05005, 'fin': 0.1368, 'ation': 0.04498, 'of': 0.0633, 'BM': 0.2515, '25': 0.3335}]


# compute the scores via lexical mathcing
lexical_scores = model.compute_lexical_matching_score(output_1['lexical_weights'][0], output_2['lexical_weights'][0])
print(lexical_scores)
# 0.19554901123046875

print(model.compute_lexical_matching_score(output_1['lexical_weights'][0], output_1['lexical_weights'][1]))
# 0.0
```

- Multi-Vector (ColBERT)
```python
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('BAAI/bge-m3',  use_fp16=True) 

sentences_1 = ["What is BGE M3?", "Defination of BM25"]
sentences_2 = ["BGE M3 is an embedding model supporting dense retrieval, lexical matching and multi-vector interaction.", 
               "BM25 is a bag-of-words retrieval function that ranks a set of documents based on the query terms appearing in each document"]

output_1 = model.encode(sentences_1, return_dense=True, return_sparse=True, return_colbert_vecs=True)
output_2 = model.encode(sentences_2, return_dense=True, return_sparse=True, return_colbert_vecs=True)

print(model.colbert_score(output_1['colbert_vecs'][0], output_2['colbert_vecs'][0]))
print(model.colbert_score(output_1['colbert_vecs'][0], output_2['colbert_vecs'][1]))
# 0.7797
# 0.4620
```


### Compute score for text pairs
Input a list of text pairs, you can get the scores computed by different methods.
```python
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('BAAI/bge-m3',  use_fp16=True) 

sentences_1 = ["What is BGE M3?", "Defination of BM25"]
sentences_2 = ["BGE M3 is an embedding model supporting dense retrieval, lexical matching and multi-vector interaction.", 
               "BM25 is a bag-of-words retrieval function that ranks a set of documents based on the query terms appearing in each document"]

sentence_pairs = [[i,j] for i in sentences_1 for j in sentences_2]

print(model.compute_score(sentence_pairs, 
                          max_passage_length=128, # a smaller max length leads to a lower latency
                          weights_for_different_modes=[0.4, 0.2, 0.4])) # weights_for_different_modes(w) is used to do weighted sum: w[0]*dense_score + w[1]*sparse_score + w[2]*colbert_score

# {
#   'colbert': [0.7796499729156494, 0.4621465802192688, 0.4523794651031494, 0.7898575067520142], 
#   'sparse': [0.195556640625, 0.00879669189453125, 0.0, 0.1802978515625], 
#   'dense': [0.6259765625, 0.347412109375, 0.349853515625, 0.67822265625], 
#   'sparse+dense': [0.482503205537796, 0.23454029858112335, 0.2332356721162796, 0.5122477412223816], 
#   'colbert+sparse+dense': [0.6013619303703308, 0.3255828022956848, 0.32089319825172424, 0.6232916116714478]
# }
```




## Evaluation  

We provide the evaluation script for [MKQA](https://github.com/FlagOpen/FlagEmbedding/tree/master/C_MTEB/MKQA) and [MLDR](https://github.com/FlagOpen/FlagEmbedding/tree/master/C_MTEB/MLDR)

### Benchmarks from the open-source community
  ![avatar](./imgs/others.webp)
 The BGE-M3 model emerged as the top performer on this benchmark (OAI is short for OpenAI). 
  For more details, please refer to the [article](https://towardsdatascience.com/openai-vs-open-source-multilingual-embedding-models-e5ccb7c90f05) and [Github Repo](https://github.com/Yannael/multilingual-embeddings)


### Our results
- Multilingual (Miracl dataset) 

![avatar](./imgs/miracl.jpg)

- Cross-lingual (MKQA dataset)

![avatar](./imgs/mkqa.jpg)

- Long Document Retrieval
  - MLDR:   
  ![avatar](./imgs/long.jpg)
  Please note that [MLDR](https://huggingface.co/datasets/Shitao/MLDR) is a document retrieval dataset we constructed via LLM, 
  covering 13 languages, including test set, validation set, and training set. 
  We utilized the training set from MLDR to enhance the model's long document retrieval capabilities. 
  Therefore, comparing baselines with `Dense w.o.long`(fine-tuning without long document dataset) is more equitable. 
  Additionally, this long document retrieval dataset will be open-sourced to address the current lack of open-source multilingual long text retrieval datasets.
  We believe that this data will be helpful for the open-source community in training document retrieval models.

  - NarritiveQA:  
  ![avatar](./imgs/nqa.jpg)

- Comparison with BM25  

We utilized Pyserini to implement BM25, and the test results can be reproduced by this [script](https://github.com/FlagOpen/FlagEmbedding/tree/master/C_MTEB/MLDR#bm25-baseline).
We tested BM25 using two different tokenizers: 
one using Lucene Analyzer and the other using the same tokenizer as M3 (i.e., the tokenizer of xlm-roberta). 
The results indicate that BM25 remains a competitive baseline, 
especially in long document retrieval.

![avatar](./imgs/bm25.jpg)



## Training
- Self-knowledge Distillation: combining multiple outputs from different 
retrieval modes as reward signal to enhance the performance of single mode(especially for sparse retrieval and multi-vec(colbert) retrival)
- Efficient Batching: Improve the efficiency when fine-tuning on long text. 
The small-batch strategy is simple but effective, which also can used to fine-tune large embedding model.
- MCLS: A simple method to improve the performance on long text without fine-tuning. 
If you have no enough resource to fine-tuning model with long text, the method is useful.

Refer to our [report](https://arxiv.org/pdf/2402.03216.pdf) for more details. 






## Acknowledgement

Thanks to the authors of open-sourced datasets, including Miracl, MKQA, NarritiveQA, etc. 
Thanks to the open-sourced libraries like [Tevatron](https://github.com/texttron/tevatron), [Pyserini](https://github.com/castorini/pyserini).



## Citation

If you find this repository useful, please consider giving a star :star: and citation

```
@misc{bge-m3,
      title={BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation}, 
      author={Jianlv Chen and Shitao Xiao and Peitian Zhang and Kun Luo and Defu Lian and Zheng Liu},
      year={2024},
      eprint={2402.03216},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

---

## nvidia/CUDA-Autocomplete

# nvidia/CUDA-Autocomplete Overview

## Description:
NVIDIA CUDA Autocomplete is a fine-tuned version of Qwen/Qwen2.5-Coder-7B enhanced for CUDA code completion. The model takes as input two strings of code context: the prefix (code before the cursor) and the suffix (code after the cursor), and outputs a single line of code that logically continues the prefix. By analyzing the surrounding code structure, variable names, and CUDA-specific patterns, the model predicts the most likely next line of code, enabling intelligent autocomplete functionality for general programming and CUDA development in the Nsight Copilot extension for VSCode and Cursor.

_This model is ready for commercial/non-commercial use._  


### License/Terms of Use:   
[NVIDIA Open Model License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/)

### Deployment Geography:  
Global

### Use Case:  
This model is intended to be used for code completion in the Nsight Copilot extension for VSCode / Cursor. 
  

### Release Date:
Huggingface : 03/16/2026

## Reference(s):
[Qwen2.5-Coder paper](https://arxiv.org/abs/2409.12186)
[Qwen2.5-Coder blog](https://qwenlm.github.io/blog/qwen2.5-coder-family/)  
[Qwen2.5-Coder GitHub repository](https://github.com/QwenLM/Qwen2.5-Coder)  

## Model Architecture:   
**Architecture Type:** Transformer   
**Network Architecture:** Qwen2ForCausalLM  
**This model was developed based on Qwen/Qwen2.5-Coder-7B.**  
**Number of model parameters:** 7B (7*10^9)  


## Computational Load (Internal Only: For NVIDIA Models Only)
**Cumulative Compute:** 1.23 * 10^20 FLOPS
**Estimated Energy and Emissions for Model Training:** 150.52 kWh
 
## Input:
**Input Type(s):** Code
**Input Format(s):** String of code (meant for prefix code and suffix code)
**Input Parameters:** One-Dimensional (1D)
**Other Properties Related to Input:**
- **Context Window:** The model processes sequential code text with prefix and suffix context
- **Encoding:** UTF-8 text encoding
- **Input Structure:** Fill-in-the-middle (FIM) format with prefix and suffix tokens  
  

## Output:
**Output Type(s):** Code
**Output Format:** String
**Output Parameters:** One-Dimensional (1D)
**Other Properties Related to Output:**
- **Output Length:** Single line of code completion
- **Generation Method:** Autoregressive token-by-token generation
- **Encoding:** UTF-8 text encoding
- **Output Structure:** Sequential code text that continues from the input prefix  
   

Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA's hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions.

## Software Integration:  
**Runtime Engine(s):** vLLM  
**Supported Hardware Microarchitecture Compatibility:**  
* H100  
* DGX Spark  
**[Supported] Operating System(s):** Linux  

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels are essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment.  


## Model Version(s): 
v0.3  
 
## Training, Testing, and Evaluation Datasets:  


## Training Dataset:

**Link:** Subset of 
1) https://huggingface.co/datasets/bigcode/the-stack-v2
2) Synthetically generated CUDA data using OSS models like GPT-OSS 120B  
**Data Modality:** Text  
**Text Training Data Size:** ~700000 samples  
**Data Collection Method by dataset:** Hybrid: Automated, Synthetic
**Labeling Method by dataset:** Not Applicable
**Properties (Quantity, Dataset Descriptions, Sensor(s)):** ~700,000 samples. Text modality (source code). Content includes open-source CUDA and general programming code collected from permissive-licensed repositories, as well as machine-generated synthetic CUDA code produced by OSS models. Primarily English-language code with CUDA-specific constructs and APIs. No sensor data involved.

### Testing Dataset:
**Link:** NVIDIA Internal Data
**Benchmark Score:** ROUGE-L score on cuda-samples dataset is 77.45 %.
**Data Collection Method by dataset:** Automated
**Labeling Method by dataset:** Not Applicable
**Properties (Quantity, Dataset Descriptions, Sensor(s)):** 2,156 samples. Text modality (source code). Content consists of internal proprietary CUDA and HPC library code (e.g., cuDNN, cuda-hpc) parsed from internal GitLab repositories. Code is CUDA-specific with domain-specific APIs and patterns. No sensor data involved.

### Evaluation Dataset:
**Link:** Subset of https://huggingface.co/datasets/bigcode/the-stack-v2
**Data Collection Method by dataset:** Automated
**Labeling Method by dataset:** Not Applicable
**Properties (Quantity, Dataset Descriptions, Sensor(s)):** ~33,000 samples. Each sample corresponds to a single source code file. Text modality (source code). Content includes open-source code collected from permissive-licensed repositories. CUDA and general programming code in English. No sensor data involved.


## Inference: 
**Acceleration Engine:** vLLM
**Test Hardware:**  
* H100  
* DGX Spark  

## Ethical Considerations:
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications.  When downloaded or used in accordance with our terms of service, developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.  
For more detailed information on ethical considerations for this model, please see the Model Card++ Explainability, Bias, Safety & Security, and Privacy Subcards.  
Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://app.intigriti.com/programs/nvidia/nvidiavdp/detail).

---

# Bias Subcard
## Participation considerations from adversely impacted groups protected classes in model design and testing:
Not Applicable

## Measures taken to mitigate against unwanted bias:
Not Applicable

---

# Explainability Subcard
## intended_domain
Code generation in VSCode / Cursor.

## Model Type
Transformer

## Intended Users
This model is designed for software developers, CUDA programmers, and AI enthusiasts who want to accelerate their coding workflow with intelligent code completion. Primary users include:
- **CUDA Developers**: Engineers building GPU-accelerated applications, high-performance computing (HPC) solutions, or scientific computing applications who need assistance with CUDA-specific syntax and patterns.
- **Software Engineers**: General programmers working in languages like Python, C++, and Java who want AI-powered code suggestions to boost productivity.
- **Students and Learners**: Individuals learning CUDA programming or general software development who benefit from contextual code completion as a learning aid.
- **AI/ML Engineers**: Developers building AI applications who need efficient coding assistance within the VSCode/Cursor development environment.

## Output
Types: A single line of code. Formats: Python, C++, Java, etc.

## Describe how the model works:
The model accepts a block of code around the cursor (as left and right context) and predicts the sequence of code that is the best continuation of the code.


## Name the adversely impacted groups this has been tested to deliver comparable outcomes regardless of:
Not Applicable

## Technical Limitations:
The model is currently trained with a large distribution of C++, Python, and CUDA code. As the representation of other languages is limited, we recommend fine-tuning the model on more diverse languages and domains.

## Verified to have met prescribed NVIDIA quality standards:
Yes

## Performance Metrics:
Acceptance rate of the code completion. Offline metrics include LLM-as-a-judge metrics and ROUGE-L score.

## Potential Known Risks:
This model may occasionally generate incorrect responses or produce repetitive code. To mitigate this, mechanisms are in place to reduce repetition, and model parameters such as temperature and max_tokens have been carefully configured to minimize these risks.

## Licensing:
NVIDIA Open Model License.

---

# Privacy Subcard
## Generatable or reverse engineerable personal data?
No

## Personal data used to create this model?
No

## How often is dataset reviewed?
Dataset is initially reviewed upon addition, and subsequent reviews are conducted as needed or upon request for changes.

## Was data from user interactions with the AI model (e.g. user input and prompts) used to train the model?
No

## Is there provenance for all datasets used in training?
Yes

## Does data labeling (annotation, metadata) comply with privacy laws?
Yes

## Applicable Privacy Policy
https://www.nvidia.com/en-us/about-nvidia/privacy-policy/

---

# Safety & Security Subcard
## Model Application Field(s):
Code generation in VSCode / Cursor.

## Describe the life critical impact (if present).
Not Applicable

## Use Case Restrictions:
Abide by [NVIDIA Open Model License](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/)

## Model and dataset restrictions:
The Principle of least privilege (PoLP) is applied limiting access for dataset generation and model development. Restrictions enforce dataset access during training, and dataset license constraints adhered to.

---

## nvidia/llama-nemotron-rerank-1b-v2

## **Model Overview**

### **Description**

The Llama Nemotron Reranking 1B model is optimized for providing a logit score that represents how relevant a document(s) is to a given query. The model was fine-tuned for **multilingual, cross-lingual** text question-answering retrieval, with support for **long documents (up to 8192 tokens)**.  This model was evaluated on 26 languages: English, Arabic, Bengali, Chinese, Czech, Danish, Dutch, Finnish, French, German, Hebrew, Hindi, Hungarian, Indonesian, Italian, Japanese, Korean, Norwegian, Persian, Polish, Portuguese, Russian, Spanish, Swedish, Thai, and Turkish.


This model is a component in a text retrieval system to improve the overall accuracy. A text retrieval system often uses an embedding model (dense) or lexical search (sparse) index to return relevant text passages given the input. A reranking model can be used to rerank the potential candidate into a final order. The reranking model has the question-passage pairs as an input and therefore, can process cross attention between the words. It’s not feasible to apply a Ranking model on all documents in the knowledge base, therefore, ranking models are often deployed in combination with embedding models.


This model is ready for commercial use.


The Llama Nemotron Reranking 1B model is a part of the NeMo Retriever collection of NIM, which provide state-of-the-art, commercially-ready models and microservices, optimized for the lowest latency and highest throughput. It features a production-ready information retrieval pipeline with enterprise support. The models that form the core of this solution have been trained using responsibly selected, auditable data sources. With multiple pre-trained models available as starting points, developers can also readily customize them for their domain-specific use cases, such as information technology, human resource help assistants, and research & development research assistants.

We are excited to announce the open sourcing of this commercial embedding model. For users interested in deploying this model in production environments, it is also available via the model API in NVIDIA Inference Microservices (NIM) at [llama-nemotron-rerank-1b-v2](https://build.nvidia.com/nvidia/llama-3_2-nv-rerankqa-1b-v2).

### **License/Terms of use**

Use of this model is governed by the [NVIDIA Open Model License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/). Additional Information: [Llama 3.2 Community Model License Agreement](https://www.llama.com/llama3_2/license/).

### **Intended use**

The Llama Nemotron Reranking 1B model is most suitable for users who want to improve their multilingual retrieval tasks by reranking a set of candidates for a given question.

### **Model Architecture**

**Architecture Type:** Transformer <br>
**Network Architecture:** Fine-tuned ranker model from the `meta-llama/Llama-3.2-1B` model.

The Llama Nemotron Reranking 1B model is a transformer cross-encoder fine-tuned with contrastive learning. We employ bi-directional attention when fine-tuning for higher accuracy. The last embedding output by the decoder model is used with a mean pooling strategy, and a binary classification head is fine-tuned for the ranking task.

Ranking models for text ranking are typically trained as a cross-encoder for sentence classification. This involves predicting the relevancy of a sentence pair (for example, question and chunked passages). The CrossEntropy loss is used to maximize the likelihood of passages containing information to answer the question and minimize the likelihood for (negative) passages that do not contain information to answer the question.

We trained the model on public datasets described in the Dataset and Training section.

### **Input**

**Input Type:** Pair of Texts <br>
**Input Format:** List of text pairs <br>
**Input Parameters:** 1D <br>
**Other Properties Related to Input:** The model was trained on question and answering over text documents from multiple languages. It was evaluated to work successfully with up to a sequence length of 8192 tokens. Longer texts are recommended to be either chunked or truncated.

### **Output**

**Output Type:** Floats <br>
**Output Format:** List of floats <br>
**Output Parameters:** 1D <br>
**Other Properties Related to Output:** Each value corresponds to a raw logit. Users can choose to apply a Sigmoid activation function to the logits to convert them into probabilities during model usage.

### **Installation**

The model requires transformers version 4.44 or above.

```bash
pip install transformers>=4.44
```

### **Usage**
```python
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name_or_path = "nvidia/llama-nemotron-rerank-1b-v2"

device = "cuda:0"
max_length = 512

queries = [
    "how much protein should a female eat?",
]
documents = [
    "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 is 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or training for a marathon. Check out the chart below to see how much protein you should be eating each day.",
    "Definition of summit for English Language Learners. : 1  the highest point of a mountain : the top of a mountain. : 2  the highest level. : 3  a meeting or series of meetings between the leaders of two or more governments.",
    "Calorie intake should not fall below 1,200 a day in women or 1,500 a day in men, except under the supervision of a health professional."
]

# Create pairs from queries and documents
pairs = [[q, d] for q in queries for d in documents]

def prompt_template(q, p):
    """Format query and passage with a prompt template."""
    return f"question:{q} \n \n passage:{p}"


tokenizer = AutoTokenizer.from_pretrained(
    model_name_or_path,
    trust_remote_code=True,
    padding_side="left"
)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model_kwargs = {
    "trust_remote_code": True,
    "torch_dtype": torch.bfloat16,
}

print(f"Loading model from {model_name_or_path}...")
model = AutoModelForSequenceClassification.from_pretrained(
    model_name_or_path,
    **model_kwargs
).eval()

if model.config.pad_token_id is None:
    model.config.pad_token_id = tokenizer.eos_token_id

model = model.to(device)


# Apply prompt template and tokenize as single sequence
texts = [prompt_template(query, doc) for query, doc in pairs]
batch_dict = tokenizer(
    texts,
    padding=True,
    truncation=True,
    return_tensors="pt",
    max_length=max_length,
)

# Move to device
batch_dict = {k: v.to(device) for k, v in batch_dict.items()}

with torch.inference_mode():
    logits = model(**batch_dict).logits
    scores = logits.view(-1).cpu().tolist()

for i, (pair, score) in enumerate(zip(pairs, scores)):
    query, doc = pair
    print(f"  Query: {query}")
    print(f"  Document: {doc[:100]}{'...' if len(doc) > 100 else ''}")
    print(f"  Score: {score:.4f}")

#   Query: how much protein should a female eat?
#   Document: As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 is 46 grams...
#   Score: 20.6250
#   Query: how much protein should a female eat?
#   Document: Definition of summit for English Language Learners. : 1  the highest point of a mountain : the top o...
#   Score: -23.1250
#   Query: how much protein should a female eat?
#   Document: Calorie intake should not fall below 1,200 a day in women or 1,500 a day in men, except under the su...
#   Score: -0.2617
```

#### vLLM Usage

1. Ensure you are using `vllm>=0.14.0`.
2. A score template **must** be provided via `--chat-template` to correctly format
   query-document pairs. Without it, the `question:... passage:...` prompt format
   is not applied and results will be incorrect.

Create the score template file and start the server:
```bash
python3 -c "
t = (
    'question:{{ (messages | selectattr(\"role\", \"eq\", \"query\") | first).content }}'
    ' \n \n '
    'passage:{{ (messages | selectattr(\"role\", \"eq\", \"document\") | first).content }}'
)
open('nemotron-rerank.jinja', 'w').write(t)
"

vllm serve nvidia/llama-nemotron-rerank-1b-v2 \
    --trust-remote-code \
    --chat-template nemotron-rerank.jinja
```

If you already have a local copy of the model, you can also pass the local
path instead of the HF repo ID.

Optional flags:

- `--dtype <float32|bfloat16|float16>` to force precision (the default is `auto`, which resolves from model config; this model defaults to BF16).
- `--data-parallel-size <num_gpus_to_use>` for multi-GPU serving.
- `--port 8000` to set the server port.

Online serving example (`/rerank` API):

```python
import requests

query = "What is machine learning?"
documents = [
    "Machine learning is a branch of AI that learns patterns from data.",
    "Python is a programming language commonly used for data science.",
    "Neural networks are one family of machine learning models.",
    "Bananas are a good source of potassium.",
]

response = requests.post(
    "http://localhost:8000/rerank",
    json={
        "model": "nvidia/llama-nemotron-rerank-1b-v2",
        "query": query,
        "documents": documents,
        "top_n": 3,
    },
    timeout=30,
)
response.raise_for_status()
for item in response.json()["results"]:
    print(item["index"], item["relevance_score"])
```

Offline inference example (Python API, no server required):

```python
from vllm import LLM

SCORE_TEMPLATE = (
    "question:{{ (messages | selectattr(\"role\", \"eq\", \"query\") | first).content }}"
    " \n \n "
    "passage:{{ (messages | selectattr(\"role\", \"eq\", \"document\") | first).content }}"
)

llm = LLM(
    model="nvidia/llama-nemotron-rerank-1b-v2",
    runner="pooling",
    trust_remote_code=True,
)

query = "What is machine learning?"
documents = [
    "Machine learning is a branch of AI that learns patterns from data.",
    "Python is a programming language commonly used for data science.",
    "Neural networks are one family of machine learning models.",
    "Bananas are a good source of potassium.",
]

outputs = llm.score(query, documents, chat_template=SCORE_TEMPLATE)
for document, output in zip(documents, outputs):
    print(document[:80], output.outputs.score)
```

### **Software Integration**

**Runtime:** Llama Nemotron Reranking 1B NIM <br>
**Supported Hardware Microarchitecture Compatibility**: NVIDIA Ampere, NVIDIA Hopper, NVIDIA Lovelace <br>
**Supported Operating System(s):** Linux

### **Model Version(s)**

Llama Nemotron Reranking 1B <br>
Short Name: llama-nemotron-rerank-1b-v2

## **Training Dataset & Evaluation**

### **Training Dataset**

The development of large-scale public open-QA datasets has enabled tremendous progress in powerful embedding models. However, one popular dataset named [MSMARCO](https://microsoft.github.io/msmarco/) restricts ‌commercial licensing, limiting the use of these models in commercial settings. To address this, NVIDIA created its own training dataset blend based on public QA datasets, which each have a license for commercial applications.

**Data Collection Method by dataset**: Automated, Unknown <br>

**Labeling Method by dataset:** Automated, Unknown <br>

**Properties:** This model was trained on 800k samples from public datasets.

### **Evaluation Results**

We evaluate the pipelines on a set of evaluation benchmarks. We applied the ranking model to the candidates retrieved from a retrieval embedding model.

Overall, the pipeline llama-nemotron-embed-1b-v2 + llama-nemotron-rerank-1b-v2 provides high BEIR+TechQA accuracy with multilingual and crosslingual support. The llama-nemotron-embed-1b-v2 ranking model is 3.5x smaller than the nv-rerankqa-mistral-4b-v3 model.

We evaluated the NVIDIA Retrieval QA Embedding Model in comparison to literature open & commercial retriever models on academic benchmarks for question-answering \- [NQ](https://huggingface.co/datasets/BeIR/nq), [HotpotQA](https://huggingface.co/datasets/hotpot_qa) and [FiQA (Finance Q\&A)](https://huggingface.co/datasets/BeIR/fiqa) from BeIR benchmark and TechQA dataset. In this benchmark, the metric used was Recall@5. As described, we need to apply the ranking model on the output of an embedding model.

| Open & Commercial Reranker Models | Average Recall@5 on NQ, HotpotQA, FiQA, TechQA dataset |
| ----- | ----- |
| llama-nemotron-embed-1b-v2 + llama-nemotron-rerank-1b-v2 | 73.64% |
| llama-nemotron-embed-1b-v2 | 68.60% |
| nv-embedqa-e5-v5 \+ nv-rerankQA-mistral-4b-v3 | 75.45% |
| nv-embedqa-e5-v5 | 62.07% |
| nv-embedqa-e5-v4 | 57.65% |
| e5-large\_unsupervised | 48.03% |
| BM25 | 44.67% |

We evaluated the model’s multilingual capabilities on the [MIRACL](https://github.com/project-miracl/miracl) academic benchmark \- a multilingual retrieval dataset, across 15 languages, and on an additional 11 languages that were translated from the English and Spanish versions of MIRACL. The reported scores are based on a custom subsampled version by selecting hard negatives for each query to reduce the corpus size.

| Open & Commercial Retrieval Models | Average Recall@5 on MIRACL multilingual datasets |
| :---- | :---- |
| llama-nemotron-embed-1b-v2 + llama-nemotron-rerank-1b-v2 | 65.80% |
| llama-nemotron-embed-1b-v2 | 60.75% |
| nv-embedqa-mistral-7b-v2 | 50.42% |
| BM25 | 26.51% |

We evaluated the cross-lingual capabilities on the academic benchmark [MLQA](https://github.com/facebookresearch/MLQA/) based on 7 languages (Arabic, Chinese, English, German, Hindi, Spanish, Vietnamese). We consider only evaluation datasets when the query and documents are in different languages. We calculate the average Recall@5 across the 42 different language pairs.

| Open & Commercial Retrieval Models | Average Recall@5 on MLQA dataset with different languages |
| :---- | :---- |
| llama-nemotron-embed-1b-v2 + llama-nemotron-rerank-1b-v2 | 86.83% |
| llama-nemotron-embed-1b-v2 | 79.86% |
| nv-embedqa-mistral-7b-v2 | 68.38% |
| BM25 | 13.01% |

We evaluated the support of long documents on the academic benchmark [Multilingual Long-Document Retrieval (MLDR)](https://huggingface.co/datasets/Shitao/MLDR) built on Wikipedia and mC4, covering 12 typologically diverse languages . The English version has a median length of 2399 tokens and 90th percentile of 7483 tokens using the llama 3.2 tokenizer.

| Open & Commercial Retrieval Models | Average Recall@5 on MLDR |
| :---- | :---- |
| llama-nemotron-embed-1b-v2 + llama-nemotron-rerank-1b-v2 | 70.69% |
| llama-nemotron-embed-1b-v2 | 59.55% |
| nv-embedqa-mistral-7b-v2 | 43.24% |
| BM25 | 71.39% |

**Data Collection Method by dataset**:
Unknown

**Labeling Method by dataset:**
Unknown

**Properties**
The evaluation datasets are based on three [MTEB/BEIR](https://github.com/beir-cellar/beir) TextQA datasets, the TechQA dataset, MIRACL, MLDR and MLQA multilingual retrieval datasets, which are all public datasets. The sizes range between 10,000s up to 5M depending on the dataset.

**Inference**
**Engine:** TensorRT <br>
**Test Hardware:**  H100 PCIe/SXM, A100 PCIe/SXM, L40s, L4, and A10G

## **Ethical Considerations**

NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications. When downloaded or used in accordance with our terms of service, developers should work with their supporting model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.

For more detailed information on ethical considerations for this model, please see the Explainability, Bias, Safety, and Privacy sections.

Please report security vulnerabilities or NVIDIA AI Concerns [here](https://www.nvidia.com/en-us/support/submit-security-vulnerability/).

## Get Help

### Enterprise Support
Get access to knowledge base articles and support cases or  submit a ticket at the [NVIDIA AI Enterprise Support Services page.](https://www.nvidia.com/en-us/data-center/products/ai-enterprise-suite/support/).

### NVIDIA NIM Documentation
Visit the [NeMo Retriever docs page](https://docs.nvidia.com/nemo/retriever/index.html) for release documentation, deployment guides and more.

## Bias

| Field | Response |
| ----- | ----- |
| Participation considerations from adversely impacted groups [protected classes](https://www.senate.ca.gov/content/protected-classes) in model design and testing | None |
| Measures taken to mitigate against unwanted bias | None |


## Explainability

| Field | Response |
| ----- | ----- |
| Intended Application & Domain: | Passage ranking for question and answer retrieval |
| Model Type: | Transformer encoder |
| Intended User: | Generative AI creators working with conversational AI models - users who want to build a multilingual question and answer application over a large text corpus, leveraging the latest dense retrieval technologies. |
| Output: | Array of float numbers (Dense Vector Representation for the input text) |
| Describe how the model works: | Model transforms the tokenized input text into a dense vector representation. |
| Performance Metrics: | Accuracy, Throughput, and Latency |
| Potential Known Risks: | This model does not always guarantee to retrieve the correct passage(s) for a given query. |
| Licensing & Terms of Use: | Use of this model is governed by the [NVIDIA Open Model License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/). Additional Information: [Llama 3.2 Community Model License Agreement](https://www.llama.com/llama3_2/license/). |
| Technical Limitations | The model’s max sequence length is 8192. Therefore, the longer text inputs should be truncated.   |
| Name the adversely impacted groups this has been tested to deliver comparable outcomes regardless of: | N/A |
| Verified to have met prescribed NVIDIA quality standards: | Yes |

## Privacy

| Field | Response |
| ----- | ----- |
| Generatable or reverse engineerable personally-identifiable information (PII)? | None |
| Was consent obtained for any personal data used? | Not Applicable |
| PII used to create this model? | None |
| How often is the dataset reviewed? | Before Every Release |
| Is a mechanism in place to honor data subject right of access or deletion of personal data? | No |
| If personal data was collected for the development of the model, was it collected directly by NVIDIA? | Not Applicable |
| If personal data was  collected for the development of the model by NVIDIA, do you maintain or have access to disclosures made to data subjects? | Not Applicable |
| If personal data was collected for the development of this AI model, was it minimized to only what was required? | Not Applicable |
| Is there provenance for all datasets used in training? | Yes |
| Does data labeling (annotation, metadata) comply with privacy laws? | Yes |
| Is data compliant with data subject requests for data correction or removal, if such a request was made? | No, not possible with externally-sourced data. |


## Safety

| Field | Response |
| ----- | ----- |
| Model Application(s): | Text Reranking for Retrieval |
| Describe the physical safety impact (if present). | Not Applicable |
| Use Case Restrictions: | Use of this model is governed by the [NVIDIA Open Model License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/). Additional Information: [Llama 3.2 Community Model License Agreement](https://www.llama.com/llama3_2/license/).  |
| Model and dataset restrictions: | The Principle of least privilege (PoLP) is applied limiting access for dataset generation and model development. Restrictions enforce dataset access during training, and dataset license constraints adhered to. |

---

## openai/gpt-oss-120b

<p align="center">
  <img alt="gpt-oss-120b" src="https://raw.githubusercontent.com/openai/gpt-oss/main/docs/gpt-oss-120b.svg">
</p>

<p align="center">
  <a href="https://gpt-oss.com"><strong>Try gpt-oss</strong></a> ·
  <a href="https://cookbook.openai.com/topic/gpt-oss"><strong>Guides</strong></a> ·
  <a href="https://arxiv.org/abs/2508.10925"><strong>Model card</strong></a> ·
  <a href="https://openai.com/index/introducing-gpt-oss/"><strong>OpenAI blog</strong></a>
</p>

<br>

Welcome to the gpt-oss series, [OpenAI’s open-weight models](https://openai.com/open-models) designed for powerful reasoning, agentic tasks, and versatile developer use cases.

We’re releasing two flavors of these open models:
- `gpt-oss-120b` — for production, general purpose, high reasoning use cases that fit into a single 80GB GPU (like NVIDIA H100 or AMD MI300X) (117B parameters with 5.1B active parameters)
- `gpt-oss-20b` — for lower latency, and local or specialized use cases (21B parameters with 3.6B active parameters)

Both models were trained on our [harmony response format](https://github.com/openai/harmony) and should only be used with the harmony format as it will not work correctly otherwise.


> [!NOTE]
> This model card is dedicated to the larger `gpt-oss-120b` model. Check out [`gpt-oss-20b`](https://huggingface.co/openai/gpt-oss-20b) for the smaller model.

# Highlights

* **Permissive Apache 2.0 license:** Build freely without copyleft restrictions or patent risk—ideal for experimentation, customization, and commercial deployment.  
* **Configurable reasoning effort:** Easily adjust the reasoning effort (low, medium, high) based on your specific use case and latency needs.  
* **Full chain-of-thought:** Gain complete access to the model’s reasoning process, facilitating easier debugging and increased trust in outputs. It’s not intended to be shown to end users.  
* **Fine-tunable:** Fully customize models to your specific use case through parameter fine-tuning.
* **Agentic capabilities:** Use the models’ native capabilities for function calling, [web browsing](https://github.com/openai/gpt-oss/tree/main?tab=readme-ov-file#browser), [Python code execution](https://github.com/openai/gpt-oss/tree/main?tab=readme-ov-file#python), and Structured Outputs.
* **MXFP4 quantization:** The models were post-trained with MXFP4 quantization of the MoE weights, making `gpt-oss-120b` run on a single 80GB GPU (like NVIDIA H100 or AMD MI300X) and the `gpt-oss-20b` model run within 16GB of memory. All evals were performed with the same MXFP4 quantization.

---

# Inference examples

## Transformers

You can use `gpt-oss-120b` and `gpt-oss-20b` with Transformers. If you use the Transformers chat template, it will automatically apply the [harmony response format](https://github.com/openai/harmony). If you use `model.generate` directly, you need to apply the harmony format manually using the chat template or use our [openai-harmony](https://github.com/openai/harmony) package.

To get started, install the necessary dependencies to setup your environment:

```
pip install -U transformers kernels torch 
```

Once, setup you can proceed to run the model by running the snippet below:

```py
from transformers import pipeline
import torch

model_id = "openai/gpt-oss-120b"

pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype="auto",
    device_map="auto",
)

messages = [
    {"role": "user", "content": "Explain quantum mechanics clearly and concisely."},
]

outputs = pipe(
    messages,
    max_new_tokens=256,
)
print(outputs[0]["generated_text"][-1])
```

Alternatively, you can run the model via [`Transformers Serve`](https://huggingface.co/docs/transformers/main/serving) to spin up a OpenAI-compatible webserver:

```
transformers serve
transformers chat localhost:8000 --model-name-or-path openai/gpt-oss-120b
```

[Learn more about how to use gpt-oss with Transformers.](https://cookbook.openai.com/articles/gpt-oss/run-transformers)

## vLLM

vLLM recommends using [uv](https://docs.astral.sh/uv/) for Python dependency management. You can use vLLM to spin up an OpenAI-compatible webserver. The following command will automatically download the model and start the server.

```bash
uv pip install --pre vllm==0.10.1+gptoss \
    --extra-index-url https://wheels.vllm.ai/gpt-oss/ \
    --extra-index-url https://download.pytorch.org/whl/nightly/cu128 \
    --index-strategy unsafe-best-match

vllm serve openai/gpt-oss-120b
```

[Learn more about how to use gpt-oss with vLLM.](https://cookbook.openai.com/articles/gpt-oss/run-vllm)

## PyTorch / Triton

To learn about how to use this model with PyTorch and Triton, check out our [reference implementations in the gpt-oss repository](https://github.com/openai/gpt-oss?tab=readme-ov-file#reference-pytorch-implementation).

## Ollama

If you are trying to run gpt-oss on consumer hardware, you can use Ollama by running the following commands after [installing Ollama](https://ollama.com/download).

```bash
# gpt-oss-120b
ollama pull gpt-oss:120b
ollama run gpt-oss:120b
```

[Learn more about how to use gpt-oss with Ollama.](https://cookbook.openai.com/articles/gpt-oss/run-locally-ollama)

#### LM Studio

If you are using [LM Studio](https://lmstudio.ai/) you can use the following commands to download.

```bash
# gpt-oss-120b
lms get openai/gpt-oss-120b
```

Check out our [awesome list](https://github.com/openai/gpt-oss/blob/main/awesome-gpt-oss.md) for a broader collection of gpt-oss resources and inference partners.

---

# Download the model

You can download the model weights from the [Hugging Face Hub](https://huggingface.co/collections/openai/gpt-oss-68911959590a1634ba11c7a4) directly from Hugging Face CLI:

```shell
# gpt-oss-120b
huggingface-cli download openai/gpt-oss-120b --include "original/*" --local-dir gpt-oss-120b/
pip install gpt-oss
python -m gpt_oss.chat model/
```

# Reasoning levels

You can adjust the reasoning level that suits your task across three levels:

* **Low:** Fast responses for general dialogue.  
* **Medium:** Balanced speed and detail.  
* **High:** Deep and detailed analysis.

The reasoning level can be set in the system prompts, e.g., "Reasoning: high".

# Tool use

The gpt-oss models are excellent for:
* Web browsing (using built-in browsing tools)
* Function calling with defined schemas
* Agentic operations like browser tasks

# Fine-tuning

Both gpt-oss models can be fine-tuned for a variety of specialized use cases.

This larger model `gpt-oss-120b` can be fine-tuned on a single H100 node, whereas the smaller [`gpt-oss-20b`](https://huggingface.co/openai/gpt-oss-20b) can even be fine-tuned on consumer hardware.

# Citation

```bibtex
@misc{openai2025gptoss120bgptoss20bmodel,
      title={gpt-oss-120b & gpt-oss-20b Model Card}, 
      author={OpenAI},
      year={2025},
      eprint={2508.10925},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2508.10925}, 
}
```

---
