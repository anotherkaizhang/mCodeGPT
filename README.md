# mCodeGPT: Automating Cancer Clinical Data Standardization with Large Language Models

[![License](https://img.shields.io/badge/License-BSD-blue.svg)](LICENSE)

## Overview

The rapid accumulation of clinical and research data in oncology presents both an opportunity and a challenge for healthcare researchers. In this paper, we introduce mCodeGPT, a state-of-the-art Python package that seamlessly integrates the capabilities of large language models (LLMs) and the Minimal Common Oncology Data Elements (mCODE) initiative. The primary function of mCodeGPT is to automate the standardization process of cancer clinical notes, thereby enhancing efficiency and reliability.

## Features

- Automatically extracts ontology named entities and quantitative information.
- Zero-shot entity relationship extraction.
- Replaces the traditional cascade of NLP techniques for information extraction.
- Versatile and applicable to a broad range of domains beyond oncology.

## Prompt Generation Methods

To address the challenges posed by the comprehensive mCODE ontology and token limitations, we've developed three innovative prompt generation methods:

### Root-to-Leaf Streamliner (RLS)

Given the complex hierarchical structure of extensive ontology maps, directly parsing these into prompts for models such as GPT-3.5 can be challenging due to inherent token limitations. RLS strategically harmonizes information from the root node to each leaf node, synthesizing the complete hierarchical information into the leaf node's prompt. This approach constrains the prompts to fit within the token limits of advanced language models while maintaining an essential hierarchical context for precise information extraction.

### Breadth-First Ontology Pruner (BFOP)

BFOP is a level-wise parsing strategy similar to the breadth-first search algorithm for hierarchical ontology structures. It starts with entities on the first level and dynamically prunes branches of the ontology tree based on real-time feedback. If a particular named entity is absent in the patient's record, its associated child entities are skipped, optimizing the extraction process in a hierarchical manner and ensuring that the prompt remains concise.

### Two-Phase Ontology Parser (2POP)

Recognizing the challenges of extracting detailed information from large and complex ontologies, 2POP is a two-phase parsing approach. In the initial phase, it generates binary queries to ascertain the presence or absence of each named entity within the patient notes. In the second phase, it narrows down the queries to seek details only for those entities confirmed as present, enhancing precision in information extraction.

## Installation

To get started with mCodeGPT, you can install it using pip:

## **Usage**:
```
e.g. use GPT-3.5 with method RLS:
>> python main.py -i './examples/input_txt.txt' -k  '<YOUR OPENAI AZURE API KEY>' -b '<YOUR OPENAI AZURE API BASE>' -v '2023-05-15' -d 'mcodegpt_gpt_35' -m 'RLS' -o filename

e.g. use GPT-4 with method 2POP:
>> python main.py -i './examples/input_txt.txt' -k  '<YOUR OPENAI AZURE API KEY>' -b '<YOUR OPENAI AZURE API BASE>' -v '2023-05-15' -d 'mcodegpt_gpt_4' -m '2POP' -o filename
```

## License

This project is licensed under the BSD License (2-Clause and 3-Clause): - see the [![License](https://img.shields.io/badge/License-BSD-blue.svg)](LICENSE) file for details.

## Acknowledgments

mCodeGPT project is partially supported by NCI U01CA274576, CPRIT RR180012, and UTHealth

## Support

If you have any questions or encounter issues, please feel free to [create an issue](https://github.com/anotherkaizhang/mCodeGPT/issues).

## Contributing

Contributions are welcome! Please see our [Contribution Guidelines](CONTRIBUTING.md) for more information.

## Authors

- [Kai Zhang](https://github.com/anotherkaizhang)
- [Xiaoqian Jiang](https://github.com/x1jiang)

## Citation

If you use mCodeGPT in your research, please cite our paper (if available).

